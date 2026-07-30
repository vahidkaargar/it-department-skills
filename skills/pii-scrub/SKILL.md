---
name: pii-scrub
description: >-
  Redact secrets and PII (API keys, tokens, emails, IPs, private keys, passwords)
  from a file or log before sharing it. Use when asked to scrub, redact, sanitize,
  or "make this safe to paste/share". Writes a .redacted copy and never edits the
  original in place.
disable-model-invocation: true
---

# PII / Secret Scrubber

Produces a redacted copy; the original is untouched. Review before sharing —
no scrubber is perfect.

## Use

```bash
python3 ~/.claude/skills/pii-scrub/scrub.py <file>            # -> <file>.redacted
python3 ~/.claude/skills/pii-scrub/scrub.py <file> --stdout   # print only
cat somefile | python3 ~/.claude/skills/pii-scrub/scrub.py -  # from stdin
```

## What it redacts

- API keys/tokens: `sk-…`, `ghp_…`, `gho_…`, AWS `AKIA…`, Google `AIza…`, Slack `xox…`
- Telegram bot tokens (`123456789:AA…`)
- `Authorization: Bearer …`, `password=…`, `api_key=…`, `token=…`
- Private keys (`-----BEGIN … PRIVATE KEY-----` blocks)
- Emails, IPv4 addresses, JWTs

Each match becomes a typed placeholder like `[REDACTED_AWS_KEY]` so the structure
stays readable. A summary of counts prints to stderr.

## When to reach for it

Before pasting logs into a ticket, chat, or any external service. Pair with
`privacy-audit` when sanitizing exposure reports.
