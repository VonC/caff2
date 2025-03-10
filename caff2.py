import pyautogui
import time
import sys
from datetime import datetime, timedelta
import random
import os
import threading
import msvcrt
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
        elif app_state == AppState.RUNNING_TIMED:
            square_color = "blue"
            circle_color = "yellow"
        elif app_state == AppState.PAUSED_INDEFINITE:
            square_color = "red"
            circle_color = "yellow"
        elif app_state == AppState.PAUSED_TIMED:
            square_color = "yellow"
            circle_color = "red"
        else:
            square_color = "gray"
            circle_color = "white"

        # Draw square background
        dc.rectangle([(0, 0), (size, size)], fill=square_color)

        # Draw circle
        dc.ellipse(
            [(size // 4, size // 4), (3 * size // 4, 3 * size // 4)], fill=circle_color
        )

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
        current_process = psutil.Process(os.getpid())
        current_process_name = os.path.basename(__file__)

        for process in psutil.process_iter(["pid", "name"]):
            if (
                process.info["pid"] != current_process.pid
                and process.info["name"] == "python.exe"
            ):
                try:
                    cmdline = process.cmdline()
                    if len(cmdline) > 1 and current_process_name in cmdline[1]:
                        # Check if the argument list contains our special "background" flag
                        if "--caff2-worker" not in cmdline:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return False
    except Exception as e:
        print(f"Error checking for running instances: {e}")
        return False  # Assume no other instance is running in case of error


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
                log_action(f"Updated icon to {app_state.name}")
        except Exception as e:
            log_action(f"Error updating icon: {e}")

    log_action(
        f"State changed to {app_state.name}"
        + (f" for {duration_minutes} minutes" if duration_minutes else "")
    )


def background_task(minutes):
    """The main task that runs in the background"""
    global last_action_time, stop_flag, app_state

    log_action(f"Background task started - interval: {minutes} minutes")

    try:
        while not stop_flag:
            # Wait for specified minutes, checking stop flag every second
            for _ in range(minutes * 60):
                if stop_flag:
                    break
                time.sleep(1)

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


def worker_process(minutes):
    """Function for the actual background worker process"""
    global stop_flag, systray_icon, refresh_minutes

    refresh_minutes = minutes

    try:
        # Set initial state
        set_app_state(AppState.RUNNING_INDEFINITE)

        # Create icon for system tray
        icon_path = create_icon_image() or "caff2_icon.ico"

        # Create system tray icon with menu
        menu_options = create_menu_options()
        tooltip = get_tooltip_text(minutes)

        # Create the system tray icon
        systray_icon = SysTrayIcon(icon_path, tooltip, menu_options)

        # Start the background task in a separate thread
        bg_thread = threading.Thread(
            target=background_task, args=(minutes,), daemon=True
        )
        bg_thread.start()

        # Start tooltip updater thread
        tooltip_thread = threading.Thread(
            target=update_tooltip, args=(minutes,), daemon=True
        )
        tooltip_thread.start()

        # Hide console window
        hide_console()

        # Run the system tray (this will block until exit)
        systray_icon.start()

    except Exception as e:
        log_action(f"Error in worker process: {str(e)}")
        traceback.print_exc()


def main():
    """Main function"""
    try:
        # Check if this is the worker process
        if "--caff2-worker" in sys.argv:
            # This is the worker process, run the actual application
            minutes = read_config()
            if not minutes:
                log_action("No minutes configuration found for worker process")
                return
            worker_process(minutes)
            return

        # Check if already running and handle command-line arg
        arg_minutes = get_minutes_from_args()
        if arg_minutes is not None:
            write_config(arg_minutes)
            if is_already_running():
                print(
                    "Another instance is already running. Updated config and exiting."
                )
                return

        # Determine minutes to wait
        minutes = None

        # Priority: 1) Command line args, 2) Config file, 3) User input
        if arg_minutes is not None:
            minutes = arg_minutes
        else:
            minutes = read_config()
            if minutes is None:
                minutes = min_num()
                write_config(minutes)

        # Launch the worker process
        script_path = os.path.abspath(sys.argv[0])
        subprocess.Popen(
            [sys.executable, script_path, "--caff2-worker"],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        print(f"Caff2 started in background (every {minutes} minutes)")

    except Exception as e:
        print(f"Error starting Caff2: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
