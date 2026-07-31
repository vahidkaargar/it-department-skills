# Recommended companion plugins — design

## Problem

The user wants to surface "best skills and superpowers" installed on their
machine as part of this repo. Their global setup includes several
third-party Claude Code marketplace plugins (superpowers, ashlr, ecc,
claude-mem, others) alongside personal/production skills (mac-mini-*, ashlr
genome, chief-of-staff email ops, etc.).

## Scope decisions (from brainstorming)

- **Source**: third-party plugins only. Personal/production skills are
  out of scope — several are infra-specific (mac-mini-nginx,
  mac-mini-firewall, ...) and this repo is public + already listed on
  skills.sh, so those stay private.
- **Integration style**: link to upstream, matching the existing `caveman`
  precedent in `install.py` (README §"Why ultra performance", `install.py`
  step 5). No vendoring — copying another maintainer's `SKILL.md` files into
  this public repo would require per-plugin license verification and would
  drift from upstream. A pointer + install command has neither problem.
- **Which plugins**: superpowers, ashlr, ecc, claude-mem (user-selected from
  what's actually installed on this machine).
- **Detection depth**: static text only, no local install-state detection.
  Detection would mean reading `~/.claude/plugins/known_marketplaces.json`,
  an internal/undocumented Claude Code config file — coupling to it risks
  breaking silently on a future Claude Code update. Matches the existing
  caveman section's style (also static text, no detection).

## Design

### 1. `personalize.py` — new step

New section, same shape/placement pattern as the existing
`-- caveman mode (optional, third-party) --` step (which already prints
info + an install command with no prompt, no file writes): a
`-- recommended companion plugins (optional, third-party) --` block that
prints, for each of the 4 plugins, a one-line description and its two-step
install command. Purely `print()` calls — no prompts, no filesystem writes,
no network calls. Placed directly after the existing caveman section so all
"other things you might want" live together at the end of the script.

### 2. `README.md` — new section

New `## Recommended companion skills` section, placed between the existing
`## Uninstall` and `## Credits` sections (Credits already attributes
caveman as "referenced as an optional companion, not vendored" — this new
section extends that same idea to the 4 plugins, but stays separate from
Credits since Credits is specifically attribution for content actually
included in this repo). Table:

| Plugin | What it adds | Install | Source |
|---|---|---|---|
| superpowers | Brainstorming → TDD → systematic-debugging → writing-plans workflow discipline | `/plugin marketplace add anthropics/claude-plugins-official` then `/plugin install superpowers@claude-plugins-official` | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| ashlr | Token-efficient tool wrappers (read/edit/grep/bash) + cost tracking + multi-agent orchestration | `/plugin marketplace add ashlrai/ashlr-plugin` then `/plugin install ashlr@ashlr-marketplace` | [ashlrai/ashlr-plugin](https://github.com/ashlrai/ashlr-plugin) |
| ecc | 100+ language/framework reviewers, build-fixers, and workflow commands (React, Go, Rust, Django, Kotlin, etc.) | `/plugin marketplace add affaan-m/ECC` then `/plugin install ecc@ecc` | [affaan-m/ECC](https://github.com/affaan-m/ECC) |
| claude-mem | Persistent cross-session memory — search past work, auto-capture, resume context | `/plugin marketplace add thedotmack/claude-mem` then `/plugin install claude-mem@thedotmack` | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) |

A one-line caveat under the table: these are third-party plugins, not
maintained by this repo; install commands verified against Claude Code's
`/plugin` docs (code.claude.com/docs/en/discover-plugins.md) as of this
writing — the `@marketplace-name` suffix is whatever that marketplace's own
manifest declares, shown in the `marketplace add` command's own output if it
ever differs from the table.

## Data flow

None — this is static documentation content. No user data is read, stored,
or transmitted. `personalize.py`'s new step performs no filesystem access
beyond `print()`.

## Error handling

N/A — no I/O, no external calls, nothing that can fail at runtime.

## Testing

Manual: run `python3 personalize.py` end-to-end (as already done for the
guard-hook toggle earlier this session) and confirm the new section prints
without affecting any other step's behavior or exit code. No existing test
in `discovery/skills-catalog/tests/` or CI touches `personalize.py`'s
output, so no regression risk there.

## Out of scope (explicitly, per user's own scoping answers)

- Vendoring any third-party plugin's actual `SKILL.md`/code into this repo.
- Importing personal/production skills (mac-mini-*, ashlr genome, etc.).
- Local install-state detection for the 4 plugins.
- Any plugin beyond the 4 named (ecc, ashlr, claude-mem, superpowers) —
  other namespaces visible on this machine (hookify, pr-review-toolkit,
  static-analysis, etc.) are not part of this pass.
