#!/usr/bin/env python3
"""it-department-skills personalizer.

Interactive: fills the [PLACEHOLDER] slots in your installed rules/context
and toggles output modes. Safe to re-run.

Cross-platform (macOS/Linux/Windows) — pure stdlib, no bash/perl.
"""
import shutil
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
HOME = Path.home()
CONTEXT = HOME / ".ai" / "context.md"
RULES = HOME / ".ai" / "rules.md"
AGENT_RULES_COPY = HOME / ".claude" / "AGENT_RULES.md"
CLAUDE_MD = HOME / ".claude" / "CLAUDE.md"
GUARD_HOOK_SRC = REPO_DIR / "hooks" / "skills-discovery-guard.py"
GUARD_HOOK_DST = HOME / ".claude" / "hooks" / "skills-discovery-guard.py"


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        ans = input(f"{prompt}{suffix}: ")
    except EOFError:
        ans = ""
    return ans.strip() or default


def fill(path: Path, placeholder: str, value: str):
    if not value:
        return
    text = path.read_text()
    path.write_text(text.replace(placeholder, value))


def remove_lines_containing(path: Path, needle: str):
    lines = path.read_text().splitlines(keepends=True)
    path.write_text("".join(line for line in lines if needle not in line))


def replace_in_files(files, old: str, new: str):
    for f in files:
        if f.is_file():
            text = f.read_text()
            if old in text:
                f.write_text(text.replace(old, new))


