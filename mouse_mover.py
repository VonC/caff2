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
from pystray import (
    Icon as SysTrayIcon,
    Menu as SysTrayMenu,
    MenuItem as SysTrayMenuItem,
)
from PIL import Image, ImageDraw
import tempfile

## Failsafe -- prevent script from stopping once mouse moves to screen corner
pyautogui.FAILSAFE = False

CONFIG_FILE = "caff2.ini"
global last_action_time
last_action_time = None
global icon
icon = None


def create_icon_image(color="blue", size=64):
    """Create an icon image for the system tray"""
    image = Image.new("RGB", (size, size), color="white")
    dc = ImageDraw.Draw(image)
    dc.rectangle([(0, 0), (size, size)], fill=color)

    # Draw mouse icon (simplified)
    dc.ellipse([(size // 4, size // 4), (3 * size // 4, 3 * size // 4)], fill="white")
    return image


def is_already_running():
    """Check if another instance of this script is already running"""
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
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return False


def read_config():
    """Read configuration from ini file"""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if "Settings" in config and "minutes" in config["Settings"]:
            return int(config["Settings"]["minutes"])
    return None


def write_config(minutes):
    """Write configuration to ini file"""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)

    if "Settings" not in config:
        config["Settings"] = {}

    config["Settings"]["minutes"] = str(minutes)

    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)


def get_minutes_from_args():
    """Get minutes from command line arguments"""
    if len(sys.argv) >= 2:
        try:
            minutes = int(sys.argv[1])
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


def random_mouse_move():
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


def get_status_text():
    """Get status text for the tray icon tooltip"""
    global last_action_time
    if last_action_time is None:
        return "Mouse mover running - no movements yet"

    time_since = datetime.now() - last_action_time
    minutes = time_since.seconds // 60
    seconds = time_since.seconds % 60

    return f"Last movement: {minutes}m {seconds}s ago"


def log_action(action_deets):
    with open("mouse_moving_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()}: {action_deets}\n")


def exit_action(icon):
    """Exit the application when selected from the tray menu"""
    icon.stop()
    os._exit(0)  # Force exit


def update_tooltip():
    """Update the tray icon tooltip with status information"""
    global icon
    while True:
        if icon:
            icon.title = get_status_text()
        time.sleep(1)


def background_task(minutes):
    """The main task that runs in the background"""
    global last_action_time

    try:
        while True:
            # Wait for specified minutes
            time.sleep(minutes * 60)

            # Perform mouse movement
            x, y = random_mouse_move()
            action_details = f"Mouse was moved to ({x:.2f}, {y:.2f})"
            log_action(action_details)

    except Exception as e:
        log_action(f"Error in background task: {str(e)}")


def main():
    # Check if already running and handle command-line arg
    arg_minutes = get_minutes_from_args()
    if arg_minutes is not None:
        write_config(arg_minutes)
        if is_already_running():
            print("Another instance is already running. Updated config and exiting.")
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

    # Create and configure the system tray icon
    image = create_icon_image()
    menu = SysTrayMenu(SysTrayMenuItem("Exit", exit_action))

    # Start the background task
    threading.Thread(target=background_task, args=(minutes,), daemon=True).start()

    # Start the tooltip updater
    threading.Thread(target=update_tooltip, daemon=True).start()

    # Run the system tray icon (this will block until the icon is stopped)
    global icon
    icon = SysTrayIcon(image, f"Mouse Mover (every {minutes} min)", menu)
    icon.run()


if __name__ == "__main__":
    main()
