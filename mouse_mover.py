import pyautogui  # for controlling mouse and keyboard
import time
import sys  # access command line arguments
from datetime import datetime
import random
import os
import threading
import msvcrt
import psutil  # for checking running processes
import configparser  # for handling ini file

## Failsafe -- prevent script from stopping once mouse moves to screen corner
pyautogui.FAILSAFE = False

CONFIG_FILE = "caff2.ini"


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


## Get durations from user:
def min_num():
    while True:
        try:
            numMin = int(input("Enter number of minutes to wait between actions: "))
            if numMin < 1:
                print("Has to be more than 1")
                raise ValueError  # has to be more than 1 min
            print(f"chosen duration: {numMin}")
            return numMin
        except ValueError:
            print("Please enter an integer (e.g. not a string)")


## Random mouse movement
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

    return new_x, new_y


## Logging actions onto text file:
def log_action(action_deets):
    with open("mouse_moving_log.txt", "a") as log_file:  # a for append mode
        log_file.write(f"{datetime.now()}: {action_deets}\n")


## Stopping the program
def stop_mechanism():
    global stop_thread  # global variable outside of the function (top level of script)
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch()
            if char == b"\x1b":  # this is for escape key
                print("\nStopping mousemover")
                stop_thread = True
                break
        time.sleep(0.5)


def main():
    global stop_thread
    stop_thread = False

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

    # Starting the stop mechanism in a separate thread
    stop_threading = threading.Thread(target=stop_mechanism)
    stop_threading.daemon = True  # Ensure thread terminates when main program exits
    stop_threading.start()

    # Record the start time
    start_time = datetime.now()

    try:
        print(
            f"Mouse mover running. Will move every {minutes} minutes. Press ESC to stop."
        )

        while not stop_thread:
            print(f"Waiting for {minutes} minutes...")

            # Wait for specified minutes, checking stop flag every second
            for _ in range(minutes * 60):
                if stop_thread:
                    break
                time.sleep(1)

            if not stop_thread:
                x, y = random_mouse_move()
                action_details = f"Mouse was moved to ({x:.2f}, {y:.2f})"
                log_action(action_details)
                print(f"Action logged at {datetime.now()}. Details: {action_details}")

    except KeyboardInterrupt:
        print("Program interrupted manually.")

    finally:
        # Calculate total runtime
        end_time = datetime.now()
        total_runtime = end_time - start_time
        print(f"Total runtime: {total_runtime}")

        # Ensure all threads are cleaned up before exiting
        stop_thread = True
        print("Program has been stopped.")


if __name__ == "__main__":
    main()
