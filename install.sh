#!/usr/bin/env bash
# it-department-skills installer
# Installs: global agent rules, portable skills, skill-discovery system (skillfind/rulesfind),
# optional discovery-guard hook, optional caveman mode (upstream plugin).
# Idempotent. Backs up anything it would overwrite. --dry-run supported.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=0
YES=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --yes|-y)  YES=1 ;;
    --help|-h)
      echo "usage: install.sh [--dry-run] [--yes]"
      echo "  --dry-run   print actions without changing anything"
      echo "  --yes       skip confirmation prompts (guard hook + caveman still ask)"
      exit 0 ;;
  esac
done

BACKUP_DIR="$HOME/.it-department-skills-backup/$(date +%Y%m%d-%H%M%S)"
say()  { printf '%s\n' "$*"; }
run()  { if [ "$DRY_RUN" = 1 ]; then say "[dry-run] $*"; else "$@"; fi; }

backup() {
  # backup <path> — move existing file/dir aside before overwrite
  local p="$1"
  if [ -e "$p" ] && [ ! -L "$p" ]; then
    run mkdir -p "$BACKUP_DIR"
    say "backup: $p -> $BACKUP_DIR/"
    run cp -R "$p" "$BACKUP_DIR/"
  fi
}

link_or_copy() {
  # symlink from repo so `git pull` updates in place
  local src="$1" dst="$2"
  run mkdir -p "$(dirname "$dst")"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    say "ok:     $dst (already linked)"
    return
  fi
  backup "$dst"
  run rm -rf "$dst"
  run ln -s "$src" "$dst"
  say "linked: $dst -> $src"
}

say "== it-department-skills installer =="
say "repo: $REPO_DIR"
[ "$DRY_RUN" = 1 ] && say "(dry run — nothing will be changed)"

# 1. Rules -------------------------------------------------------------------
say ""
say "-- rules --"
run mkdir -p "$HOME/.ai" "$HOME/.claude"
link_or_copy "$REPO_DIR/rules/AGENT_RULES.md" "$HOME/.ai/rules.md"
link_or_copy "$HOME/.ai/rules.md"            "$HOME/.claude/AGENT_RULES.md"
link_or_copy "$REPO_DIR/rules/absolute-mode.md" "$HOME/.claude/absolute-mode.md"
if [ ! -e "$HOME/.ai/context.md" ]; then
  run cp "$REPO_DIR/templates/.ai/context.md" "$HOME/.ai/context.md"
  say "created: ~/.ai/context.md (template — run personalize.sh to fill it)"
else
  say "ok:     ~/.ai/context.md exists (kept yours)"
fi

# 2. Skills ------------------------------------------------------------------
say ""
say "-- skills --"
run mkdir -p "$HOME/.claude/skills" "$HOME/.agents"
for d in "$REPO_DIR"/skills/*/; do
  name="$(basename "$d")"
  link_or_copy "${d%/}" "$HOME/.claude/skills/$name"
done
# canonical home for skills-discovery is ~/.agents (cross-tool), Claude gets symlink
link_or_copy "$REPO_DIR/skills/skills-discovery" "$HOME/.agents/skills-discovery"

# 3. Discovery system --------------------------------------------------------
say ""
say "-- discovery (skillfind / rulesfind) --"
link_or_copy "$REPO_DIR/discovery/skills-catalog" "$HOME/.agents/skills-catalog"
BIN_DIR="$HOME/.local/bin"
run mkdir -p "$BIN_DIR"
link_or_copy "$HOME/.agents/skills-catalog/scripts/skillfind" "$BIN_DIR/skillfind"
link_or_copy "$HOME/.agents/skills-catalog/scripts/skillfind" "$BIN_DIR/rulesfind"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) say "NOTE: add to your shell rc:  export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac
if [ "$DRY_RUN" = 0 ]; then
  say "building index..."
  python3 "$HOME/.agents/skills-catalog/scripts/build-index.py" --quiet || \
    say "WARN: index build failed — run: python3 ~/.agents/skills-catalog/scripts/build-index.py"
fi

# 4. Discovery-guard hook (optional, Claude Code only) -----------------------
say ""
say "-- discovery-guard hook (optional) --"
say "Blocks agents from ls/find-ing skill dirs, forcing search-first discovery."
install_guard=n
if [ "$YES" = 1 ]; then install_guard=y; else
  read -r -p "Install skills-discovery-guard PreToolUse hook for Claude Code? [y/N] " install_guard || true
fi
if [ "${install_guard:-n}" = y ]; then
  run mkdir -p "$HOME/.claude/hooks"
  link_or_copy "$REPO_DIR/hooks/skills-discovery-guard.sh" "$HOME/.claude/hooks/skills-discovery-guard.sh"
  say "Hook file installed. Register it in ~/.claude/settings.json:"
  say '  "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [ { "type": "command",'
  say '    "command": "bash ~/.claude/hooks/skills-discovery-guard.sh" } ] } ] }'
  say "(installer never edits settings.json for you — merge the snippet manually,"
  say " full example: docs/hooks.md)"
else
  say "skipped guard hook"
fi

# 5. Caveman mode (optional, third-party) ------------------------------------
say ""
say "-- caveman mode (optional, third-party) --"
say "Ultra-compressed agent output (~75% fewer tokens). Upstream project:"
say "  https://github.com/JuliusBrussee/caveman (MIT, by Julius Brussee)"
say "Install it separately with its own installer:"
say "  curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh -o /tmp/caveman-install.sh"
say "  less /tmp/caveman-install.sh   # review first"
say "  bash /tmp/caveman-install.sh"

say ""
say "== done =="
say "backups (if any): $BACKUP_DIR"
say "next: ./personalize.sh   # fill in your name, stack, and toggle output modes"
