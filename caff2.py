# Import essential modules first
import os
import sys
import ctypes

# Now we can check for worker process and hide the window immediately
if __name__ == "__main__" and "--caff2-worker" in sys.argv:
    # Hide console immediately using Windows API
    kernel32 = ctypes.WinDLL("kernel32")
    user32 = ctypes.WinDLL("user32")
    hwnd = kernel32.GetConsoleWindow()
    if hwnd:
        user32.ShowWindow(hwnd, 0)  # SW_HIDE

import pyautogui
import time
import sys
from datetime import datetime, timedelta
import random
import os
import threading
import psutil
import configparser
import traceback
import tempfile
import ctypes
import subprocess
from infi.systray import SysTrayIcon
from PIL import Image, ImageDraw
from enum import Enum

## Failsafe -- prevent script from stopping once mouse moves to screen corner
pyautogui.FAILSAFE = False

CONFIG_FILE = "caff2.ini"
global last_action_time
last_action_time = None
global stop_flag
stop_flag = False
global systray_icon
systray_icon = None


# App state management
class AppState(Enum):
    RUNNING_INDEFINITE = 1
    RUNNING_TIMED = 2
    PAUSED_INDEFINITE = 3
    PAUSED_TIMED = 4


global app_state
app_state = AppState.RUNNING_INDEFINITE
global state_end_time
state_end_time = None
global refresh_minutes
refresh_minutes = 3  # Default value

# For hiding console window
kernel32 = ctypes.WinDLL("kernel32")
user32 = ctypes.WinDLL("user32")
SW_HIDE = 0


def hide_console():
    """Hide the console window"""
    try:
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            user32.ShowWindow(hwnd, SW_HIDE)
    except Exception as e:
        print(f"Error hiding console: {e}")


