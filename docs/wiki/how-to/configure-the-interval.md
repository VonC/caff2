# Change the activity interval

[Documentation home](../README.md) · How-to guide

The interval controls how many minutes pass between mouse-and-Shift activity
cycles. Choose a whole number of at least 1, shorter than the idle timeout you
want to avoid.

## Set the interval at launch

1. If Caff2 is running, select **Exit** from its tray menu.
2. Open a terminal in the project folder.
3. Start with the new interval, for example five minutes:

   ```powershell
   .\run.bat 5
   ```

4. Hover over the tray icon and confirm `Refresh: every 5 minutes`.

The launcher saves this value in `caff2.ini`. Future launches without arguments
reuse it. Starting another copy while a worker exists exits before updating
the setting, so it cannot reconfigure that worker.

## Edit the INI file instead

Exit Caff2, then set `minutes` in the project's `caff2.ini`:

```ini
[Settings]
minutes = 1
```

Run `.\run.bat` to load the saved value. The shipped file contains 1. A running
worker does not reload edits; restart it to apply them. `caff2.ini` is tracked
by Git, so local preference changes appear in `git status`.

Use a positive integer even though the INI reader does not validate the range.
Zero prevents the worker from starting its activity loop; negative numbers
can cause an excessively rapid loop. Fractional or nonnumeric values are not
valid intervals.

## Recover from missing configuration

Launch with an explicit interval, such as `.\run.bat 1`, and verify the resulting
INI file and tray tooltip. If the file is malformed, repair its section and
value first. A write failure can leave the worker reading an older value or
no usable configuration.

With no usable argument or configuration, the launcher asks interactively for
minutes. That prompt has no timeout or automatic default. Supplying a valid
argument is preferable for shortcuts and unattended launches.

For full parsing and precedence details, see
[commands](../reference/command-line.md) and [settings](../reference/settings.md).
