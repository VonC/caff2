# Set up development and sensitive-commit protection

[Documentation home](../README.md) · How-to guide

## Prepare the project environment

Clone the repository and open **Command Prompt** in its root:

```bat
call .\senv.bat
```

This activates `.venv`, installs requirements, and checks optional sensitive
hooks. Interactive Command Prompt also gains `r` (run Caff2) and `fsenv`
(force setup again) DOSKEY macros. Scripts should call the batch files directly
instead of relying on these macros.

PowerShell does not retain activation performed inside a batch child process.
Use the environment's executable directly there:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m py_compile caff2.py tools/install_sensitive_hooks.py src/caff.py
```

To set up without batch files:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Manual pip setup does not install the optional hooks. Run
`.\.venv\Scripts\python.exe tools/install_sensitive_hooks.py` when that
integration applies. The helper switches to llm-shared's own interpreter for
installation; the application environment is not the hook runtime.

## Configure optional maintainer protection

Ordinary users do not need a shared checkout or private rules. For maintainers
using this integration:

1. Place an initialized `llm-shared` checkout beside `caff2` and prepare its
   own Python environment. The helper searches its
   `venvs/python_3*llm-shared*/Scripts/python.exe` environments and chooses
   the one with the most recently modified environment directory.
2. Keep project-specific rules in the ignored
   `a.sensitive.replacements.local.txt`. Shared rules come from the local Git
   setting `sensitive.sharedRulesFile`, or from the same filename in the
   common parent directory. If you need a different shared path, set it with
   `git config --local sensitive.sharedRulesFile "C:/path/to/private-rules.txt"`,
   replacing the example path.
3. Follow the shared tooling's replacement-file syntax. This integration
   rejects blank lines, comment lines, empty patterns, and lines without `==>`.
   Do not store confidential examples in public documentation.
4. In a fresh Command Prompt, call `senv.bat`; in an already initialized one,
   run `fsenv`. Inspect the reported rule counts and installation result.

Shared and project rules are merged. The composable `pre-commit` and
`commit-msg` integration preserves existing hooks. Configured but invalid
protection fails setup, including a missing configured rules file or shared
environment. With no Git checkout, or no optional integration configured,
the helper can report a successful skip.

When changing hook integration, verify it with actual clean and deliberately
rejected commits in a disposable repository using synthetic rules. Do not
introduce real confidential terms into this repository as test content.
Pre-commit checks staged content, and commit-msg checks the pending message;
these checks do not establish that existing history is clean. A separate
history audit is needed for that. `--no-verify` can bypass local hooks.

## Validate an application change

There is currently no automated Caff2 test suite or declared CI test command.
The `batcolors` submodule's test script is unrelated to the application.
The compile and dependency checks above catch syntax and dependency issues,
but do not exercise Windows input or tray behavior.

For changes to runtime behavior, use an interactive Windows session to check
launch, one activity cycle, pause, resume, timed transitions, a second launch,
and Exit. Exercise custom dialogs when they change. Keep the
[documented timing rules](../reference/tray.md) in mind while checking results.
Review relevant logs after the session.

The [source map](../reference/files-and-internals.md) identifies entry points,
internal functions, type stubs, and the legacy script. Update the matching wiki
page when behavior changes. Keep local rules, logs, virtual environments, and
review evidence ignored, and inspect `git diff` and `git status` before staging.
