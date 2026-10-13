# Commands and exit codes

[Documentation home](../README.md) · Reference

## Supported entry points

Run from the project folder unless otherwise noted.

| Command | Behavior |
|---|---|
| `.\run.bat` | Prepare the environment, change to the project directory, launch with the saved interval |
| `.\run.bat 5` | As above, saving a five-minute interval before launch |
| `call .\senv.bat` | In Command Prompt, prepare and activate the environment without launching Caff2 |
| `.\.venv\Scripts\python.exe caff2.py` | Launch directly using existing dependencies and the working directory's configuration |
| `.\.venv\Scripts\python.exe caff2.py 5` | Direct launch with a saved five-minute interval |
| `.\.venv\Scripts\python.exe tools/install_sensitive_hooks.py` | Install or verify optional maintainer hooks, or report a skip |

`run.bat` forwards its arguments to `caff2.py`. The application searches all
arguments after the script name and uses the first integer at least 1.
Unrecognized text, zero, negative numbers, and non-integer arguments are ignored.
For example, `caff2.py text 5 10` selects 5. This permissive parser is not an
option parser: there are no implemented `--help`, `--version`, `--stop`, or
Caffeine-compatible switches. An unknown switch can still lead to a normal
launch using saved configuration.

`--caff2-worker` is an internal argument that selects worker mode and bypasses
the normal instance check. Do not use it as a regular launch command.

The launch sequence checks for an existing instance first, then selects:

1. The first valid interval argument, saved to `caff2.ini`.
2. Otherwise the integer in `[Settings] minutes` in that file.
3. Otherwise an interactive prompt, whose answer is saved to the file.

There is no prompt timeout and no automatic three-minute fallback in the
current root application. The checked-in configuration is one minute.

## Return codes

| Entry point | Code | Meaning |
|---|---|---|
| `caff2.py` launcher | 0 | Worker process created; also used for Ctrl+C at the interval prompt |
| `caff2.py` launcher | 1 | Exception caught while starting the application |
| `caff2.py` launcher | 2 | Another instance detected; configuration is not updated |
| `run.bat` | 0, 1, 2 | Forwards the application result when Python was invoked |
| `run.bat` | 1 | Also used for any failure returned by `senv.bat` |
| `run.bat` | 5 | Could not change to the project directory |
| `senv.bat` | 0 | Setup ready, including any permitted hook skip |
| `senv.bat` | 3 | Python/version, environment creation/activation, or dependency-installation failure |
| `senv.bat` | 5 | `senv.local.bat` returned an error |
| `senv.bat` | 6 | Optional hook integration failed |
| Hook helper | 0 | Protection installed/verified or legitimately skipped |
| Hook helper | Nonzero | Invalid/incomplete configuration or shared installer failure |

`run.bat` prints a friendly existing-instance message for code 2. These are
explicit codes from the scripts; failures outside their handlers, such as
interpreter/import errors, can also produce nonzero statuses.

The launcher does not wait for the worker to finish initialization. Worker
exceptions are logged and may be shown in a message box; they do not propagate
back to the launcher. Its exit code cannot serve as a worker health check.

## Interactive Command Prompt macros

`senv.bat` defines `r` to invoke `run.bat` and `fsenv` to clear
`CAFF2_ENV_READY` before calling setup again. DOSKEY macros apply to interactive
Command Prompt input, not PowerShell or ordinary batch execution. See
[environment settings](settings.md) for the setup guard.
