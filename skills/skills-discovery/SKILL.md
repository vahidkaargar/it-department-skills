---
name: skills-discovery
description: MANDATORY SOURCE OF TRUTH for finding skills and rules on this machine — not optional. Use when you need a capability, skill, playbook, or rule and don't know which exists. ALWAYS search with skillfind/rulesfind/the localhost API instead of listing skill directories; a PreToolUse hook (skills-discovery-guard) blocks raw `ls`/`find` enumeration of skill dirs and will deny the tool call. Covers Claude Code, Cursor, Codex, Copilot, and any shell-capable agent.
---

# Skills discovery — source of truth

**Enforced when the opt-in guard hook is installed** (see repo `docs/hooks.md`;
treat search-first as mandatory even without it). The hook
`~/.claude/hooks/skills-discovery-guard.py` runs on every
Bash call (PreToolUse) and denies (`exit 2`) raw enumeration of skill directories —
`ls`/`find`/`tree` against `~/.claude/skills`, `~/.agents`, `~/.cursor/skills`,
`~/.skills-archive`, plugin caches, or bulk `find -name SKILL.md` / glob-cat of many
SKILL.md files. `skillfind`/`rulesfind`/`build-index.py`/`skillserve.py` are
allow-listed by name so the catalog's own tooling still works. This is the STRICT §3
rule (`~/.ai/rules.md`, propagates into `AGENT_RULES.md` + `CLAUDE.md`) — every agent
on this machine must comply, not just Claude Code.

Skills may live across many roots on this machine. NEVER enumerate them into context.
Search first, read ONE SKILL.md.

## Find a skill (any agent with shell access)

```bash
skillfind "<intent>"              # ranked top-5, e.g. skillfind "nginx reload"
skillfind "<intent>" --json       # machine-readable (name, path, score, category)
skillfind --get <name>            # one skill: path + triggers
skillfind --category <slug>       # browse one category
rulesfind "<topic>"               # rules (.md/.mdc); --always = per-session token cost
```

Then: **Read the single SKILL.md path returned. Follow it. Done.**

- Hot set pre-listed (~1k tokens): `~/.agents/skills-catalog/CATALOG.md`
- Machine index: `~/.agents/skills-catalog/index.json` (query via `--json`, don't load whole)
- Archived skills searchable too; restore: `mv ~/.skills-archive/<name> ~/.claude/skills/<name>`

## HTTP API (optional, agents with no shell)

If `skillserve.py` is running (see repo docs for setup), on
`http://127.0.0.1:3401` (bind localhost only):
`/search?q=<intent>&n=5` · `/get?name=<skill>` (returns full SKILL.md body) ·
`/catalog` · `/rules?q=` · `/rules?always=1` · `/health`.

## No shell, no HTTP? (last fallback)

Read `~/.agents/skills-catalog/CATALOG.md` (hot set), or grep
`~/.agents/skills-catalog/index.json` for keywords. Never walk skill dirs.

## Per-tool wiring map

| Tool | Entry point |
|---|---|
| Claude Code (global) | copy installed to `~/.claude/skills/skills-discovery` by install.py + `~/.claude/CLAUDE.md` pointer |
| Cursor (global) | not auto-installed — copy this skill dir to `~/.cursor/skills/` (or point Cursor at the `~/.agents` copy) |
| Cursor (per-repo) | copy `~/.agents/skills-catalog/templates/skills-discovery.mdc` → `<repo>/.cursor/rules/` |
| Codex / Copilot / other | paste `~/.agents/skills-catalog/templates/AGENTS-snippet.md` into repo `AGENTS.md`; cross-tool map in `~/.ai/rules.md` §8 |

## Maintenance

- Index auto-rebuilds when skill dirs change. After editing frontmatter/rules only: `skillfind --rebuild`.
- `CATALOG.md` is generated — never hand-edit. Generator: `~/.agents/skills-catalog/scripts/build-index.py`.
- Installed as copies — edit in the cloned repo and re-run `python3 install.py` to propagate.
