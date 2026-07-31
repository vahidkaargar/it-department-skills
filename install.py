#!/usr/bin/env python3
"""it-department-skills installer — standalone, copy-based (no symlinks).

Copies rules, skills, and the discovery system into your home config.
After install the cloned repo is no longer needed; re-run install.py from a
fresh clone to update. Idempotent. Backs up anything it would overwrite.

Cross-platform (macOS/Linux/Windows) — pure stdlib, no bash/perl/shellcheck.
"""
import datetime
import filecmp
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
IGNORE_NAMES = {"index.json", "rules-index.json", "CATALOG.md", "__pycache__"}


def say(msg=""):
    print(msg)


def parse_args(argv):
    dry_run = False
    yes = False
    with_guard_hook = False
    home_override = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--dry-run":
            dry_run = True
        elif a in ("--yes", "-y"):
            yes = True
        elif a == "--with-guard-hook":
            with_guard_hook = True
        elif a in ("--help", "-h"):
            say("usage: install.py [--dry-run] [--yes] [--with-guard-hook]")
            say("  --dry-run         print actions without changing anything")
            say("  --yes             skip confirmation prompts")
            say("  --with-guard-hook install the opt-in skills-discovery-guard hook")
            say("                    non-interactively (ignored without --yes)")
            say("  --home PATH       internal: override home dir (for CI/testing)")
            sys.exit(0)
        elif a == "--home":
            i += 1
            if i >= len(argv):
                print("--home requires a value", file=sys.stderr)
                sys.exit(1)
            home_override = argv[i]
        else:
            print(f"unknown option: {a} (see --help)", file=sys.stderr)
            sys.exit(1)
        i += 1
    return dry_run, yes, with_guard_hook, home_override


DRY_RUN, YES, WITH_GUARD_HOOK, HOME_OVERRIDE = parse_args(sys.argv[1:])
HOME = Path(HOME_OVERRIDE) if HOME_OVERRIDE else Path.home()
BACKUP_DIR = HOME / ".it-department-skills-backup" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def do_mkdir(p: Path):
    if DRY_RUN:
        say(f"[dry-run] mkdir -p {p}")
    else:
        p.mkdir(parents=True, exist_ok=True)


def make_executable(p: Path):
    if DRY_RUN:
        return
    try:
        mode = p.stat().st_mode
        p.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass


def dirs_identical(a: Path, b: Path) -> bool:
    if a.is_dir() != b.is_dir():
        return False
    if a.is_file():
        try:
            return filecmp.cmp(a, b, shallow=False)
        except OSError:
            return False
    cmp = filecmp.dircmp(a, b, ignore=list(IGNORE_NAMES))
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(dirs_identical(a / d, b / d) for d in cmp.common_dirs)


def backup_path(src: Path, dst: Path):
    if src.is_symlink():
        dst.symlink_to(os.readlink(src))
    elif src.is_dir():
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy2(src, dst)


def remove_path(p: Path):
    if p.is_symlink() or p.is_file():
        p.unlink()
    elif p.is_dir():
        shutil.rmtree(p)


def copy_path(src: Path, dst: Path):
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def install_copy(src: Path, dst: Path):
    """Copy file/dir, backing up an existing different dst."""
    do_mkdir(dst.parent)

    if dst.exists() or dst.is_symlink():
        # a symlinked dst is never "up to date" — it must become a real copy;
        # generated index files are excluded so re-runs stay idempotent
        if not dst.is_symlink() and dirs_identical(src, dst):
            say(f"ok:      {dst} (already up to date)")
            return
        # mirror the destination path inside the backup dir so same-named
        # destinations (e.g. skills-discovery, installed twice) cannot collide
        bdst = BACKUP_DIR / dst.relative_to(HOME)
        do_mkdir(bdst.parent)
        say(f"backup:  {dst} -> {bdst}")
        if DRY_RUN:
            say(f"[dry-run] backup {dst} -> {bdst}")
            say(f"[dry-run] remove {dst}")
        else:
            backup_path(dst, bdst)  # a failed backup raises BEFORE remove
            remove_path(dst)

    if DRY_RUN:
        say(f"[dry-run] copy {src} -> {dst}")
    else:
        copy_path(src, dst)
    say(f"installed: {dst}")


