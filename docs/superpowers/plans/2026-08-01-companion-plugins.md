# Recommended Companion Plugins Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Point users at 4 third-party Claude Code plugins (superpowers, ashlr, ecc, claude-mem) that are useful alongside this repo, via a README table and a `personalize.py` print block — no code from those plugins is copied in.

**Architecture:** Two independent, purely-additive content changes: a new README section and a new `personalize.py` print-only step. Neither reads nor writes any file beyond the one it's editing; neither has runtime logic to test beyond "does it run/render."

**Tech Stack:** Markdown (README), stdlib Python 3 (`personalize.py`, unchanged style — `print()` calls only, no new imports, no new functions).

## Global Constraints

- No vendoring: do not copy any plugin's actual `SKILL.md`/source into this repo — link to the upstream GitHub repo only.
- No local install-state detection: do not read `~/.claude/plugins/known_marketplaces.json` or any other Claude Code internal config file.
- No new prompts/interactivity in `personalize.py` for this feature — plain `print()` statements only, matching the existing `-- caveman mode (optional, third-party) --` step's style exactly.
- Exactly these 4 plugins, in this order: superpowers, ashlr, ecc, claude-mem. No others.
- Install commands must be the exact two-step `/plugin marketplace add <owner>/<repo>` then `/plugin install <plugin>@<marketplace>` syntax verified against Claude Code's own docs — do not paraphrase or invent alternate syntax.
- README section goes between the existing `## Uninstall` and `## Credits` headings.
- `personalize.py` section goes immediately after the existing final optional-tooling block, before the closing `print("== done ...")` line.

---

### Task 1: Add "Recommended companion skills" section to README.md

**Files:**
- Modify: `README.md` (insert new `## Recommended companion skills` section between the existing `## Uninstall` heading, ending `docs/uninstall.md`, and the existing `## Credits` heading)

**Interfaces:**
- Consumes: nothing (static content, no code).
- Produces: nothing consumed by Task 2 — the two tasks are fully independent.

- [ ] **Step 1: Insert the new section**

Find this exact existing text in `README.md`:

```markdown
## Uninstall

Plain copies — remove them and restore from the printed backup dir:
`~/.it-department-skills-backup/<timestamp>/`. Details: `docs/uninstall.md`.

## Credits
```

Replace it with (inserting the new section between them, changing nothing else):

```markdown
## Uninstall

Plain copies — remove them and restore from the printed backup dir:
`~/.it-department-skills-backup/<timestamp>/`. Details: `docs/uninstall.md`.

## Recommended companion skills

Not part of this repo, not vendored — third-party Claude Code plugins that
pair well with it. Install commands verified against Claude Code's
[`/plugin` docs](https://code.claude.com/docs/en/discover-plugins.md); the
`@marketplace-name` suffix is whatever that marketplace's own manifest
declares, shown in the `marketplace add` command's own output if it ever
differs from the table below.

| Plugin | What it adds | Install | Source |
|---|---|---|---|
| [superpowers](https://github.com/anthropics/claude-plugins-official) | Brainstorming → TDD → systematic-debugging → writing-plans workflow discipline | `/plugin marketplace add anthropics/claude-plugins-official`<br>`/plugin install superpowers@claude-plugins-official` | `anthropics/claude-plugins-official` |
| [ashlr](https://github.com/ashlrai/ashlr-plugin) | Token-efficient tool wrappers (read/edit/grep/bash) + cost tracking + multi-agent orchestration | `/plugin marketplace add ashlrai/ashlr-plugin`<br>`/plugin install ashlr@ashlr-marketplace` | `ashlrai/ashlr-plugin` |
| [ecc](https://github.com/affaan-m/ECC) | 100+ language/framework reviewers, build-fixers, and workflow commands (React, Go, Rust, Django, Kotlin, etc.) | `/plugin marketplace add affaan-m/ECC`<br>`/plugin install ecc@ecc` | `affaan-m/ECC` |
| [claude-mem](https://github.com/thedotmack/claude-mem) | Persistent cross-session memory — search past work, auto-capture, resume context | `/plugin marketplace add thedotmack/claude-mem`<br>`/plugin install claude-mem@thedotmack` | `thedotmack/claude-mem` |

## Credits
```

- [ ] **Step 2: Verify placement and rendering**