def create_icon_image():
    """Create an icon image for the system tray based on current state"""
    global app_state
    size = 64

    try:
        image = Image.new("RGB", (size, size), color="white")
        dc = ImageDraw.Draw(image)

        # Set colors based on state
        if app_state == AppState.RUNNING_INDEFINITE:
            square_color = "blue"
            circle_color = "white"
            outline_color = None  # No outline
        elif app_state == AppState.RUNNING_TIMED:
            square_color = "blue"
            circle_color = "yellow"
            outline_color = "red"  # Red outline for better contrast
        elif app_state == AppState.PAUSED_INDEFINITE:
            square_color = "red"
            circle_color = "yellow"
            outline_color = None
        elif app_state == AppState.PAUSED_TIMED:
            square_color = "yellow"
            circle_color = "red"
            outline_color = None
        else:
            square_color = "gray"
            circle_color = "white"
            outline_color = None

        # Draw square background
        dc.rectangle([(0, 0), (size, size)], fill=square_color)

        # Calculate circle dimensions
        circle_outer = [(size // 4, size // 4), (3 * size // 4, 3 * size // 4)]

        # Draw outline if needed (slightly larger than the main circle)
        if outline_color:
            # Make outline slightly larger than the inner circle
            outline_padding = 3
            outline_outer = [
                (
                    circle_outer[0][0] - outline_padding,
                    circle_outer[0][1] - outline_padding,
                ),
                (
                    circle_outer[1][0] + outline_padding,
                    circle_outer[1][1] + outline_padding,
                ),
            ]
            dc.ellipse(outline_outer, fill=outline_color)

        # Draw main circle
        dc.ellipse(circle_outer, fill=circle_color)

        # Save to a temporary file
        icon_path = os.path.join(
            tempfile.gettempdir(), f"caff2_icon_{app_state.name}.ico"
        )
        image.save(icon_path, format="ICO")
        return icon_path
    except Exception as e:
        print(f"Error creating icon image: {e}")
        # Return a simple default image
        return None


def is_already_running():
    """Check if another instance of this script is already running"""
    try:
        # Use the script directory for lock file instead of temp directory
        lock_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "caff2.lock"
        )

        debug_log(f"Checking lock file: {lock_file}", "caff2_lock_debug.log")

        # Check if lock file exists
        if os.path.exists(lock_file):
            debug_log("Lock file exists", "caff2_lock_debug.log")
            # Read the PID from the lock file
            try:
                with open(lock_file, "r") as f:
                    pid_str = f.read().strip()
                    debug_log(f"Lock file content: {pid_str}", "caff2_lock_debug.log")
                    pid = int(pid_str)

                # Check if process with this PID is still running
                try:
                    # If process exists and is a Python process, consider app running
                    process = psutil.Process(pid)
                    debug_log(
                        f"Process exists. Name={process.name()}", "caff2_lock_debug.log"
                    )
                    if process.name() in ["python.exe", "python"]:
                        debug_log(
                            "Process is Python. App is already running.",
                            "caff2_lock_debug.log",
                        )
                        return True
                    else:
                        debug_log(
                            "Process is not Python. Removing stale lock.",
                            "caff2_lock_debug.log",
                        )
                        os.remove(lock_file)
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    # Process no longer exists, lock file is stale
                    debug_log(
                        f"Process doesn't exist: {e}. Removing stale lock.",
                        "caff2_lock_debug.log",
                    )
                    os.remove(lock_file)
            except Exception as e:
                # Lock file exists but is invalid, remove it
                debug_log(f"Invalid lock file: {e}. Removing.", "caff2_lock_debug.log")
                os.remove(lock_file)

        # Count worker processes even if no lock file exists
        current_pid = os.getpid()
        current_process_name = os.path.basename(__file__)
        debug_log(
            f"Current process: PID={current_pid}, Name={current_process_name}",
            "caff2_lock_debug.log",
        )

        # Count worker processes
        worker_processes = []

        for process in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if process.info["pid"] != current_pid and process.info["name"] in [
                    "python.exe",
                    "python",
                ]:
                    cmdline = process.info["cmdline"]
                    if cmdline and any(current_process_name in arg for arg in cmdline):
                        # This is a process running our script
                        is_worker = any("--caff2-worker" in arg for arg in cmdline)
                        debug_log(
                            f"Found process: PID={process.info['pid']}, worker={is_worker}",
                            "caff2_lock_debug.log",
                        )

                        if is_worker:
                            worker_processes.append(process.info["pid"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        debug_log(
            f"Found {len(worker_processes)} worker processes: {worker_processes}",
            "caff2_lock_debug.log",
        )

        # If there are already worker processes running, the app is already running
        if len(worker_processes) > 0:
            debug_log(
                "Application is already running (worker processes found)",
                "caff2_lock_debug.log",
            )
            return True

        # If we get here, no instances are running
        # The worker process will create its own lock file later
        return False

    except Exception as e:
        print(f"Error checking for running instances: {e}")
        debug_log(f"Error checking for running instances: {e}", "caff2_lock_debug.log")
        traceback.print_exc()
        return False


def read_config():
    """Read configuration from ini file"""
    try:
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
            if "Settings" in config and "minutes" in config["Settings"]:
                return int(config["Settings"]["minutes"])
        return None
    except Exception as e:
        print(f"Error reading config: {e}")
        return None


def write_config(minutes):
    """Write configuration to ini file"""
    try:
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)

        if "Settings" not in config:
            config["Settings"] = {}

        config["Settings"]["minutes"] = str(minutes)

        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)
    except Exception as e:
        print(f"Error writing config: {e}")


def get_minutes_from_args():
    """Get minutes from command line arguments"""
    for i, arg in enumerate(sys.argv):
        if arg == "--caff2-worker":
            continue

        if i >= 1:  # Skip script name
            try:
                minutes = int(arg)
                if minutes >= 1:
                    return minutes
            except ValueError:
                pass
    return None


def min_num():
    while True:
        try:
            numMin = int(input("Enter number of minutes to wait between actions: "))
            if numMin < 1:
                print("Has to be more than 1")
                raise ValueError
            print(f"chosen duration: {numMin}")
            return numMin
        except ValueError:
            print("Please enter an integer (e.g. not a string)")
        except KeyboardInterrupt:
            print("\nExiting due to user interrupt")
            sys.exit(0)


def format_time_duration(seconds):
    """Format time duration in a human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    elif seconds < 86400:  # Less than a day
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"


def format_datetime(dt):
    """Format datetime in a minimal way"""
    now = datetime.now()

    # Same day
    if dt.date() == now.date():
        return dt.strftime("%H:%M:%S")

    # Same month and year
    if dt.month == now.month and dt.year == now.year:
        return dt.strftime("%d %H:%M:%S")

    # Same year
    if dt.year == now.year:
        return dt.strftime("%d/%m %H:%M:%S")

    # Different year
    return dt.strftime("%d/%m/%y %H:%M:%S")


def random_mouse_move():
    """Perform random mouse movements and return new position"""
    global app_state

    # Don't move if paused
    if app_state == AppState.PAUSED_INDEFINITE or app_state == AppState.PAUSED_TIMED:
        return None, None

    try:
        # Get current mouse position
        current_x, current_y = pyautogui.position()

        # Make random small movements relative to current position
        offset_x = random.uniform(-50, 50)
        offset_y = random.uniform(-50, 50)

        pyautogui.moveRel(offset_x, offset_y)
        new_x, new_y = pyautogui.position()

        # Return to a position close to the original
        pyautogui.moveTo(current_x + 1, current_y + 1)

        # Press shift a few times
        for _ in range(3):
            pyautogui.press("shift")

        global last_action_time
        last_action_time = datetime.now()

        return new_x, new_y
    except Exception as e:
        log_action(f"Error during action: {e}")
        return current_x, current_y  # Return original position in case of error


def resume_callback(systray):
    """Callback for resume menu item"""
    global app_state

    # Only do something if we're in a paused state
    if app_state == AppState.PAUSED_INDEFINITE or app_state == AppState.PAUSED_TIMED:
        set_app_state(AppState.RUNNING_INDEFINITE)
        # Trigger an immediate action to confirm it's working
        threading.Thread(target=perform_immediate_action, daemon=True).start()


def perform_immediate_action():
    """Perform an immediate action to confirm resume is working"""
    time.sleep(0.5)  # Brief delay to allow state change to complete
    x, y = random_mouse_move()
    if x is not None and y is not None:
        action_details = f"Resume action performed at coordinates ({x:.2f}, {y:.2f})"
        log_action(action_details)


def log_action(action_deets):
    """Log an action to the log file"""
    try:
        with open("caff2_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()}: {action_deets}\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")


def get_tooltip_text(minutes):
    """Get tooltip text for system tray icon"""
    global app_state, state_end_time, last_action_time

    lines = []

    # Line 1: Frequency
    lines.append(f"Refresh: every {minutes} minutes")

    # Line 2: State
    state_text = "State: "
    if app_state == AppState.RUNNING_INDEFINITE:
        state_text += "Running"
    elif app_state == AppState.RUNNING_TIMED:
        state_text += "Running (timed)"
    elif app_state == AppState.PAUSED_INDEFINITE:
        state_text += "Paused"
    elif app_state == AppState.PAUSED_TIMED:
        state_text += "Paused (timed)"
    lines.append(state_text)

    # Line 3: End time if timed
    if state_end_time and (
        app_state == AppState.RUNNING_TIMED or app_state == AppState.PAUSED_TIMED
    ):
        time_left = (state_end_time - datetime.now()).total_seconds()
        if time_left > 0:
            duration_text = format_time_duration(int(time_left))
            end_time_text = format_datetime(state_end_time)
            lines.append(f"Duration: {duration_text} (until {end_time_text})")

    # Line 4: Last action time
    if last_action_time and (
        app_state == AppState.RUNNING_INDEFINITE or app_state == AppState.RUNNING_TIMED
    ):
        time_diff = datetime.now() - last_action_time
        minutes_diff = int(time_diff.total_seconds() // 60)
        seconds_diff = int(time_diff.total_seconds() % 60)
        lines.append(f"Last action: {minutes_diff}m {seconds_diff}s ago")

    return "\n".join(lines)


def update_tooltip(minutes):
    """Update the tooltip periodically"""
    global stop_flag, systray_icon, app_state, state_end_time

    while not stop_flag:
        try:
            # Update app state based on timer
            if state_end_time:
                if datetime.now() >= state_end_time:
                    if app_state == AppState.RUNNING_TIMED:
                        set_app_state(AppState.PAUSED_INDEFINITE)
                        log_action("Timed run completed, switching to paused state")
                    elif app_state == AppState.PAUSED_TIMED:
                        set_app_state(AppState.RUNNING_INDEFINITE)
                        log_action("Timed pause completed, resuming normal operation")

            # Update tooltip text
            if systray_icon:
                tooltip = get_tooltip_text(minutes)
                systray_icon.update(hover_text=tooltip)

        except Exception as e:
            log_action(f"Error updating tooltip: {e}")
        time.sleep(1)


def set_app_state(new_state, duration_minutes=None):
    """Set application state and update icon"""
    global app_state, state_end_time, systray_icon

    # Record previous state for logging
    previous_state = app_state

    # Set new state
    app_state = new_state

    # Set end time if duration provided
    if duration_minutes:
        state_end_time = datetime.now() + timedelta(minutes=duration_minutes)
    else:
        state_end_time = None

    # Update icon
    if systray_icon:
        try:
            new_icon = create_icon_image()
            if new_icon:
                systray_icon.update(icon=new_icon)
                log_action(
                    f"Updated icon from {previous_state.name} to {app_state.name}"
                )
        except Exception as e:
            log_action(f"Error updating icon: {e}")

    state_change_msg = f"State changed from {previous_state.name} to {app_state.name}"
    if duration_minutes:
        state_change_msg += (
            f" for {duration_minutes} minutes (until {format_datetime(state_end_time)})"
        )

    log_action(state_change_msg)


def background_task(minutes):
    """The main task that runs in the background"""
    global last_action_time, stop_flag, app_state

    log_action(f"Background task started - interval: {minutes} minutes")

    try:
        last_check_time = datetime.now()

        while not stop_flag:
            current_time = datetime.now()
            elapsed_seconds = (current_time - last_check_time).total_seconds()

            # Only wait for the remaining time in the current interval
            if elapsed_seconds < minutes * 60:
                # Wait for a shorter time and check stop_flag more frequently
                time.sleep(
                    0.5
                )  # Sleep for half a second at a time instead of up to a minute
                continue

            # Time for an action, reset the timer
            last_check_time = current_time

            if not stop_flag:
                # Only perform action if not paused
                if (
                    app_state == AppState.RUNNING_INDEFINITE
                    or app_state == AppState.RUNNING_TIMED
                ):
                    x, y = random_mouse_move()
                    if x is not None and y is not None:
                        action_details = (
                            f"Action performed at coordinates ({x:.2f}, {y:.2f})"
                        )
                        log_action(action_details)
                else:
                    log_action(f"Action skipped - currently in {app_state.name} state")
    except Exception as e:
        error_msg = f"Error in background task: {str(e)}"
        log_action(error_msg)
    finally:
        log_action("Background task ended")


def pause_callback(systray, duration=None):
    """Callback for pause menu items"""
    if duration is None:
        # Custom duration
        try:
            from tkinter import Tk, simpledialog

            root = Tk()
            root.withdraw()
            duration = simpledialog.askinteger(
                "Custom Duration",
                "Enter pause duration in minutes (0 for indefinite):",
                minvalue=0,
                maxvalue=10080,
            )  # Max 7 days
            root.destroy()

            if duration is None:  # User cancelled
                return
        except Exception as e:
            log_action(f"Error in custom duration dialog: {e}")
            return

    if duration == 0:
        set_app_state(AppState.PAUSED_INDEFINITE)
    else:
        set_app_state(AppState.PAUSED_TIMED, duration)


def run_callback(systray, duration=None):
    """Callback for run menu items"""
    if duration is None:
        # Custom duration
        try:
            from tkinter import Tk, simpledialog

            root = Tk()
            root.withdraw()
            duration = simpledialog.askinteger(
                "Custom Duration",
                "Enter run duration in minutes (0 for indefinite):",
                minvalue=0,
                maxvalue=10080,
            )  # Max 7 days
            root.destroy()

            if duration is None:  # User cancelled
                return
        except Exception as e:
            log_action(f"Error in custom duration dialog: {e}")
            return

    if duration == 0:
        set_app_state(AppState.RUNNING_INDEFINITE)
    else:
        set_app_state(AppState.RUNNING_TIMED, duration)


def resume_callback(systray):
    """Callback for resume menu item"""
    set_app_state(AppState.RUNNING_INDEFINITE)


def exit_app(systray):
    """Exit the application"""
    global stop_flag
    stop_flag = True
    log_action("Exiting application via system tray")

    # Remove lock file - now using script directory
    try:
        lock_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "caff2.lock"
        )
        debug_log(f"Removing lock file: {lock_file}", "caff2_exit.log")
        if os.path.exists(lock_file):
            os.remove(lock_file)
            debug_log("Lock file removed successfully", "caff2_exit.log")
    except Exception as e:
        debug_log(f"Error removing lock file: {e}", "caff2_exit.log")

    os._exit(0)


def create_menu_options():
    """Create menu options for the system tray icon"""
    pause_menu = (
        ("5 minutes", None, lambda systray: pause_callback(systray, 5)),
        ("10 minutes", None, lambda systray: pause_callback(systray, 10)),
        ("15 minutes", None, lambda systray: pause_callback(systray, 15)),
        ("30 minutes", None, lambda systray: pause_callback(systray, 30)),
        ("45 minutes", None, lambda systray: pause_callback(systray, 45)),
        ("1 hour", None, lambda systray: pause_callback(systray, 60)),
        ("Custom...", None, lambda systray: pause_callback(systray, None)),
        ("Indefinite", None, lambda systray: pause_callback(systray, 0)),
    )

    run_menu = (
        ("5 minutes", None, lambda systray: run_callback(systray, 5)),
        ("10 minutes", None, lambda systray: run_callback(systray, 10)),
        ("15 minutes", None, lambda systray: run_callback(systray, 15)),
        ("30 minutes", None, lambda systray: run_callback(systray, 30)),
        ("45 minutes", None, lambda systray: run_callback(systray, 45)),
        ("1 hour", None, lambda systray: run_callback(systray, 60)),
        ("Custom...", None, lambda systray: run_callback(systray, None)),
        ("Indefinite", None, lambda systray: run_callback(systray, 0)),
    )

    menu_options = (
        ("Pause", None, pause_menu),
        ("Run", None, run_menu),
        ("Resume", None, resume_callback),
        ("Exit", None, exit_app),
    )

    return menu_options


def debug_log(message, filename="caff2_debug.log"):
    """Write to a debug log file with the specified filename"""
    try:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(log_path, "a") as f:
            f.write(f"{datetime.now()}: {message}\n")
    except Exception as e:
        # Use Windows temp file as fallback
        try:
            temp_log = os.path.join(tempfile.gettempdir(), "caff2_fallback_log.txt")
            with open(temp_log, "a") as f:
                f.write(f"{datetime.now()}: ERROR writing to {filename}: {e}\n")
                f.write(f"{datetime.now()}: {message}\n")
        except:
            pass  # If even this fails, we can't do much more


def worker_process(minutes):
    """Function for the actual background worker process"""
    global stop_flag, systray_icon, refresh_minutes

    debug_log("Worker process starting", "caff2_worker.log")
    debug_log(f"Process ID: {os.getpid()}", "caff2_worker.log")
    debug_log(f"Minutes setting: {minutes}", "caff2_worker.log")

    # Create or update the lock file with the worker's PID
    lock_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caff2.lock")
    try:
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))
        debug_log(
            f"Worker process updated lock file with its PID: {os.getpid()}",
            "caff2_worker.log",
        )
    except Exception as e:
        debug_log(f"Error updating lock file: {e}", "caff2_worker.log")

    refresh_minutes = minutes

    try:
        # Set initial state
        set_app_state(AppState.RUNNING_INDEFINITE)
        debug_log("Set initial state to RUNNING_INDEFINITE", "caff2_worker.log")

        # Create icon for system tray
        icon_path = create_icon_image()
        if not icon_path:
            debug_log("Failed to create custom icon, using default", "caff2_worker.log")
            icon_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "caff2_icon.ico"
            )
            if not os.path.exists(icon_path):
                # Create a simple icon if needed
                debug_log("Creating simple default icon", "caff2_worker.log")
                from PIL import Image

                img = Image.new("RGB", (64, 64), color="blue")
                icon_path = os.path.join(tempfile.gettempdir(), "caff2_default.ico")
                img.save(icon_path, format="ICO")

        debug_log(f"Using icon at: {icon_path}", "caff2_worker.log")

        # Create system tray icon with menu
        debug_log("Creating menu options", "caff2_worker.log")
        menu_options = create_menu_options()
        tooltip = get_tooltip_text(minutes)

        debug_log("Initializing system tray icon")
        # Create the system tray icon with exception handling
        try:
            systray_icon = SysTrayIcon(icon_path, tooltip, menu_options)
            debug_log("System tray icon created successfully", "caff2_worker.log")
        except Exception as e:
            debug_log(f"Error creating system tray icon: {e}", "caff2_worker.log")
            traceback.print_exc()
            raise  # Re-raise to be caught by outer try/except

        # Start the background task in a separate thread
        debug_log("Starting background task thread", "caff2_worker.log")
        bg_thread = threading.Thread(
            target=background_task, args=(minutes,), daemon=True
        )
        bg_thread.start()

        # Start tooltip updater thread
        debug_log("Starting tooltip updater thread", "caff2_worker.log")
        tooltip_thread = threading.Thread(
            target=update_tooltip, args=(minutes,), daemon=True
        )
        tooltip_thread.start()

        # Hide console window
        debug_log("Hiding console window", "caff2_worker.log")
        hide_console()

        # Run the system tray (this will block until exit)
        debug_log("Starting system tray (blocking call)", "caff2_worker.log")
        systray_icon.start()
        debug_log("System tray exited normally")

    except Exception as e:
        error_msg = f"Error in worker process: {str(e)}"
        debug_log(error_msg, "caff2_worker.log")
        log_action(error_msg)
        traceback.print_exc()

        # Try to show a visible error
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(
                0, f"Caff2 Error: {str(e)}", "Caff2 Error", 0
            )
        except:
            pass


def main():
    """Main function"""
    try:
        # Always check for running instances first
        if "--caff2-worker" not in sys.argv:  # Only do this in the main process
            print("Checking for existing instances...")
            if is_already_running():
                print("Another instance is already running. Exiting.")
                sys.exit(2)

        # This block handles worker process execution
        if "--caff2-worker" in sys.argv:
            # Worker process code
            minutes = read_config()
            if not minutes:
                debug_log("No minutes configuration found", "caff2_main.log")
                log_action("No minutes configuration found for worker process")
                return
            worker_process(minutes)
            return

        # Main process continues here
        debug_log("Running as main process", "caff2_main.log")

        # Handle minutes configuration
        arg_minutes = get_minutes_from_args()
        if arg_minutes is not None:
            write_config(arg_minutes)

        minutes = arg_minutes if arg_minutes is not None else read_config()
        if minutes is None:
            minutes = min_num()
            write_config(minutes)

        # Launch the worker process with multiple invisibility techniques
        script_path = os.path.abspath(sys.argv[0])
        debug_log(f"Launching worker process: {script_path}", "caff2_main.log")

        # Create startupinfo to hide window
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE

        # Use BOTH startupinfo AND creationflags for maximum invisibility
        worker = subprocess.Popen(
            [sys.executable, script_path, "--caff2-worker"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
            close_fds=True,
            start_new_session=True,
        )

        debug_log(f"Worker process started with PID: {worker.pid}", "caff2_main.log")
        print(f"Caff2 started in background (every {minutes} minutes)")

        # Exit main process
        sys.exit(0)

    except Exception as e:
        print(f"Error starting Caff2: {e}")
        try:
            debug_log(f"Error in main: {e}", "caff2_main.log")
        except:
            pass
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
