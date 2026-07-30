# Contributing

- New skills: follow `skills/write-a-skill` (SKILL.md under ~100 lines, frontmatter
  with `name` + trigger-rich `description`, progressive disclosure via bundled files).
- Run `skills/skill-tester` on your skill before opening a PR.
- No machine-specific paths, hostnames, emails, or secrets — CI (`.github/workflows/ci.yml`)
  and reviewers will reject anything matching common secret/PII patterns (see `skills/pii-scrub`).
- Rules changes (`rules/AGENT_RULES.md`): keep it lean; long examples go to
  `templates/.ai/examples/` and are referenced by path.
- Installer/personalizer/hook scripts are Python 3, stdlib-only, and must run
  unmodified on macOS, Linux, and Windows — no `os.system`/shell-outs for
  filesystem work, use `pathlib`/`shutil` instead. Must pass `python3 -m py_compile`.
