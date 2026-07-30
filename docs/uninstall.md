# Uninstall

Everything is installed as plain copies — remove them and restore backups.

```bash
rm -f  ~/.ai/rules.md ~/.claude/AGENT_RULES.md ~/.claude/absolute-mode.md \
       ~/.local/bin/skillfind ~/.local/bin/rulesfind \
       ~/.claude/hooks/skills-discovery-guard.sh
rm -rf ~/.agents/skills-catalog ~/.agents/skills-discovery
# per-skill dirs installed by this repo:
for s in skills-discovery write-a-skill skill-tester skill-security-auditor \
         pii-scrub remember tech-debt-tracker blindspot-check \
         thiel-style-converter positioning-with-ekram; do
  rm -rf ~/.claude/skills/$s
done
# only if you never customized them:
rm -f ~/.ai/context.md; rm -rf ~/.ai/examples
```

Restore anything the installer backed up from
`~/.it-department-skills-backup/<timestamp>/`, remove the `@AGENT_RULES.md`
line from `~/.claude/CLAUDE.md` if personalize.sh added it, and unregister the
hook from `~/.claude/settings.json` if you enabled it.
