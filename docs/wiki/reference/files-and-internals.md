# Files, dependencies, and source map

[Documentation home](../README.md) · Reference

## Runtime files

| File | Location | Contents and lifetime |
|---|---|---|
| `caff2.ini` | Working directory | Tracked interval configuration; read at launch, saved from argument/prompt |
| `caff2_log.txt` | Working directory | Appended action coordinates, state changes, skipped cycles, errors |
| `caff2.lock` | Beside `caff2.py` | Worker PID; removed by Caff2's Exit callback |
| `caff2_main.log` | Beside `caff2.py` | Launcher/worker-selection diagnostics |
| `caff2_worker.log` | Beside `caff2.py` | Worker startup, configuration, icon, thread, and error diagnostics |
| `caff2_lock_debug.log` | Beside `caff2.py` | Lock checks and process discovery |
| `caff2_debug.log` | Beside `caff2.py` | General debug events |
| `caff2_exit.log` | Beside `caff2.py` | Explicit Exit lock cleanup |
| `caff2_fallback_log.txt` | Windows temporary directory | Debug output when the normal debug-file write fails |
| `caff2_icon_<STATE>.ico` | Windows temporary directory | Generated 64 by 64 state icon |
| `caff2_default.ico` | Windows temporary directory | Generated fallback blue icon when needed |
| `caff2_icon.ico` | Beside `caff2.py`, if supplied | Optional fallback used after state-icon generation fails |

`<STATE>` is an `AppState` name, such as `RUNNING_INDEFINITE`. Generated icons
can remain after exit. Logs are opened in append mode and have no built-in
rotation or retention limit. A listed log may not exist until its code path
runs. Fallback logging applies to debug logs, not the action log.

`run.bat` sets the working directory to the application folder. Direct launches
can place the INI and action log elsewhere. The repository ignores the action
log, `*.log`, `*.lock`, `.venv/`, Python caches, `senv.local.bat`, `*.local.*`,
and `.reviews/`. Inspect logs before sharing: they can contain machine-local
details and usage information.

## Dependencies and platform

| Dependency | Use |
|---|---|
| Windows | Console/window APIs, tray integration, batch launchers |
| Python 3.10 or newer | Runtime, including current type-alias syntax |
| `pyautogui` | Mouse positioning/movement and Shift presses |
| `psutil` | Process inspection for instance detection |
| `infi.systray` | Windows notification-area icon and menu |
| `pillow` | Icon drawing and ICO output |
| Tkinter/Tcl/Tk | Standard-library interface and runtime for custom-duration dialogs |

The four external Python packages are listed without version pins in
[`requirements.txt`](../../../requirements.txt). There is no declared Python
package/build configuration or installed console entry point. The supported
entry point is the root script via `run.bat` or Python. The code is
Windows-specific; it imports Windows APIs during module loading.

## Source and repository layout

| Path | Role |
|---|---|
| [`caff2.py`](../../../caff2.py) | Current launcher, worker, activity, tray, configuration, logging |
| [`run.bat`](../../../run.bat) | Environment setup followed by launch from the project directory |
| [`senv.bat`](../../../senv.bat) | Project virtualenv setup and optional maintainer hook integration |
| [`tools/install_sensitive_hooks.py`](../../../tools/install_sensitive_hooks.py) | Validates private-rule setup and delegates hook installation to sibling llm-shared |
| [`src/caff.py`](../../../src/caff.py) | Earlier standalone foreground activity loop; not used by the current launcher |
| `typings/infi/systray/` | Editor/type-checker stubs, not the installed runtime implementation |
| `batcolors/` | Retained historical submodule; current batch scripts do not require it |
| `.project`, `.pydevproject` | Eclipse/PyDev project metadata |
| `.vscode/caff2.code-workspace` | Optional VS Code workspace and appearance settings |
| `docs/wiki/` | This documentation |
| [`LICENSE`](../../../LICENSE) | Eclipse Public License 1.0 |

The submodule URL and legacy branch are recorded in
[`.gitmodules`](../../../.gitmodules). It is not a Caff2 runtime dependency.

## Internal function map

These are implementation details, not a stable public Python API. Importing
the module loads Windows and GUI dependencies and sets `pyautogui.FAILSAFE`
to `False`; it is not a platform-neutral library.

| Area | Symbols in `caff2.py` |
|---|---|
| Entry and lifetime | `main`, `worker_process`, `hide_console`, `exit_app` |
| Instance detection | `is_already_running` |
| Interval selection | `read_config`, `write_config`, `get_minutes_from_args`, `min_num` |
| Activity | `background_task`, `random_mouse_move`, `perform_immediate_action` |
| State | `AppState`, `set_app_state`, `pause_callback`, `run_callback`, `resume_callback` |
| Tray display | `create_icon_image`, `create_menu_options`, `get_tooltip_text`, `update_tooltip` |
| Time formatting | `format_time_duration`, `format_datetime` |
| Logging | `log_action`, `debug_log` |

Global `app_state` and `state_end_time` hold session state; `last_action_time`
feeds the tooltip, `stop_flag` controls loops, and `systray_icon` holds the tray
object. `refresh_minutes` is assigned on startup, while the background and
tooltip functions receive their interval as arguments. Shared state is not
protected by an application-level mutex. `MenuCallback`, `SubMenu`, `Action`,
and `MenuOptions` are typing aliases for nested menu definitions.

`random_mouse_move` chooses independent X/Y offsets between -50 and 50, moves
relative to the current pointer, returns to the starting position plus (1, 1),
and presses Shift three times. It returns the intermediate moved-to coordinates
for logging. An error can return the original coordinates, so an `Action
performed` line alone is not conclusive if adjacent lines report an error.

## Legacy script

`src/caff.py` is not launched by `run.bat`. It uses a foreground infinite loop,
a simple positional argument, and a three-minute fallback for certain invalid
or absent arguments. It moves through ten positions near the screen edge,
returns near the original pointer location, and presses Shift three times.
It has no tray, INI persistence, instance lock, or timed Run/Pause controls.
Its argument handling also rejects some invalid inputs by raising an exception.

Use the root application for the documented Caff2 experience. Do not infer
its defaults or controls from the legacy script.
