#!/usr/bin/env bash
# PreToolUse(Bash) guard: block enumerating skill directories directly.
# Rule (AGENT_RULES.md §3 rule 2b, skills-discovery SKILL.md): search via skillfind/rulesfind
# or the localhost API (127.0.0.1:3401, if skillserve.py is running), never
# `ls`/`find`/bulk-`cat` the skill roots.
#
# Protocol: read PreToolUse JSON on stdin. exit 2 = block (stderr → Claude),
# exit 0 = allow.

input="$(cat)"
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"
elif command -v python3 >/dev/null 2>&1; then
  cmd="$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)"
else
  # fail open, but say so once — never fail silently
  echo "skills-discovery-guard: neither jq nor python3 found — guard inactive" >&2
  exit 0
fi

[ -z "$cmd" ] && exit 0

norm="$(printf '%s' "$cmd" | tr -s '[:space:]' ' ')"

# Allow the catalog's own tooling to walk these dirs (skillfind, build-index.py, skillserve.py).
if printf '%s' "$norm" | grep -Eq 'skillfind|rulesfind|build-index\.py|skillserve\.py|skills-catalog/scripts'; then
  exit 0
fi

block() {
  echo "BLOCKED by skills-discovery-guard: $1" >&2
  echo "Rule: never enumerate skill directories. Use:" >&2
  echo "  skillfind \"<intent>\" / rulesfind \"<topic>\"   (CLI)" >&2
  echo "  curl http://127.0.0.1:3401/search?q=<intent>   (HTTP API, if skillserve.py is running)" >&2
  echo "Truth: ~/.agents/skills-discovery/SKILL.md" >&2
  exit 2
}

# Skill root directories this rule protects (macOS /Users, Linux /home, root).
roots='(~/\.claude/skills|~/\.agents|~/\.cursor/skills|~/\.skills-archive|\$HOME/\.claude/skills|\$HOME/\.agents|\$HOME/\.cursor/skills|\$HOME/\.skills-archive|/Users/[a-zA-Z0-9_.-]+/\.claude/skills|/Users/[a-zA-Z0-9_.-]+/\.agents|/Users/[a-zA-Z0-9_.-]+/\.cursor/skills|/Users/[a-zA-Z0-9_.-]+/\.skills-archive|/home/[a-zA-Z0-9_.-]+/\.claude/skills|/home/[a-zA-Z0-9_.-]+/\.agents|/home/[a-zA-Z0-9_.-]+/\.cursor/skills|/home/[a-zA-Z0-9_.-]+/\.skills-archive|/root/\.claude/skills|/root/\.agents|/root/\.cursor/skills|/root/\.skills-archive|\.claude/plugins/(cache|marketplaces))'

# ls / find / tree directly against a skill root (bare or with flags), not a single named skill subdir.
if printf '%s' "$norm" | grep -Eiq "^(ls|find|tree)( +-[a-zA-Z]+)* +${roots}(/)?( |\$)"; then
  block "lists a skill root directory ($cmd)"
fi

# find ... -name SKILL.md style bulk discovery anywhere.
if printf '%s' "$norm" | grep -Eiq -- '-name +.?SKILL\.md.?'; then
  block "bulk-searches for SKILL.md files"
fi

# cat/head/grep -r globbing many SKILL.md at once (e.g. cat ~/.claude/skills/*/SKILL.md).
if printf '%s' "$norm" | grep -Eiq '(cat|head|grep) .*skills/\*/SKILL\.md'; then
  block "bulk-reads multiple SKILL.md files via glob"
fi

exit 0