Run: `grep -n "^## " README.md`
Expected: heading order includes `## Uninstall`, then `## Recommended companion skills`, then `## Credits`, in that sequence, with no other heading between them.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "Add recommended companion skills section to README"
```

---

### Task 2: Add companion-plugins step to personalize.py

**Files:**
- Modify: `personalize.py` (insert new print-only block immediately after the existing final optional-tooling block inside `main()`, before the closing `print("== done ...")` line)

**Interfaces:**
- Consumes: nothing (no new constants, no new functions — plain `print()` calls inside `main()`).
- Produces: nothing — terminal task, nothing downstream depends on this.

- [ ] **Step 1: Locate the exact insertion point**

`personalize.py`'s `main()` currently ends with (this is the real, current tail of the file — the rebuild-index step followed by the closing print):

```python
    print("")
    print("-- rebuild index --")
    build_index = HOME / ".agents" / "skills-catalog" / "scripts" / "build-index.py"
    if build_index.is_file():
        subprocess.run([sys.executable, str(build_index), "--quiet"])
    print("== done — open a new agent session to pick up changes ==")
```

- [ ] **Step 2: Insert the new block**

Insert the new block between the `if build_index.is_file(): ...` block and the closing `print("== done ...")` line, so the tail of `main()` becomes:

```python
    print("")
    print("-- rebuild index --")
    build_index = HOME / ".agents" / "skills-catalog" / "scripts" / "build-index.py"
    if build_index.is_file():
        subprocess.run([sys.executable, str(build_index), "--quiet"])

    print("")
    print("-- recommended companion plugins (optional, third-party) --")
    print("Not part of this repo, not vendored — install via Claude Code's own")
    print("/plugin manager if useful to you:")
    print("")
    print("superpowers: brainstorming -> TDD -> systematic-debugging -> writing-plans workflow")
    print("  /plugin marketplace add anthropics/claude-plugins-official")
    print("  /plugin install superpowers@claude-plugins-official")
    print("")
    print("ashlr: token-efficient read/edit/grep/bash wrappers + cost tracking")
    print("  /plugin marketplace add ashlrai/ashlr-plugin")
    print("  /plugin install ashlr@ashlr-marketplace")
    print("")
    print("ecc: 100+ language/framework reviewers, build-fixers, workflow commands")
    print("  /plugin marketplace add affaan-m/ECC")
    print("  /plugin install ecc@ecc")
    print("")
    print("claude-mem: persistent cross-session memory (search past work, auto-capture)")
    print("  /plugin marketplace add thedotmack/claude-mem")
    print("  /plugin install claude-mem@thedotmack")

    print("== done — open a new agent session to pick up changes ==")
```

(The `print("== done ...")` line moves down but its text is unchanged — do not duplicate it.)

- [ ] **Step 3: Syntax-check**

Run: `python3 -m py_compile personalize.py`
Expected: no output, exit code 0.

- [ ] **Step 4: Lint**

Run: `ruff check personalize.py`
Expected: no violations (matches CI's "Python lint (ruff)" step).

- [ ] **Step 5: End-to-end smoke test**

Run (in a scratch dir, mirroring the guard-hook toggle test done earlier this session):

```bash
FAKE_HOME=$(mktemp -d)
python3 install.py --yes --home "$FAKE_HOME"
printf 'y\ny\ny\ny\ny\ny\ny\ny\n' | HOME="$FAKE_HOME" python3 personalize.py
```

Expected: output includes a `-- recommended companion plugins (optional, third-party) --` block listing all 4 plugins, appearing after the rebuild-index step and before `== done ==`, with no traceback and exit code 0. Leave `$FAKE_HOME` in place afterward (OS temp dir, self-cleaning) rather than force-deleting it — matches this session's established handling of destructive cleanup commands.

- [ ] **Step 6: Commit**

```bash
git add personalize.py
git commit -m "Add recommended companion plugins step to personalize.py"
```

---

## Post-plan verification (not a subagent task — run after both tasks land)

- [ ] `git log --oneline -5` shows both commits.
- [ ] `git push` (ask user first, per this session's standing pattern of confirming pushes).
- [ ] Re-render README on GitHub (or locally) to confirm the table renders correctly with `<br>` line breaks inside cells.
