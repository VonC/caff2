# Caff2: Caffeine, but in Python, for Windows

## Quick start

Install **Python 3.10 or newer for Windows**, including pip, and enable
**Add python.exe to PATH**. Download or clone this repository, open a terminal
in its folder, and run:

```bat
.\run.bat
```

The first run creates `.venv` and installs `requirements.txt`; it needs access
to a Python package index. Later runs reuse that environment. Global `senv`,
`switchpy`, Git, and the `batcolors` submodule are not needed to run Caff2.
Arguments are forwarded to the application, for example `run.bat 5` sets the
interval to five minutes. Use the tray menu to pause or exit.

To activate the environment for development in Command Prompt, run
`call .\senv.bat`. To use Python directly after setup:

```bat
.venv\Scripts\python.exe caff2.py 5
```

Alternatively, set up Python without either batch script:

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe caff2.py
```

Optional private package-index and certificate settings belong in the ignored
`senv.local.bat`. Existing `PIP_INDEX_URL`, `PIP_EXTRA_INDEX_URL`, and `PIP_CERT`
settings are respected; the corresponding `UV_*` settings are also supported.

## Maintainer commit protection

When a sibling `../llm-shared` checkout and private replacement rules are
available, `senv.bat` installs or verifies its composable `pre-commit` and
`commit-msg` hooks, using **llm-shared's own Python environment**. Existing
hooks are preserved. This integration is optional for ordinary installations.

Shared rules come from the local Git setting `sensitive.sharedRulesFile`, or
otherwise `../a.sensitive.replacements.local.txt`. Project rules belong in
`a.sensitive.replacements.local.txt`. Rules and audit reports are ignored and
must never be committed. Configured but invalid protection makes setup fail
with an error. After changing hook configuration, use `fsenv` in Command Prompt
or start a fresh terminal to run setup again.

These hooks check staged content and the pending commit message. A separate
history audit is necessary before publishing existing commits. Git's
`--no-verify` option bypasses these local hooks.

## Additional features

- Allows clearer input from user for the number of minutes
- Uses threading to revert to default if value isn't entered in fast enough (e.g. if the user forgets to enter even after starting the program)
- Adds all actions into a txt file for analysis if required.
- Allows stopping mechanism via escape button and system tray icon
- Runs discreetly in the background with no visible console window.
- Employs a robust single-instance mechanism using a lock file to prevent multiple executions.
- Features improved responsiveness to exit commands, particularly via system tray, due to more frequent checks.
- Includes comprehensive debug logging for easier troubleshooting.
- Provides batch scripts for setup and execution using standard Python tooling.

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
   - The batch scripts use plain console output and work without the historical `batcolors` submodule.
   - `run.bat` also specifically handles the "another instance running" error message (errorlevel 2) from `caff2.py` with a user-friendly message.

## Hard-Forked from [Stay-Awake](https://github.com/ianian-dot/Stay-Awake-2)

<sup>(Jordan - 2017, Muhammed Abdelkader - 2022, Ian Petrus Tan - 2024)</sup>

Initially, a small python script to move your mouse, press the shift key, and keep your
PC awake when you're away

Uses command line arguments to set the number of minutes between movements and
requires Python 3.10 or newer on Windows.
 Default timer is 3 minutes, but can be 1 or more.

## Dependencies

This software is using PyAutoGui <https://github.com/asweigart/pyautogui> as the driver behind the movement.
