# Hooks

## skills-discovery-guard (opt-in)

PreToolUse hook for Claude Code. Denies (`exit 2`) Bash commands that enumerate
skill directories (`ls`/`find`/`tree` on `~/.claude/skills`, `~/.agents`,
`~/.cursor/skills`, `~/.skills-archive`, plugin caches), forcing agents through
`skillfind`/`rulesfind` instead. Catalog tooling is allow-listed.

`install.sh` copies the hook file; register it yourself in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/hooks/skills-discovery-guard.sh" }
        ]
      }
    ]
  }
}
```

Merge into your existing `hooks.PreToolUse` array if you already have one.
Remove the entry (and the file) to disable.
