#!/usr/bin/env python3
"""PreToolUse(Bash) guard: block enumerating skill directories directly.

Rule (AGENT_RULES.md §3 rule 2b, skills-discovery SKILL.md): search via
skillfind/rulesfind or the localhost API (127.0.0.1:3401, if skillserve.py is
running), never `ls`/`find`/bulk-`cat` the skill roots.

Protocol: read PreToolUse JSON on stdin. exit 2 = block (stderr -> Claude),
exit 0 = allow.

Cross-platform (macOS/Linux/Windows) — pure stdlib, no jq/bash required.
"""
import json
import re
import sys

# Skill root directories this rule protects (macOS /Users, Linux /home, root).
ROOTS = (
    r"(~/\.claude/skills|~/\.agents|~/\.cursor/skills|~/\.skills-archive|"
    r"\$HOME/\.claude/skills|\$HOME/\.agents|\$HOME/\.cursor/skills|\$HOME/\.skills-archive|"
    r"/Users/[a-zA-Z0-9_.-]+/\.claude/skills|/Users/[a-zA-Z0-9_.-]+/\.agents|"
    r"/Users/[a-zA-Z0-9_.-]+/\.cursor/skills|/Users/[a-zA-Z0-9_.-]+/\.skills-archive|"
    r"/home/[a-zA-Z0-9_.-]+/\.claude/skills|/home/[a-zA-Z0-9_.-]+/\.agents|"
    r"/home/[a-zA-Z0-9_.-]+/\.cursor/skills|/home/[a-zA-Z0-9_.-]+/\.skills-archive|"
    r"/root/\.claude/skills|/root/\.agents|/root/\.cursor/skills|/root/\.skills-archive|"
    r"\.claude/plugins/(cache|marketplaces))"
)
LIST_ROOT_RE = re.compile(rf"^(ls|find|tree)( +-[a-zA-Z]+)* +{ROOTS}(/)?( |$)", re.IGNORECASE)
BULK_FIND_RE = re.compile(r"-name +.?SKILL\.md.?", re.IGNORECASE)
GLOB_CAT_RE = re.compile(r"(cat|head|grep) .*skills/\*/SKILL\.md", re.IGNORECASE)
ALLOWLIST_RE = re.compile(r"skillfind|rulesfind|build-index\.py|skillserve\.py|skills-catalog/scripts")


def block(reason: str, cmd: str):
    print(f"BLOCKED by skills-discovery-guard: {reason}", file=sys.stderr)
    print("Rule: never enumerate skill directories. Use:", file=sys.stderr)
    print('  skillfind "<intent>" / rulesfind "<topic>"   (CLI)', file=sys.stderr)
    print("  curl http://127.0.0.1:3401/search?q=<intent>   (HTTP API, if skillserve.py is running)", file=sys.stderr)
    print("Truth: ~/.agents/skills-discovery/SKILL.md", file=sys.stderr)
    sys.exit(2)


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        data = {}

    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not cmd:
        sys.exit(0)

    norm = re.sub(r"\s+", " ", cmd).strip()

    # Allow the catalog's own tooling to walk these dirs (skillfind, build-index.py, skillserve.py).
    if ALLOWLIST_RE.search(norm):
        sys.exit(0)

    # ls / find / tree directly against a skill root (bare or with flags), not a single named skill subdir.
    if LIST_ROOT_RE.search(norm):
        block(f"lists a skill root directory ({cmd})", cmd)

    # find ... -name SKILL.md style bulk discovery anywhere.
    if BULK_FIND_RE.search(norm):
        block("bulk-searches for SKILL.md files", cmd)

    # cat/head/grep -r globbing many SKILL.md at once (e.g. cat ~/.claude/skills/*/SKILL.md).
    if GLOB_CAT_RE.search(norm):
        block("bulk-reads multiple SKILL.md files via glob", cmd)

    sys.exit(0)


if __name__ == "__main__":
    main()