def main():
    say("== it-department-skills installer (copy-based, standalone) ==")
    say(f"repo: {REPO_DIR}")
    if DRY_RUN:
        say("(dry run — nothing will be changed)")

    # 1. Rules -----------------------------------------------------------
    say("")
    say("-- rules --")
    do_mkdir(HOME / ".ai")
    do_mkdir(HOME / ".claude")
    install_copy(REPO_DIR / "rules" / "AGENT_RULES.md", HOME / ".ai" / "rules.md")
    install_copy(REPO_DIR / "rules" / "AGENT_RULES.md", HOME / ".claude" / "AGENT_RULES.md")
    install_copy(REPO_DIR / "rules" / "absolute-mode.md", HOME / ".claude" / "absolute-mode.md")

    # preserve a personalize.py "Absolute Mode OFF" choice across updates
    if not DRY_RUN:
        for f in (HOME / ".ai" / "rules.md", HOME / ".claude" / "AGENT_RULES.md"):
            b = BACKUP_DIR / f.relative_to(HOME)
            if (
                b.is_file()
                and f.is_file()
                and "Absolute Mode OFF by default" in b.read_text(errors="ignore")
                and "Absolute Mode ACTIVE by default" in f.read_text(errors="ignore")
            ):
                text = f.read_text()
                text = text.replace(
                    "Absolute Mode ACTIVE by default",
                    'Absolute Mode OFF by default (enable per-session: say "absolute mode")',
                )
                f.write_text(text)
                say(f"kept:    Absolute Mode OFF (your personalize.py choice) in {f}")

    context_md = HOME / ".ai" / "context.md"
    if not context_md.exists():
        if DRY_RUN:
            say(f"[dry-run] copy {REPO_DIR / 'templates' / '.ai' / 'context.md'} -> {context_md}")
        else:
            do_mkdir(context_md.parent)
            shutil.copy2(REPO_DIR / "templates" / ".ai" / "context.md", context_md)
        say("created: ~/.ai/context.md (template — run personalize.py to fill it)")
    else:
        say("ok:      ~/.ai/context.md exists (kept yours)")

    examples_dir = HOME / ".ai" / "examples"
    if not examples_dir.exists():
        if DRY_RUN:
            say(f"[dry-run] copy {REPO_DIR / 'templates' / '.ai' / 'examples'} -> {examples_dir}")
        else:
            shutil.copytree(REPO_DIR / "templates" / ".ai" / "examples", examples_dir)
        say("created: ~/.ai/examples/")

    # 2. Skills ------------------------------------------------------------
    say("")
    say("-- skills --")
    do_mkdir(HOME / ".claude" / "skills")
    do_mkdir(HOME / ".agents")
    for d in sorted((REPO_DIR / "skills").iterdir()):
        if d.is_dir():
            install_copy(d, HOME / ".claude" / "skills" / d.name)
    # cross-tool canonical copy for skills-discovery (Cursor/Codex read ~/.agents)
    install_copy(REPO_DIR / "skills" / "skills-discovery", HOME / ".agents" / "skills-discovery")

    # 3. Discovery system --------------------------------------------------
    say("")
    say("-- discovery (skillfind / rulesfind) --")
    install_copy(REPO_DIR / "discovery" / "skills-catalog", HOME / ".agents" / "skills-catalog")
    bin_dir = HOME / ".local" / "bin"
    do_mkdir(bin_dir)
    install_copy(REPO_DIR / "discovery" / "skills-catalog" / "scripts" / "skillfind", bin_dir / "skillfind")
    install_copy(REPO_DIR / "discovery" / "skills-catalog" / "scripts" / "skillfind", bin_dir / "rulesfind")
    for p in (
        bin_dir / "skillfind",
        bin_dir / "rulesfind",
        HOME / ".agents" / "skills-catalog" / "scripts" / "skillfind",
        HOME / ".agents" / "skills-catalog" / "scripts" / "build-index.py",
    ):
        make_executable(p)

    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    if str(bin_dir) not in path_entries:
        say('NOTE: add to your shell rc:  export PATH="$HOME/.local/bin:$PATH"')

    if not DRY_RUN:
        say("building index...")
        build_index = HOME / ".agents" / "skills-catalog" / "scripts" / "build-index.py"
        result = subprocess.run([sys.executable, str(build_index), "--quiet"])
        if result.returncode != 0:
            say("WARN: index build failed — run: python3 ~/.agents/skills-catalog/scripts/build-index.py")

    # 4. Discovery-guard hook (optional, Claude Code only) -----------------
    say("")
    say("-- discovery-guard hook (optional) --")
    say("Blocks agents from ls/find-ing skill dirs, forcing search-first discovery.")
    if YES:
        install_guard = WITH_GUARD_HOOK
    else:
        try:
            ans = input("Install skills-discovery-guard PreToolUse hook for Claude Code? [y/N] ")
        except EOFError:
            ans = ""
        install_guard = ans.strip().lower().startswith("y")

    if install_guard:
        guard_dst = HOME / ".claude" / "hooks" / "skills-discovery-guard.py"
        install_copy(REPO_DIR / "hooks" / "skills-discovery-guard.py", guard_dst)
        make_executable(guard_dst)
        say("Hook file installed. Register it in ~/.claude/settings.json:")
        say('  "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [ { "type": "command",')
        say('    "command": "python3 ~/.claude/hooks/skills-discovery-guard.py" } ] } ] }')
        say("(installer never edits settings.json for you — merge the snippet manually,")
        say(" full example: docs/hooks.md)")
    else:
        say("skipped guard hook (opt-in only — pass --with-guard-hook with --yes to install non-interactively)")

    # 5. Caveman mode (optional, third-party) -------------------------------
    say("")
    say("-- caveman mode (optional, third-party) --")
    say("Ultra-compressed agent output (~75% fewer tokens). Upstream project:")
    say("  https://github.com/JuliusBrussee/caveman (MIT, by Julius Brussee)")
    say("Install it separately with its own installer:")
    say("  curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh -o /tmp/caveman-install.sh")
    say("  less /tmp/caveman-install.sh   # review first")
    say("  bash /tmp/caveman-install.sh")

    say("")
    say("== done ==")
    say("Everything was COPIED — you can delete this repo clone now.")
    say(f"backups (if any): {BACKUP_DIR}")
    say("update later: git pull && python3 install.py   (re-copies changed files, backs up local edits)")
    say("next: python3 personalize.py   # fill in your machine/stack, toggle output modes")


if __name__ == "__main__":
    main()
