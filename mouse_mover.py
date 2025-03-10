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
from PIL import Image, ImageDraw

## Failsafe -- prevent script from stopping once mouse moves to screen corner
pyautogui.FAILSAFE = False

CONFIG_FILE = "caff2.ini"
global last_action_time
last_action_time = None
global stop_flag
stop_flag = False


def create_icon_image(color="blue", size=64):
    """Create an icon image for the system tray"""
    try:
        image = Image.new("RGB", (size, size), color="white")
        dc = ImageDraw.Draw(image)
        dc.rectangle([(0, 0), (size, size)], fill=color)
        dc.ellipse(
            [(size // 4, size // 4), (3 * size // 4, 3 * size // 4)], fill="white"
        )
        return image
    except Exception as e:
        print(f"Error creating icon image: {e}")
        # Return a simple default image
        return Image.new("RGB", (16, 16), color=color)


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
        print(f"Error during mouse movement: {e}")
        return current_x, current_y  # Return original position in case of error


def log_action(action_deets):
    """Log an action to the log file"""
    try:
        with open("mouse_moving_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()}: {action_deets}\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")


def background_task(minutes):
    """The main task that runs in the background"""
    global last_action_time
    global stop_flag

    print(f"Background task started - moving mouse every {minutes} minutes")

    try:
        while not stop_flag:
            # Wait for specified minutes, checking stop flag every second
            for _ in range(minutes * 60):
                if stop_flag:
                    break
                time.sleep(1)

            if not stop_flag:
                x, y = random_mouse_move()
                action_details = f"Mouse was moved to ({x:.2f}, {y:.2f})"
                log_action(action_details)
                print(f"Action performed at {datetime.now()}. {action_details}")

    except Exception as e:
        error_msg = f"Error in background task: {str(e)}"
        log_action(error_msg)
        print(error_msg)
        traceback.print_exc()
    finally:
        print("Background task ended")


def key_monitor():
    """Monitor for ESC key press to exit the program"""
    global stop_flag
    print("Press ESC to exit")

    try:
        while not stop_flag:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b"\x1b":  # ESC key
                    print("ESC pressed, exiting...")
                    stop_flag = True
            time.sleep(0.1)
    except Exception as e:
        print(f"Error in key monitor: {e}")
        stop_flag = True  # Trigger exit on error


def main():
    """Main function"""
    global stop_flag

    try:
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

        print(f"Mouse mover will move every {minutes} minutes")

        # Start the background task
        bg_thread = threading.Thread(
            target=background_task, args=(minutes,), daemon=True
        )
        bg_thread.start()

        # Start the key monitor
        key_thread = threading.Thread(target=key_monitor, daemon=True)
        key_thread.start()

        # Keep the main thread running until stop flag is set
        try:
            while not stop_flag:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            stop_flag = True

    except Exception as e:
        print(f"Error in main function: {e}")
        traceback.print_exc()
    finally:
        print("Exiting Mouse Mover")
        # Ensure we exit even if threads are still running
        os._exit(0)


if __name__ == "__main__":
    main()
