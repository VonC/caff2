# Configuration and environment variables

[Documentation home](../README.md) · Reference

## Application configuration

The root application reads `caff2.ini` relative to the current working directory.
`run.bat` sets that directory to the project root. The shipped content is:

```ini
[Settings]
minutes = 1
```

| Field | Meaning |
|---|---|
| `[Settings]` | Required section name, with this capitalization |
| `minutes` | Integer interval between input cycles, in minutes; use at least 1 |

The CLI and interactive prompt enforce a minimum of 1; the INI reader only
converts text to an integer. A zero value causes worker startup to return
without starting activity, while a negative value can cause a rapid loop.
An absent section/key, missing file, or conversion/read error gives no usable
configuration and leads the normal launcher to prompt if there is no valid
argument. Malformed INI syntax can also prevent saving a replacement value.

Argument and prompt values are written with `ConfigParser`. Saving rewrites
the file; existing comments and formatting need not survive. The file is
tracked by Git. Read/write errors are printed, but a failed write is not
necessarily fatal to the launcher; the worker rereads the file independently.

Only the interval is persisted. Run/Pause state and deadlines are in memory,
there is no live reload, and each worker starts in indefinite running mode.
There is no setting for the mouse displacement, Shift count, hotkey, or startup
state. The [tray duration](tray.md) is separate from this interval.

## Private setup configuration

`senv.bat` calls an optional `senv.local.bat` in the project root before creating
or preparing the environment. It is ignored by Git and can set private package
index or certificate variables using normal batch `set "NAME=value"` syntax.
It is executable local setup code, not an INI file. Its nonzero return causes
setup to exit with code 5.

These are setup inputs; the Caff2 worker does not read them as application
settings. Do not put credentials or internal endpoints in tracked files.

| Variable | Handling by `senv.bat` |
|---|---|
| `PIP_INDEX_URL` | Respected by pip; not overwritten when already defined |
| `PIP_EXTRA_INDEX_URL` | Respected by pip; not overwritten when already defined |
| `PIP_CERT` | Respected by pip; not overwritten when already defined |
| `UV_INDEX_URL` | Copied to `PIP_INDEX_URL` only when the latter is undefined |
| `UV_EXTRA_INDEX_URL` | Copied to `PIP_EXTRA_INDEX_URL` only when the latter is undefined |
| `UV_CERT` | Cleared if its path does not exist; otherwise copied to unset `PIP_CERT` and `SSL_CERT_FILE` |
| `PYPI_HOST` | If set and `UV_INDEX_URL` is unset, creates `UV_INDEX_URL` as `https://` followed by this value |
| `SSL_CERT_FILE` | Preserved if already defined; otherwise may receive valid `UV_CERT` |

The scripts run pip, not uv; the `UV_*` variables provide compatible setup
inputs. pip also applies its own standard environment and configuration rules.

## Setup state and helper variables

| Variable | Purpose |
|---|---|
| `CAFF2_ENV_READY` | Project-path guard for completed setup in the current environment |
| `PRJ_DIR`, `PRJ_DIR_NAME` | Derived project path and folder name, set by setup |
| `NO_MORE_SENV_<folder-name>` | Compatibility marker set to `true` on successful setup |

When the guard matches this project and `.venv\Scripts\activate.bat` exists,
setup reactivates it and returns early. That skips the local setup file,
version/dependency checks, and hook installation for that invocation. Clear
the guard with `fsenv` in interactive Command Prompt, or use a fresh terminal,
when you need to rerun setup after changes.

`run.bat` uses `setlocal`, so setup variables it creates do not persist into
its caller. A caller that already ran `senv.bat` can pass the guard into it.
There is no configured offline mode; an unguarded setup invokes pip even when
the virtual environment already exists.

## Sensitive-rule configuration

The helper merges project rules from `a.sensitive.replacements.local.txt` with
shared rules from Git's local `sensitive.sharedRulesFile` setting. If that
setting is absent, it looks for the same rules filename in the parent of the
sibling `llm-shared` checkout. Relative configured paths resolve from Caff2's
root. Rules inside this checkout must be ignored and untracked.

See [development and hook setup](../how-to/develop.md) for prerequisites and
failure behavior. This optional configuration is independent of `caff2.ini`.
