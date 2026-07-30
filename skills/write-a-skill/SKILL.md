---
name: write-a-skill
description: Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, build, or author a new skill.
license: MIT
metadata:
  derived_from: "https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill"
  original_author: "Matt Pocock (@mattpocock)"
  original_license: MIT
  voice: "Matt Pocock — direct, concrete, imperative, example-driven"
  version: 1.0.0
---

# Writing Skills

> Derived from [Matt Pocock's write-a-skill](https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill) (MIT). Matt's voice and 3-phase workflow preserved verbatim. Additions: validation tools + references + cs-* wrapper (see *Tooling + Companions* below).

## Process

1. **Gather requirements** - ask user about:
   - What task/domain does the skill cover?
   - What specific use cases should it handle?
   - Does it need executable scripts or just instructions?
   - Any reference materials to include?

2. **Draft the skill** - create:
   - SKILL.md with concise instructions
   - Additional reference files if content exceeds 100 lines
   - Utility scripts if deterministic operations needed

3. **Review with user** - present draft and ask:
   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more/less detailed?

## Skill Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── REFERENCE.md       # Detailed docs (if needed)
├── EXAMPLES.md        # Usage examples (if needed)
└── scripts/           # Utility scripts (if needed)
    └── helper.js
```

## SKILL.md Template

Copy-paste starting point: [references/skill_md_template.md](references/skill_md_template.md).

## Description Requirements

The description is **the only thing your agent sees** when deciding which skill to load — see [references/description_design_patterns.md](references/description_design_patterns.md) for the four format rules and good/bad examples.

## When to Add Scripts

Add utility scripts when:

- Operation is deterministic (validation, formatting)
- Same code would be generated repeatedly
- Errors need explicit handling

Scripts save tokens and improve reliability vs generated code.

## When to Split Files

See [references/progressive_disclosure_principles.md](references/progressive_disclosure_principles.md) for the 100-line ceiling, the one-level-deep rule, and anti-patterns to avoid.

## Review Checklist

After drafting, verify:

- [ ] Description includes triggers ("Use when...")
- [ ] SKILL.md under 100 lines
- [ ] No time-sensitive info
- [ ] Consistent terminology
- [ ] Concrete examples included
- [ ] References one level deep

## Tooling + Companions

Validation tools + cs-* wrapper sit alongside this skill. Run all 6 review-checklist items programmatically:

```
python3 ~/.claude/skills/write-a-skill/scripts/skill_review_checklist_runner.py <path-to-skill>
```

See [references/companion_tooling.md](references/companion_tooling.md) for the tool catalogue, cs-skill-author persona agent, and `/cs:write-a-skill` slash command.

**Version:** 1.0.0 — derived from Matt Pocock (MIT) + this repo's wrapper
