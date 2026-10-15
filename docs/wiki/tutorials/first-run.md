# Install Caff2 and observe your first activity cycle

[Documentation home](../README.md) · Tutorial

This walkthrough takes you from a complete checkout to a running tray icon,
one observed activity cycle, and a clean exit. Use an interactive Windows
desktop and a folder you can write to.

## 1. Prepare Python and the application

Install Python 3.10 or newer for Windows with pip, venv, and Tcl/Tk support.
Enable **Add python.exe to PATH** in the installer. Tcl/Tk is used by the
optional custom-duration dialogs.

Install [Git for Windows](https://git-scm.com/downloads/win), then open PowerShell
and clone the repository with its `batcolors` submodule:

```powershell
git clone --recurse-submodules https://github.com/VonC/caff2.git
cd caff2
```

The recursive clone checks out the submodule revision recorded by Caff2. If you
already cloned without `--recurse-submodules`, run this from the folder containing
`run.bat`:

```powershell
git submodule update --init --recursive
```

GitHub ZIP downloads omit submodule contents and Git metadata. If you downloaded
a ZIP, use the clone command above in a separate folder for a complete checkout.

Check that the submodule is initialized:

```powershell
git submodule status
```

The output should show a commit ID followed by `batcolors`, with a leading space.
A leading `-` means it is uninitialized; a leading `+` means its checkout differs
from the recorded revision. Run the update command above to initialize it or
check out the recorded revision.

Check the interpreter:

```powershell
python --version
```

It should report Python 3.10 or newer. If it does not, follow
[setup troubleshooting](../how-to/troubleshoot.md#setup-fails).

## 2. Launch with a one-minute interval

```powershell
.\run.bat 1
```

Setup creates `.venv` if necessary and installs the packages listed in
`requirements.txt`. The first setup needs access to a Python package index.
Setup can check dependencies again on later launches; it reuses the environment.
An optional-hook message saying protection was skipped is normal in an ordinary
installation without maintainer rules.

The launcher should print `Caff2 started in background (every 1 minutes)` and
return to the terminal. The worker runs without a console. Look in the Windows
notification area, including its hidden-icons overflow, for a blue square
with a white circle.

## 3. Observe an activity cycle

Hover over the icon. The tooltip should report a one-minute refresh interval
and a running state. Leave the pointer over an idle area of the desktop and
wait a little over a minute. Caff2 should briefly move it and press Shift three
times. The tooltip can then show how long ago the last action occurred.

You can also inspect the action log from the project folder:

```powershell
Get-Content .\caff2_log.txt -Tail 10
```

Look for an `Action performed` entry. If the icon or action is missing, use
the [troubleshooting guide](../how-to/troubleshoot.md). A launcher success
message alone does not confirm worker startup.

## 4. Pause, resume, and exit

Right-click the icon and select **Pause > Indefinite**. Its background becomes
red, with a yellow circle, and the tooltip reports a paused state. Activity
cycles are skipped while the worker remains available in the tray.

Select **Resume**. The icon returns to blue and white, and an action is requested
after about half a second. When finished, right-click and select **Exit**.
The worker stops and removes `caff2.lock`.

You have now exercised a complete session. Next, use the
[session controls guide](../how-to/control-a-session.md) for timed activity,
or [change the interval](../how-to/configure-the-interval.md). Keeping the
desktop active does not guarantee prevention of Windows Update restarts;
see [purpose and limits](../explanation/purpose-and-limits.md).