def main():
    print("== personalize it-department-skills ==")

    if not CONTEXT.is_file():
        print(f"ERROR: {CONTEXT} not found — run python3 install.py first", file=sys.stderr)
        sys.exit(1)

    context_text = CONTEXT.read_text()
    if "[MACHINE_DESCRIPTION]" in context_text:
        print("")
        print("-- machine context (~/.ai/context.md) --")
        machine = ask('Describe this machine (e.g. "MacBook Pro — primary dev machine")')
        stack1 = ask('Primary stack (e.g. "TypeScript/Node — backend services")')
        stack2 = ask("Secondary stack (blank to remove line)")
        rule1 = ask("One hard rule agents must never break (blank to remove line)")
        fill(CONTEXT, "[MACHINE_DESCRIPTION]", machine)
        fill(CONTEXT, "[STACK_1]", stack1)
        if stack2:
            fill(CONTEXT, "[STACK_2]", stack2)
        else:
            remove_lines_containing(CONTEXT, "[STACK_2]")
        if rule1:
            fill(CONTEXT, "[HARD_RULE_1]", rule1)
        else:
            remove_lines_containing(CONTEXT, "[HARD_RULE_1]")
        print(f"updated: {CONTEXT}")
    else:
        print(f"context already personalized (no placeholders left) — edit {CONTEXT} directly")

    print("")
    print("-- output modes --")
    print("Absolute Mode: terse, no filler/hedging (spec: ~/.claude/absolute-mode.md)")
    am = ask("Enable Absolute Mode by default in rules? (y/n)", "y")
    rule_files = (RULES, AGENT_RULES_COPY)
    if am.lower().startswith("y"):
        replace_in_files(
            rule_files,
            'Absolute Mode OFF by default (enable per-session: say "absolute mode")',
            "Absolute Mode ACTIVE by default",
        )
        print('Absolute Mode default: on (toggle per-session with "normal mode")')
    else:
        replace_in_files(
            rule_files,
            "Absolute Mode ACTIVE by default",
            'Absolute Mode OFF by default (enable per-session: say "absolute mode")',
        )
        print("Absolute Mode default: off (re-run personalize.py to re-enable)")

    print("")
    print("-- CLAUDE.md pointer --")
    snippet = "@AGENT_RULES.md"
    if CLAUDE_MD.is_file() and snippet in CLAUDE_MD.read_text():
        print(f"ok: {CLAUDE_MD} already imports AGENT_RULES.md")
    else:
        add = ask(f"Append '@AGENT_RULES.md' import to {CLAUDE_MD}? (y/n)", "y")
        if add.lower() == "y":
            CLAUDE_MD.parent.mkdir(parents=True, exist_ok=True)
            with CLAUDE_MD.open("a") as fh:
                fh.write("\n# Global agent rules (it-department-skills)\n")
                fh.write(f"{snippet}\n")
            print(f"updated: {CLAUDE_MD}")

    print("")
    print("-- discovery-guard hook (optional) --")
    print("Blocks agents from ls/find-ing skill dirs, forcing search-first discovery")
    print("via skillfind. Off by default — this only toggles the hook FILE; you still")
    print("register/remove it yourself in ~/.claude/settings.json (see docs/hooks.md).")
    currently_installed = GUARD_HOOK_DST.is_file()
    guard = ask(
        "Install/keep the skills-discovery-guard hook file? (y/n)",
        "y" if currently_installed else "n",
    )
    if guard.lower().startswith("y"):
        if not GUARD_HOOK_SRC.is_file():
            print(f"WARN: {GUARD_HOOK_SRC} not found — run this from inside the cloned repo")
        else:
            GUARD_HOOK_DST.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(GUARD_HOOK_SRC, GUARD_HOOK_DST)
            try:
                GUARD_HOOK_DST.chmod(GUARD_HOOK_DST.stat().st_mode | 0o111)
            except OSError:
                pass
            print(f"installed: {GUARD_HOOK_DST}")
            print("Register it in ~/.claude/settings.json (merge into hooks.PreToolUse):")
            print('  "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [ { "type": "command",')
            print('    "command": "python3 ~/.claude/hooks/skills-discovery-guard.py" } ] } ] }')
    elif currently_installed:
        GUARD_HOOK_DST.unlink()
        print(f"removed: {GUARD_HOOK_DST}")
        print("Remove its entry from ~/.claude/settings.json too if you registered one.")
    else:
        print("skipped — hook not installed")

    print("")
    print("-- rtk token-optimizer (optional) --")
    rtk = shutil.which("rtk")
    if rtk:
        try:
            version = subprocess.run(
                [rtk, "--version"], capture_output=True, text=True, check=False
            ).stdout.strip()
        except OSError:
            version = ""
        print(f"rtk found ({version or 'installed'}). It compacts CLI output")
        print("(git, tests, builds, ...) so agents burn fewer tokens per command.")
        wire_rtk = ask("Wire the rtk hook into your global Claude Code config now? (y/n)", "n")
        if wire_rtk.lower().startswith("y"):
            result = subprocess.run([rtk, "init", "-g", "--auto-patch"])
            if result.returncode != 0:
                print("WARN: rtk init failed — run 'rtk init -g' yourself to see why")
        else:
            print("skipped — run 'rtk init -g' yourself anytime")
    else:
        print("rtk not found on PATH — skipping (install it yourself, then re-run this step with: rtk init -g)")

    print("")
    print("-- rebuild index --")
    build_index = HOME / ".agents" / "skills-catalog" / "scripts" / "build-index.py"
    if build_index.is_file():
        subprocess.run([sys.executable, str(build_index), "--quiet"])

    print("")
    print("-- recommended companion plugins (optional, third-party) --")
    print("Not part of this repo, not vendored — install via Claude Code's own")
    print("/plugin manager if useful to you:")
    print("")
    print("superpowers: brainstorming -> TDD -> systematic-debugging -> writing-plans workflow")
    print("  /plugin marketplace add anthropics/claude-plugins-official")
    print("  /plugin install superpowers@claude-plugins-official")
    print("")
    print("ashlr: token-efficient read/edit/grep/bash wrappers + cost tracking")
    print("  /plugin marketplace add ashlrai/ashlr-plugin")
    print("  /plugin install ashlr@ashlr-marketplace")
    print("")
    print("ecc: 100+ language/framework reviewers, build-fixers, workflow commands")
    print("  /plugin marketplace add affaan-m/ECC")
    print("  /plugin install ecc@ecc")
    print("")
    print("claude-mem: persistent cross-session memory (search past work, auto-capture)")
    print("  /plugin marketplace add thedotmack/claude-mem")
    print("  /plugin install claude-mem@thedotmack")

    print("== done — open a new agent session to pick up changes ==")


if __name__ == "__main__":
    main()
