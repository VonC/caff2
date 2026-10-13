# Start Caff2 when you sign in

[Documentation home](../README.md) · How-to guide

Caff2 has no built-in startup installer. Use a Windows shortcut if you want
it to start in your interactive desktop session after sign-in.

1. Complete the [first-run tutorial](../tutorials/first-run.md) and exit Caff2.
2. Keep the installation in a stable, writable folder.
3. Create a shortcut to that folder's `run.bat`. In its properties, set the
   **Target** to the quoted full path, optionally followed by the interval:

   ```text
   "C:\Apps\caff2\run.bat" 1
   ```

   Replace the example path with your installation. Set **Start in** to its
   folder, such as `C:\Apps\caff2`.
4. Press **Win+R**, enter `shell:startup`, and put the shortcut in that folder.
5. Launch the shortcut once and verify the tray icon and interval. At the next
   sign-in, verify it starts again.

`run.bat` sets the working directory itself, but providing **Start in** also
makes the shortcut's intent clear. A setup console may appear briefly. Every
launch goes through environment setup and may access the package index.

If dependencies are already installed and you want to skip setup on sign-in,
use this shortcut target instead:

```text
"C:\Apps\caff2\.venv\Scripts\python.exe" "C:\Apps\caff2\caff2.py" 1
```

For that form, **Start in** must be the Caff2 folder: direct Python launches
resolve `caff2.ini` and the action log from the working directory. Keep using
`python.exe`; the current instance detector does not recognize `pythonw.exe`
by name. After updating dependencies, run setup manually before using the
shortcut again.

Remove the shortcut to disable automatic startup; this does not stop a worker
already running. Use **Exit** for that. Caff2 is not a Windows service and does
not keep working before sign-in or after sign-out. The tray and input simulation
require an interactive desktop session.
