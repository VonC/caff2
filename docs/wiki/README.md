# Caff2 documentation

Caff2 keeps a Windows desktop active by periodically moving the mouse and
pressing Shift. It runs as a Python process with a notification-area icon,
inspired by [Caffeine](https://www.zhornsoftware.co.uk/caffeine/).

Use it to reduce interruptions from idle sleep during work you want to keep
running. It does not control Windows Update or guarantee that Windows will
never restart. Read [purpose and limits](explanation/purpose-and-limits.md)
for that distinction and the context behind choosing Python.

These pages describe the root `caff2.py` application and its Windows launchers.
The older `src/caff.py` script is documented separately in the
[source reference](reference/files-and-internals.md).

## Explanation

Understand the application and its design.

- [Purpose, Caffeine, and practical limits](explanation/purpose-and-limits.md)
- [Processes, activity cycles, and state](explanation/architecture.md)

## Tutorials

Learn by completing a first session.

- [Install Caff2 and observe your first activity cycle](tutorials/first-run.md)

## How-to guides

Complete a specific task.

- [Pause, resume, run for a limited time, and exit](how-to/control-a-session.md)
- [Change the activity interval](how-to/configure-the-interval.md)
- [Start Caff2 when you sign in](how-to/start-at-sign-in.md)
- [Update or remove an installation](how-to/maintain-an-installation.md)
- [Troubleshoot setup, missing icons, and existing instances](how-to/troubleshoot.md)
- [Set up development and sensitive-commit protection](how-to/develop.md)

## Reference

Look up exact values and behavior.

- [Commands and exit codes](reference/command-line.md)
- [Configuration and environment variables](reference/settings.md)
- [Tray menu, icons, and timers](reference/tray.md)
- [Files, dependencies, and source map](reference/files-and-internals.md)

[Project overview](../../README.md) · [License](../../LICENSE)
