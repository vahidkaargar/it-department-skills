#!/usr/bin/env bash
# it-department-skills personalizer
# Interactive: fills the [PLACEHOLDER] slots in your installed rules/context
# and toggles output modes. Safe to re-run.
set -euo pipefail

CONTEXT="$HOME/.ai/context.md"
RULES="$HOME/.ai/rules.md"

command -v perl >/dev/null 2>&1 || { echo "ERROR: perl is required (apt/apk/brew install perl)"; exit 1; }

ask() { # ask "<prompt>" <default> -> stdout
  local prompt="$1" def="${2:-}" ans
  read -r -p "$prompt${def:+ [$def]}: " ans || true
  printf '%s' "${ans:-$def}"
}

fill() { # fill <file> <placeholder> <value>
  local f="$1" ph="$2" val="$3"
  [ -z "$val" ] && return 0
  # portable in-place replace (BSD/GNU sed differ; use perl)
  PH="$ph" VAL="$val" perl -pi -e 's/\Q$ENV{PH}\E/$ENV{VAL}/g' "$f"
}

echo "== personalize it-department-skills =="

[ -f "$CONTEXT" ] || { echo "ERROR: $CONTEXT not found — run ./install.sh first"; exit 1; }

if grep -q '\[MACHINE_DESCRIPTION\]' "$CONTEXT"; then
  echo ""
  echo "-- machine context (~/.ai/context.md) --"
  machine="$(ask 'Describe this machine (e.g. "MacBook Pro — primary dev machine")' '')"
  stack1="$(ask 'Primary stack (e.g. "TypeScript/Node — backend services")' '')"
  stack2="$(ask 'Secondary stack (blank to remove line)' '')"
  rule1="$(ask 'One hard rule agents must never break (blank to remove line)' '')"
  fill "$CONTEXT" '[MACHINE_DESCRIPTION]' "$machine"
  fill "$CONTEXT" '[STACK_1]' "$stack1"
  if [ -n "$stack2" ]; then fill "$CONTEXT" '[STACK_2]' "$stack2"
  else perl -ni -e 'print unless /\[STACK_2\]/' "$CONTEXT"; fi
  if [ -n "$rule1" ]; then fill "$CONTEXT" '[HARD_RULE_1]' "$rule1"
  else perl -ni -e 'print unless /\[HARD_RULE_1\]/' "$CONTEXT"; fi
  echo "updated: $CONTEXT"
else
  echo "context already personalized (no placeholders left) — edit $CONTEXT directly"
fi

echo ""
echo "-- output modes --"
echo "Absolute Mode: terse, no filler/hedging (spec: ~/.claude/absolute-mode.md)"
am="$(ask 'Enable Absolute Mode by default in rules? (y/n)' 'y')"
case "$am" in
  [Yy]*)
    for f in "$RULES" "$HOME/.claude/AGENT_RULES.md"; do
      [ -f "$f" ] && perl -pi -e 's/Absolute Mode OFF by default \(enable per-session: say "absolute mode"\)/Absolute Mode ACTIVE by default/' "$f"
    done
    echo "Absolute Mode default: on (toggle per-session with \"normal mode\")" ;;
  *)
    for f in "$RULES" "$HOME/.claude/AGENT_RULES.md"; do
      [ -f "$f" ] && perl -pi -e 's/Absolute Mode ACTIVE by default/Absolute Mode OFF by default (enable per-session: say "absolute mode")/' "$f"
    done
    echo "Absolute Mode default: off (re-run personalize.sh to re-enable)" ;;
esac

echo ""
echo "-- CLAUDE.md pointer --"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
SNIPPET='@AGENT_RULES.md'
if [ -f "$CLAUDE_MD" ] && grep -q '@AGENT_RULES.md' "$CLAUDE_MD"; then
  echo "ok: $CLAUDE_MD already imports AGENT_RULES.md"
else
  add="$(ask "Append '@AGENT_RULES.md' import to $CLAUDE_MD? (y/n)" 'y')"
  if [ "$add" = y ]; then
    { echo ""; echo "# Global agent rules (it-department-skills)"; echo "$SNIPPET"; } >> "$CLAUDE_MD"
    echo "updated: $CLAUDE_MD"
  fi
fi

echo ""
echo "-- rebuild index --"
python3 "$HOME/.agents/skills-catalog/scripts/build-index.py" --quiet || true
echo "== done — open a new agent session to pick up changes =="
