# Caff2: Caffeine, but in Python, for Windows

## Additional features

- Allows clearer input from user for the number of minutes
- Uses threading to revert to default if value isn't entered in fast enough (e.g. if the user forgets to enter even after starting the program)
- Adds all actions into a txt file for analysis if required.
- Allows stopping mechanism via escape button and system tray icon
- Runs discreetly in the background with no visible console window.
- Employs a robust single-instance mechanism using a lock file to prevent multiple executions.
- Features improved responsiveness to exit commands, particularly via system tray, due to more frequent checks.
- Includes comprehensive debug logging for easier troubleshooting.
- Provides convenient new batch scripts for simpler setup and execution with colored output.

## Evolutions

The recent changes to the `caff2.py` script and the introduction of new utility batch files (`run.bat`, `senv.bat`) along with a `batcolors` submodule, and corresponding updates to `.gitignore` and `README.md`, are driven by several key motivations:

1. **Enhanced User Experience and Discretion (Invisibility):**

   - The primary goal was to transform Caff2 from a potentially console-visible script into a truly discreet, background application. Users want a "caffeine" program to run unnoticed.
   - This is achieved by:
     - Implementing **multiple console hiding techniques** when the `caff2.py` worker process is launched (`subprocess.CREATE_NO_WINDOW`, `startupinfo`, redirecting stdout/stderr/stdin to `DEVNULL`, `start_new_session`).
     - Using `ctypes` and Windows API calls (`ShowWindow(hwnd, 0)`) directly within the worker process to ensure the console is hidden immediately upon startup, even before the `subprocess` flags fully take effect.

2. **Robust Single-Instance Management:**

   - Previous methods for checking if an instance was already running were less reliable.
   - The updated `is_already_running()` function now uses a **dedicated lock file (`caff2.lock`)**. This is a more robust and explicit mechanism to ensure only one instance of Caff2 is active at a time, preventing conflicts or unintended multiple actions.
   - The lock file also includes logic to **clean up stale locks** (e.g., if a previous instance crashed).
   - The `exit_app` function now explicitly removes the lock file upon clean shutdown.

3. **Improved Responsiveness and Control:**

   - The `background_task` now sleeps for shorter intervals (`0.5` seconds instead of up to `1` minute) when waiting during an activity cycle.
   - This change, though minor, makes the application **more responsive** to the `stop_flag`, meaning the application will exit much faster when the user triggers an exit via the system tray icon, providing a smoother user experience.

4. **Enhanced Debugging and Troubleshooting:**

   - A new `debug_log()` function has been introduced, widely used throughout `caff2.py`.
   - This provides a **much-needed logging mechanism** for a background application that provides little visual feedback. In case of issues, the logs can help diagnose problems without needing to run the script in a visible console.
   - The `.gitignore` was updated to exclude these new log files (`*.log`), preventing them from being accidentally committed.

5. **Simplified Installation and Execution (Batch Scripts):**
   - The new `run.bat` and `senv.bat` files aim to **streamline the setup and execution process**, especially for Windows users.
   - `senv.bat` helps in **setting up the Python environment**, and potentially a virtual environment, in a standardized way.
   - `run.bat` provides a simple entry point to start the `caff2.py` application.
   - The integration of the `batcolors` submodule allows for **colored console output** in these batch scripts, making messages (tasks, successes, errors) clearer and more visually appealing for the user.
   - `run.bat` also specifically handles the "another instance running" error message (errorlevel 2) from `caff2.py` with a user-friendly message.

## Hard-Forked from [Stay-Awake](https://github.com/ianian-dot/Stay-Awake-2)

<sup>(Jordan - 2017, Muhammed Abdelkader - 2022, Ian Petrus Tan - 2024)</sup>

Initially, a small python script to move your mouse, press the shift key, and keep your
PC awake when you're away

Uses command line arguments to set the number of minutes between movements and
requires Python3 or higher.  
 Default timer is 3 minutes, but can be 1 or more.

## Dependencies

This software is using PyAutoGui <https://github.com/asweigart/pyautogui> as the driver behind the movement.

## Optional- Create Virtual Env Step

``` bash
python3 -m venv ./caff2 ```
pip install -r requirements.txt ```
```
