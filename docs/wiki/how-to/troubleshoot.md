# Troubleshoot Caff2

[Documentation home](../README.md) · How-to guide

Run commands below from the installation folder in PowerShell unless stated
otherwise. Diagnose the launcher and worker separately: a successful launcher
exit only means it created the worker process.

## Setup fails

Check `python --version`; a new environment needs Python 3.10 or newer on
`PATH`, with venv and pip available. If Windows opens an installer/store prompt
instead, select the installed Python interpreter or correct its PATH/app alias.

For package-index, proxy, or certificate errors, inspect the pip output above
`Unable to set up the environment`. Use the appropriate local index and CA
settings in the ignored `senv.local.bat`; the supported variables are listed
in [settings](../reference/settings.md). Check access to your configured index
and the certificate-file path. Recreate a damaged environment using the
[maintenance guide](maintain-an-installation.md).

An error about sensitive rules or `llm-shared` belongs to the optional
maintainer integration. Repair the configured rules, shared checkout, or
shared Python environment using the [development guide](develop.md). An ordinary
installation without this configuration is allowed to skip that integration.

## The terminal returns but no tray icon appears

1. Check the notification area's hidden-icons overflow.
2. Inspect the startup logs:

   ```powershell
   Get-Content .\caff2_main.log -Tail 30
   Get-Content .\caff2_worker.log -Tail 30
   Get-Content .\caff2_debug.log -Tail 30
   ```

3. Check `caff2.ini` has a positive integer under `[Settings]`. Confirm the
   folder is writable. If launching Python directly, use the project folder
   as the working directory.
4. If debug logs cannot be written there, inspect
   `$env:TEMP\caff2_fallback_log.txt`. A file can be absent when that stage
   was never reached.
5. Inspect the worker process as described below before trying another launch.

The worker's standard output and errors are hidden. An initialization failure
may produce a Windows error dialog, but logs are the primary evidence.
The `System tray exited normally` debug line is not by itself proof of process
exit: the installed tray library starts its own message-loop thread.

## Another instance is already running

Use the existing tray icon if it is available. Otherwise inspect Caff2-related
Python processes:

```powershell
Get-CimInstance Win32_Process |
    Where-Object {
        $_.Name -in @('python.exe', 'python') -and
        $_.CommandLine -like '*caff2.py*'
    } |
    Select-Object ProcessId, ExecutablePath, CommandLine
```

Inspect the full script path and `--caff2-worker` argument to identify the
correct instance. If it is your unresponsive Caff2 worker, stop that specific
process through Task Manager; do not terminate unrelated Python programs.

`caff2.lock` contains a PID, but a reused PID can belong to a different Python
application. If no Caff2 worker is running, inspect the lock and
`caff2_lock_debug.log`. After confirming it is stale, remove only that file
and launch once:

```powershell
Remove-Item -LiteralPath .\caff2.lock
.\run.bat
```

Simultaneous launches can race because instance detection is not an atomic lock.
Workers from a second Caff2 folder can also be detected by the process scan.

## No activity, or the computer still sleeps

Confirm the tray state is running and wait one full configured interval. The
first activity is delayed; **Run** and automatic timed resume also wait for
the next cycle. **Resume** from a paused state requests a prompt action.

Inspect `caff2_log.txt` for skipped cycles and errors. Confirm the interval is
shorter than the idle timeout, and that Caff2 runs in an interactive session.
Input simulation may not affect a locked, disconnected, or policy-controlled
desktop as it does the local desktop. Consult
[purpose and limits](../explanation/purpose-and-limits.md) if Windows sleeps
or restarts despite recorded activity.

## Custom-duration dialog does not open

Ensure the Python installation includes Tcl/Tk. From the project folder, run:

```powershell
.\.venv\Scripts\python.exe -m tkinter
```

This should open Tk's demonstration window; close it afterwards. If it fails,
repair the Python installation's Tcl/Tk component. Caff2 logs dialog errors
in `caff2_log.txt`. The fixed duration and Indefinite menu entries do not use Tk.

## The interval does not change

Exit the worker before changing the INI or launching with a different number.
A second launcher exits before saving settings, and a running worker never
reloads them. Check the tooltip after restarting. With direct Python launches,
also check the working directory for an unexpected second `caff2.ini`.

## Mouse or keyboard input interferes with work

Choose **Pause > Indefinite**, or **Exit** to stop entirely. Moving the pointer
into a corner will not stop this application, and it does not register Escape
as a global shortcut. Inspect the worker process if the tray is unavailable.

## Prepare a useful issue report

Include the Python version, Windows version, launch method, interval, tray state,
and the relevant error lines from the [log files](../reference/files-and-internals.md).
Record installed package versions if the problem followed an update. Review
logs before sharing them: they can contain local paths, process IDs, timestamps,
and pointer coordinates. Keep private package-index settings and sensitive
replacement rules out of reports.
