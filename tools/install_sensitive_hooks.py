"""Use the optional sibling llm-shared checkout to protect maintainer commits."""

import shutil
import subprocess
import sys
from pathlib import Path


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True,
        encoding="utf-8", check=False,
    )


def main():
    root = Path(__file__).resolve().parent.parent
    shared_root = root.parent / "llm-shared"
    if not shutil.which("git") or not (root / ".git").exists():
        print("HOOK: skipped (no Git checkout).")
        return 0
    checkout = git(root, "rev-parse", "--show-toplevel")
    if checkout.returncode or Path(checkout.stdout.strip()).resolve() != root:
        print("ERROR: Cannot resolve the Caff2 Git checkout.")
        return 1
    configured = git(root, "config", "--path", "--get", "sensitive.sharedRulesFile")
    if configured.returncode not in (0, 1):
        print("ERROR: Cannot read sensitive hook configuration.")
        return 1
    local_rules = root / "a.sensitive.replacements.local.txt"
    if not shared_root.is_dir():
        if configured.returncode == 0 or local_rules.is_file():
            print("ERROR: Sensitive rules are configured, but sibling llm-shared is missing.")
            return 1
        print("HOOK: skipped (optional sibling llm-shared is absent).")
        return 0
    shared_rules = (
        Path(configured.stdout.strip()) if configured.returncode == 0
        else shared_root.parent / "a.sensitive.replacements.local.txt"
    )
    if not shared_rules.is_absolute():
        shared_rules = root / shared_rules
    if not shared_rules.is_file():
        if configured.returncode == 0:
            print("ERROR: Configured shared sensitive rules file is missing.")
            return 1
        shared_rules = None
    if shared_rules is None and not local_rules.is_file():
        print("HOOK: skipped (no private sensitive rules configured).")
        return 0

    interpreters = list(shared_root.glob("venvs/python_3*llm-shared*/Scripts/python.exe"))
    if not interpreters:
        print("ERROR: Set up llm-shared's Python environment before installing hooks.")
        return 1
    interpreter = max(interpreters, key=lambda p: p.parent.parent.stat().st_mtime)
    if Path(sys.executable).resolve() != interpreter.resolve():
        return subprocess.call([str(interpreter), str(Path(__file__).resolve())])

    for name in ("install_hooks.py", "sensitive_pre_commit.py", "sensitive_commit_msg.py"):
        if not (shared_root / "tools" / "sensitive_history" / name).is_file():
            print("ERROR: The llm-shared sensitive hook implementation is incomplete.")
            return 1
    for path in (local_rules, shared_rules):
        if path is None:
            continue
        if path.resolve().is_relative_to(root):
            if git(root, "check-ignore", "--quiet", "--no-index", "--", str(path)).returncode:
                print("ERROR: Private sensitive rules must be Git-ignored.")
                return 1
            tracked = git(root, "ls-files", "--", str(path))
            if tracked.returncode or tracked.stdout.strip():
                print("ERROR: Private sensitive rules must not be tracked.")
                return 1
        if path.is_file():
            lines = path.read_text(encoding="utf-8").splitlines()
            if any(
                not line.strip() or line.lstrip().startswith(("#", "\ufeff"))
                or "==>" not in line or not line.split("==>", 1)[0]
                for line in lines
            ):
                print("ERROR: Invalid sensitive replacement rules format.")
                return 1

    sys.path.insert(0, str(shared_root))
    from tools.sensitive_history.history_scan import (
        HistoryScanError, merge_patterns, patterns_from_replacement_file,
    )
    from tools.sensitive_history.install_hooks import main as install

    try:
        shared = patterns_from_replacement_file(shared_rules) if shared_rules else []
        local = patterns_from_replacement_file(local_rules) if local_rules.is_file() else []
        effective = merge_patterns(shared, local)
    except HistoryScanError:
        print("ERROR: Sensitive rules must contain valid, nonempty watch patterns.")
        return 1
    print(f"HOOK: rules shared={len(shared)}, local={len(local)}, effective={len(effective)}")
    args = [str(root), "--shared-root", str(shared_root)]
    if shared_rules:
        args.extend(["--shared-rules", str(shared_rules)])
    return install(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OSError:
        print("ERROR: Cannot access sensitive hook files or tools.")
        raise SystemExit(1)
