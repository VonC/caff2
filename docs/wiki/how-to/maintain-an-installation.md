# Update or remove an installation

[Documentation home](../README.md) · How-to guide

## Update the application

1. Select **Exit** in the tray before replacing source files or dependencies.
2. Preserve your interval from `caff2.ini` and any private `senv.local.bat`.
   For a Git checkout, inspect `git status` and preserve local changes before
   updating to the version you intend to use.
3. Update the source from the [project repository](https://github.com/VonC/caff2).
   For an archive installation, extract the new copy to a fresh folder and
   carry over your settings deliberately.
4. Open a fresh terminal in the installation folder and run `.\run.bat`.
   In an already initialized Command Prompt, run `fsenv` first to refresh setup.
5. Confirm the tray tooltip and one activity cycle. Update any startup shortcut
   if the installation path changed.

Dependencies are not version-pinned in `requirements.txt`. Setup installs any
missing requirements, but its pip command does not request an upgrade of every
already installed package. For dependency investigations, record the installed
versions using `.\.venv\Scripts\python.exe -m pip freeze`.

## Recreate a damaged Python environment

Exit Caff2 and close terminals using its virtual environment. Rename `.venv`
to a spare name outside the checkout, or remove just that generated environment
after confirming the path. Then run `.\run.bat` in a fresh terminal. Setup
creates a new `.venv` using the Python on `PATH` and reinstalls requirements.
Your application settings remain in `caff2.ini`.

## Remove Caff2

1. Select **Exit**, and confirm the Caff2 worker has stopped.
2. Remove any startup shortcut you added.
3. Preserve any source changes, settings, logs, or private maintainer material
   you need to keep.
4. Delete your Caff2 installation folder when you no longer need it.

The application does not install a Windows service or a global Python package
through `run.bat`; its dependencies live in `.venv`. Generated icons named
`caff2_icon_*.ico`, `caff2_default.ico`, and a possible `caff2_fallback_log.txt`
can remain in the Windows temporary directory. See the
[file reference](../reference/files-and-internals.md) for their purpose.
