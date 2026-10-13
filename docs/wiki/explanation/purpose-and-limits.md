# Purpose, Caffeine, and practical limits

[Documentation home](../README.md) · Explanation

Caff2 is a small Windows utility for keeping an interactive desktop active
during a long task. Its motivation includes avoiding idle periods that can
interrupt work through sleep, screen locking, or an inconvenient update restart.
Its actual mechanism is periodic mouse movement and simulated Shift presses.

## Relationship to Caffeine

[Caffeine by Zhorn Software](https://www.zhornsoftware.co.uk/caffeine/) is the
inspiration for the experience: a background utility controlled from the tray.
Caffeine normally simulates F15 activity every 59 seconds and also offers
Windows execution-state API options. Caff2 uses Python and PyAutoGUI, with
mouse movements and three Shift presses at an interval measured in minutes.
It does not implement Caffeine's command-line switches or all of its features.

The source lineage is separate from that inspiration. Caff2 is a hard fork of
[Stay-Awake-2](https://github.com/ianian-dot/Stay-Awake-2), with contributions
credited to Jordan (2017), Muhammed Abdelkader (2022), and Ian Petrus Tan (2024),
and subsequent Caff2 work by VonC. The repository uses the
[Eclipse Public License 1.0](../../../LICENSE).

## Sleep prevention and Windows Update

Simulated input can prevent inactivity timers from expiring when Windows and
the current session recognize that input. Choose an activity interval shorter
than the relevant idle timeout. Caff2 neither changes the power plan nor calls
`SetThreadExecutionState`; it relies on input simulation.

An awake computer can still install updates and restart. Caff2 does not pause
updates, set active hours, cancel shutdowns, or override restart deadlines.
Manual sleep, lid-close actions, session policies, and a disconnected remote
desktop can also behave differently from ordinary desktop inactivity. Its
activity is therefore not proof that an unattended task will survive.

Windows Update's active-hours setting is the appropriate companion control
for reducing inconvenient restarts. Microsoft documents it in
[Keep your PC up to date with active hours](https://support.microsoft.com/en-us/windows/deployment/updates-lifecycle/keep-your-pc-up-to-date-with-active-hours).
On Windows 11 it is under **Settings > Windows Update > Advanced options >
Active hours**. Update policy remains independent of Caff2's Run/Pause state.

## Why a Python process?

One motivation for Caff2 is the maintainer's observation that Windows Defender
could flag the Caffeine executable while this Python application was not
flagged in their environment. That is an observation about those installations,
not a promise about antivirus behavior on other machines or future versions.
Caff2 does not change Defender settings or attempt to evade detection.

Running the source through a standard Python interpreter also makes the
application's behavior available for inspection and modification. It still
depends on installed Python packages and the machine's security policy.

## Effects you can notice

The pointer briefly moves by up to 50 pixels in each direction, then returns
to one pixel beyond its starting position on each axis. Three Shift presses
follow. These actions can affect the application currently receiving input;
pause Caff2 when they would interfere with your work.

The application disables PyAutoGUI's screen-corner fail-safe. It has no global
Escape-key stop handler. Use the tray's **Exit** item to stop it, or follow
the [troubleshooting guide](../how-to/troubleshoot.md) if the tray is unavailable.
Keeping a session active can also keep it unlocked; Caff2 is not a substitute
for locking the computer when appropriate.

For the timing model, see [processes and state](architecture.md).
