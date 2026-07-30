# it-department-skills

[![CI](https://github.com/vahidkaargar/it-department-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/vahidkaargar/it-department-skills/actions/workflows/ci.yml)

Battle-tested global rules, portable skills, and a token-efficient skill-discovery
system for AI coding agents (Claude Code, Cursor, Codex, Copilot — anything with a
shell). Extracted from a production IT/agent stack and sanitized for public use.

Why "ultra performance"? Three levers:

1. **Strict global rules** — one cross-tool ruleset (`rules/AGENT_RULES.md`) with a
   hard done-checklist, security defaults, and research protocol. Agents stop
   guessing and start verifying.
2. **Search-first skill discovery** — once you have hundreds of skills, letting an
   agent `ls` skill directories burns thousands of tokens per session. `skillfind`
   gives ranked top-5 keyword search over an auto-built index; an optional
   PreToolUse hook makes search-first *mandatory* by denying raw enumeration.
3. **Compressed output modes** — Absolute Mode (no filler, no hedging) ships in the
   rules; [caveman](https://github.com/JuliusBrussee/caveman) (third-party,
   optional) compresses agent chat output ~75%.

## Quick start

```bash
git clone https://github.com/vahidkaargar/it-department-skills.git
cd it-department-skills
python3 install.py --dry-run   # see what it would do
python3 install.py             # copies into ~/.ai, ~/.claude, ~/.agents (backs up existing)
python3 personalize.py         # fill in your machine/stack, toggle output modes
```

Installer and personalizer are pure-stdlib Python 3 — no bash/perl/shellcheck
required, so this works identically on macOS, Linux, and Windows (use `python`
instead of `python3` on Windows if that's how it's aliased on your machine).

Then in any agent session:

```bash
skillfind "redact secrets from log"   # -> pii-scrub SKILL.md path
rulesfind "output mode"               # -> absolute-mode spec
```

## What's inside

| Path | What |
|---|---|
| `rules/AGENT_RULES.md` | Cross-tool agent ruleset — priority order, standards, workflow, done-checklist |
| `rules/absolute-mode.md` | Terse output grammar spec (eliminate/preserve lists, precedence) |
| `skills/skills-discovery/` | The mandatory search-first discovery skill (canonical doc) |
| `skills/write-a-skill/` | Author new skills correctly (progressive disclosure, <100-line SKILL.md) |
| `skills/skill-tester/` | Validate + score skill quality |
| `skills/skill-security-auditor/` | Audit third-party skills before installing them |
| `skills/pii-scrub/` | Redact secrets/PII from files before sharing |
| `skills/remember/` | Save durable knowledge to agent memory deliberately |
| `skills/tech-debt-tracker/` | Scan, score, and plan tech-debt remediation |
| `skills/blindspot-check/` | Red-team a big decision against 95 cognitive biases before committing |
| `skills/thiel-style-converter/` | Rewrite arguments in measured Zero-to-One strategic style (anti-fabrication built in) |
| `skills/positioning-with-ekram/` | Product/category positioning operator — diagnose before copy, eval-tested |
| `skills/jscpd/` | Copy-paste detector reference — run jscpd, read its AI-reporter clone output |
| `discovery/skills-catalog/` | `skillfind`/`rulesfind` CLI, index builder, optional localhost HTTP API |
| `hooks/skills-discovery-guard.py` | PreToolUse hook: denies `ls`/`find` on skill dirs (opt-in) |
| `templates/.ai/` | Starter `.ai/context.md` + examples layout for the rules' context protocol |
| `install.py` / `personalize.py` | Idempotent installer (copy + backup) and interactive personalizer — pure stdlib, cross-platform |

This repo also dogfoods its own tooling for contributors (not copied to client
machines by `install.py`):

| Path | What |
|---|---|
| `CLAUDE.md` / `.rtk/filters.toml` | [rtk](https://www.rtk-ai.app/) (Rust Token Killer) instructions + project filters, via `rtk init` |
| `.jscpd.json` | jscpd duplication-check config, enforced in CI (`.github/workflows/ci.yml`) |

## Design principles

- **One source of truth.** Rules live in `~/.ai/rules.md`; every tool (Claude,
  Cursor, Copilot) points at it. Edit once.
- **Search, never enumerate.** Agents read ONE SKILL.md per task, found via
  keyword search over a prebuilt index — not directory listings.
- **Standalone copy installs.** No symlinks — the installer copies everything
  into `~/.ai`, `~/.claude`, `~/.agents`, so it works identically on any fresh
  machine and the clone can be deleted afterwards. Update by `git pull` +
  re-running `python3 install.py` (unchanged files are skipped, local edits backed up).
- **Nothing edits your settings silently.** The guard hook is opt-in and the
  installer prints the settings.json snippet instead of merging it.

## Uninstall

Plain copies — remove them and restore from the printed backup dir:
`~/.it-department-skills-backup/<timestamp>/`. Details: `docs/uninstall.md`.

## Credits

- [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee (MIT) —
  referenced as an optional companion, not vendored.
- `skills/write-a-skill` builds on skill-authoring doctrine by Matt Pocock (MIT).
- `skills/blindspot-check`, `skills/thiel-style-converter`, and
  `skills/positioning-with-ekram` by
  [Soheil Momeni](https://github.com/soheilmomeniii) (MIT) — vendored with
  upstream LICENSE files; security-audited before inclusion.
- `skills/jscpd` usage doc adapted from the [jscpd](https://github.com/kucherenko/jscpd)
  project's own CLI reference (MIT).

## License

MIT — see [LICENSE](LICENSE).
