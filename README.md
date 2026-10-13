# Caff2: Caffeine, but in Python, for Windows

Caff2 keeps a Windows desktop active with periodic mouse movement and Shift
presses, controlled from a tray icon. Inspired by
[Caffeine](https://www.zhornsoftware.co.uk/caffeine/), it helps prevent idle sleep.
It does not control Windows Update or guarantee prevention of restarts.

## Quick install and start

1. Install [Python 3.10 or newer for Windows](https://www.python.org/downloads/windows/)
   with pip, and enable **Add python.exe to PATH**.
2. [Download Caff2](https://github.com/VonC/caff2/archive/refs/heads/master.zip)
   and extract it, or clone this repository. Open PowerShell or Command Prompt
   in the folder containing `run.bat`.
3. Run:

   ```bat
   .\run.bat
   ```

The first run creates a local Python environment and installs dependencies;
it needs access to a Python package index. Later runs reuse that environment
and may check dependencies again. No manual package installation or Git is needed
when using the download.

## Use Caff2

Look for the **blue square with a white circle** in the Windows notification
area (including hidden icons). The shipped interval is **one minute**; the
first mouse movement occurs after a full interval. Hover to see the current state.

Right-click the icon to select:

- **Pause**: stop activity indefinitely or for a chosen duration.
- **Resume**: continue activity after a pause.
- **Run**: run for a chosen duration, then pause, or run indefinitely.
- **Exit**: stop Caff2 completely.

To change the interval, exit Caff2 first, then launch with a number of minutes:

```bat
.\run.bat 5
```

This saves a five-minute interval in `caff2.ini` for future launches.

## Documentation

The **[documentation wiki](docs/wiki/README.md)** covers explanations, tutorials,
how-to guides, and reference material. Start with the
[first-run walkthrough](docs/wiki/tutorials/first-run.md),
[troubleshooting](docs/wiki/how-to/troubleshoot.md), or
[development and commit protection](docs/wiki/how-to/develop.md).

## Credits and license

Hard-forked from [Stay-Awake-2](https://github.com/ianian-dot/Stay-Awake-2),
with contributions by Jordan (2017), Muhammed Abdelkader (2022), and
Ian Petrus Tan (2024), followed by Caff2 work by VonC.
Uses [PyAutoGUI](https://github.com/asweigart/pyautogui) for input simulation.
Licensed under the [Eclipse Public License 1.0](LICENSE).
