# Pause, resume, run for a limited time, and exit

[Documentation home](../README.md) · How-to guide

Use the running application's tray icon for session controls. Right-click it
to open the menu; it may be in Windows' hidden-icons overflow.

## Pause while you work with the mouse or keyboard

Choose **Pause > Indefinite**. Input simulation stops at subsequent activity
checks, while the tray remains available. An action already in progress may
finish. Choose **Resume** when ready to continue; this switches to indefinite
running and requests an action after about half a second.

To resume automatically, choose **Pause > 15 minutes**, or another duration.
When that time expires, Caff2 runs indefinitely again. It sends input on the
next regular activity cycle, which need not coincide with the end of the pause.

## Keep running for a limited period

Choose **Run > 1 hour** to run until an hour from now, then pause indefinitely.
The application stays in the tray after the timed run completes. This does
not schedule application exit, computer sleep, or shutdown.

A Run duration does not change how often input occurs. For example, a
five-minute activity interval remains five minutes during a one-hour run.
Choosing **Run > Indefinite** removes the deadline. Unlike **Resume**, it does
not request an immediate action.

## Use a custom duration

Choose **Run > Custom...** or **Pause > Custom...**, enter a whole number of
minutes, and confirm. The range is 0 through 10080 (seven days); 0 selects
indefinite operation. Cancel leaves the state unchanged. If the dialog cannot
open, see [custom-dialog troubleshooting](troubleshoot.md#custom-duration-dialog-does-not-open).

Each new selection replaces any earlier timer. Running and paused durations
are not saved across application restarts.

## Exit completely

Choose Caff2's **Exit** menu item. It removes the worker lock and terminates
the process. If the tray library also shows **Quit**, prefer **Exit**, which
runs Caff2's cleanup callback. Closing the terminal that launched Caff2 does
not stop its worker, and Escape is not a global stop key.

If the icon is unavailable, use the process inspection procedure in
[troubleshooting](troubleshoot.md#another-instance-is-already-running).

For all menu labels, colors, and timer behavior, see the
[tray reference](../reference/tray.md).
