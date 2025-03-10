import pyautogui
import time
import sys
from datetime import datetime
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

## Failsafe -- prevent script from stopping once mouse moves to screen corner
pyautogui.FAILSAFE = False

CONFIG_FILE = "caff2.ini"
global last_action_time
last_action_time = None
global stop_flag
stop_flag = False
global systray_icon
systray_icon = None

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


def create_icon_image(color="blue", size=64):
    """Create an icon image for the system tray"""
    try:
        image = Image.new("RGB", (size, size), color="white")
        dc = ImageDraw.Draw(image)
        dc.rectangle([(0, 0), (size, size)], fill=color)
        dc.ellipse(
            [(size // 4, size // 4), (3 * size // 4, 3 * size // 4)], fill="white"
        )

        # Save to a temporary file
        icon_path = os.path.join(tempfile.gettempdir(), "mouse_mover_icon.ico")
        image.save(icon_path, format="ICO")
        return icon_path
    except Exception as e:
        print(f"Error creating icon image: {e}")
        return None  # Return None in case of error


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


def random_mouse_move():
    """Perform random mouse movements and return new position"""
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
        with open("mouse_moving_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()}: {action_deets}\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")


def get_tooltip_text(minutes):
    """Get tooltip text for system tray icon"""
    global last_action_time
    base_text = f"Caff2: every {minutes} minutes"

    if last_action_time is None:
        return base_text

    time_diff = datetime.now() - last_action_time
    minutes_diff = time_diff.total_seconds() // 60
    seconds_diff = int(time_diff.total_seconds() % 60)

    return f"{base_text} | Last action: {minutes_diff}m {seconds_diff}s ago"


def update_tooltip(minutes):
    """Update the tooltip periodically"""
    global stop_flag, systray_icon
    while not stop_flag:
        try:
            if systray_icon:
                tooltip = get_tooltip_text(minutes)
                systray_icon.update(hover_text=tooltip)
        except Exception as e:
            log_action(f"Error updating tooltip: {e}")
        time.sleep(1)


def background_task(minutes):
    """The main task that runs in the background"""
    global last_action_time
    global stop_flag

    log_action(f"Background task started - interval: {minutes} minutes")

    try:
        while not stop_flag:
            # Wait for specified minutes, checking stop flag every second
            for _ in range(minutes * 60):
                if stop_flag:
                    break
                time.sleep(1)

            if not stop_flag:
                x, y = random_mouse_move()
                action_details = f"Action performed at coordinates ({x:.2f}, {y:.2f})"
                log_action(action_details)
    except Exception as e:
        error_msg = f"Error in background task: {str(e)}"
        log_action(error_msg)
    finally:
        log_action("Background task ended")


def exit_app(systray):
    """Exit the application"""
    global stop_flag
    stop_flag = True
    log_action("Exiting application via system tray")
    os._exit(0)


def worker_process(minutes):
    """Function for the actual background worker process"""
    global stop_flag, systray_icon

    try:
        # Create icon for system tray
        icon_path = (
            create_icon_image() or "mouse_mover_icon.ico"
        )  # Default if creation fails

        # Create system tray icon with menu
        menu_options = (("Exit", None, exit_app),)
        tooltip = f"Caff2: every {minutes} minutes"

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
