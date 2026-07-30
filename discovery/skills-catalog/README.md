# skills-catalog — token-efficient skill discovery

Problem: once you accumulate hundreds of skills across `~/.agents`,
`~/.claude/skills`, `~/.cursor/skills`, plugins, and `~/.skills-archive`,
loading lists into agent context burns tokens.
Fix: tiny always-on hot catalog + on-demand keyword search; agent reads ONE SKILL.md.

## Layout

```
CATALOG.md            generated quick-ref (hot set only) — never hand-edit
index.json            machine index of all skills, realpath-deduped
rules-index.json      rules (.md/.mdc) incl. always_on flag
scripts/build-index.py    scanner/generator (stdlib python3)
scripts/skillfind         search CLI (also installed as rulesfind — same script, second copy)
scripts/skillserve.py     optional localhost HTTP API (stdlib python3)
```

CLI on PATH: install.sh copies `scripts/skillfind` to `~/.local/bin` under both
names; invoked as `rulesfind` it behaves as `skillfind --rules`.

## Use

```bash
skillfind "<intent>"              # ranked top-5
skillfind "<intent>" --json       # machine-readable
skillfind --get <name>            # one skill: path + triggers
skillfind --category <slug>       # browse category
rulesfind "<topic>"               # rules; --always = always-on rules
skillfind --rebuild               # force index rebuild
```

Index entry shape:

```json
{"name":"example-skill","dir":"example-skill","sources":["claude"],
 "status":"active","category":"engineering","path":"/Users/.../SKILL.md",
 "description":"...","triggers":["..."]}
```

`status`: active | archived. `priority`: hot = shown in CATALOG.md.
Index auto-rebuilds when skill roots change (mtime check on every search).

## Enforcement

`hooks/skills-discovery-guard.sh` (PreToolUse, Claude Code) denies raw
`ls`/`find`/`tree` enumeration of skill dirs — search-first is mandatory,
not advisory. Catalog tooling itself is allow-listed.

## Optional HTTP API

`scripts/skillserve.py` serves the same search on `127.0.0.1:3401`
(`/search /get /catalog /rules /health`) for agents without shell access.
Keep it localhost-only; put nginx in front if you need auth or LAN access.
