## Skill discovery — MANDATORY, not advisory

All skills on this machine are indexed. NEVER enumerate skill directories —
on Claude Code this is hard-blocked by a PreToolUse hook (`skills-discovery-guard.py`,
exit 2 on `ls`/`find` against skill roots); treat it as a hard rule regardless of tool.
Need a capability? Search, read ONE SKILL.md, follow it:

```bash
skillfind "<intent>"          # ranked top-5; add --json for machine-readable
rulesfind "<topic>"           # rules; --always = always-on token cost
```

No shell? Read `~/.agents/skills-catalog/CATALOG.md` (hot set, ~1k tokens).
Source of truth: `~/.agents/skills-discovery/SKILL.md`.
