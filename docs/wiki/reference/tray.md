# Tray menu, icons, and timers

[Documentation home](../README.md) · Reference

The root application exposes its controls through a notification-area icon.
Right-click the icon to open the menu. The icon is generated locally with
Pillow and changes with the application state.

## Menu items

| Item | Effect |
|---|---|
| **Pause > duration** | Pause now; return to indefinite running after the duration |
| **Pause > Indefinite** | Pause until another selection changes state |
| **Run > duration** | Run now; switch to indefinite pause after the duration |
| **Run > Indefinite** | Run with no deadline |
| **Resume** | When paused, switch to indefinite running and request an action after about 0.5 seconds; no effect when already running |
| **Exit** | Set stop flag, remove `caff2.lock`, terminate the worker |

Both Run and Pause provide **5 minutes**, **10 minutes**, **15 minutes**,
**30 minutes**, **45 minutes**, **1 hour**, **Custom...**, and **Indefinite**.
Custom accepts integer minutes from 0 to 10080 inclusive. Zero means indefinite;
Cancel leaves the current state unchanged. Tkinter provides these dialogs.

The installed `infi.systray` library also appends a **Quit** item. Caff2 does
not attach its `exit_app` callback to that library item. Use **Exit** for
Caff2's explicit lock cleanup. Double-click behavior is library-defined;
Caff2 does not implement Caffeine's double-click active/inactive toggle.

## States and icons

| State | Square | Circle | Outline | Expiration result |
|---|---|---|---|---|
| Running indefinitely | Blue | White | None | None |
| Running for a duration | Blue | Yellow | Red | Paused indefinitely |
| Paused indefinitely | Red | Yellow | None | None |
| Paused for a duration | Yellow | Red | None | Running indefinitely |

An icon-generation error can cause a fallback icon instead, so use the tooltip
and logs to confirm state when the appearance is unexpected.

## Tooltip

The updater refreshes roughly every second. Available fields are:

- `Refresh: every N minutes`: the worker's activity interval.
- `State`: Running, Running (timed), Paused, or Paused (timed).
- `Duration`: remaining time and a local deadline, while a timed state has
  remaining time.
- `Last action`: elapsed minutes and seconds since the last successful action,
  shown only in running states after an action has occurred.

Remaining durations are formatted as seconds, minutes/seconds, hours/minutes,
or days/hours. Deadlines omit the date when on the current day, include the day
within the current month, then day/month within the year, and day/month/year
otherwise. The tray library limits tooltip length, so long text may be cut off.

## Timing semantics

The activity clock starts with a full interval of waiting. Paused cycles are
skipped, but the clock continues. Changing Run/Pause state does not reset it.
Only the explicit Resume callback adds an early action; it also leaves the
regular clock in place.

Each timed selection establishes a new deadline relative to the selection
time and replaces any previous deadline. Expiration is checked approximately
once per second; it is not an exact scheduler. A timed run can finish without
an activity cycle if the interval does not fall within the chosen duration.
Pause does not interrupt a mouse/keyboard action already in progress.

For task-oriented instructions, use the
[session controls guide](../how-to/control-a-session.md).
