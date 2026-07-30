# Uninstall

Everything is symlinked from the repo, so removal is deleting links and
restoring backups.

```bash
# remove symlinks (only if they point into this repo)
for p in ~/.ai/rules.md ~/.claude/AGENT_RULES.md ~/.claude/absolute-mode.md \
         ~/.agents/skills-catalog ~/.agents/skills-discovery \
         ~/.local/bin/skillfind ~/.local/bin/rulesfind \
         ~/.claude/hooks/skills-discovery-guard.sh; do
  [ -L "$p" ] && rm "$p"
done
# per-skill links
for d in ~/.claude/skills/*; do [ -L "$d" ] && rm "$d"; done
```

Restore anything the installer backed up from
`~/.it-department-skills-backup/<timestamp>/`, remove the `@AGENT_RULES.md`
line from `~/.claude/CLAUDE.md` if personalize.sh added it, and unregister the
hook from `~/.claude/settings.json` if you enabled it.
