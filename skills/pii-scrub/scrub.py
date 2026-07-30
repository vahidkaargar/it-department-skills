#!/usr/bin/env python3
"""Redact secrets and PII from a file/stdin. Writes <file>.redacted by default.

Usage:
    scrub.py <file>            -> writes <file>.redacted
    scrub.py <file> --stdout   -> prints redacted text
    scrub.py -                 -> reads stdin, prints redacted text

No external dependencies. Conservative: prefers over-redacting to leaking.
"""
from __future__ import annotations

import re
import sys
from collections import Counter

# Order matters: most specific first. Each entry is (label, compiled_regex).
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("PRIVATE_KEY", re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL)),
    ("AWS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GOOGLE_KEY", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("GITHUB_TOKEN", re.compile(r"\bgh[posru]_[0-9A-Za-z]{36,}\b")),
    ("SLACK_TOKEN", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("OPENAI_KEY", re.compile(r"\bsk-[0-9A-Za-z_\-]{20,}\b")),
    ("TELEGRAM_TOKEN", re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b")),
    ("BEARER", re.compile(r"(?i)\b(authorization:\s*bearer)\s+\S+")),
    ("SECRET_ASSIGN", re.compile(
        r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|token|access[_-]?key)\b"
        r"(\s*[:=]\s*)(\"[^\"]+\"|'[^']+'|\S+)")),
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    ("IPV4", re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
]

# Keep harmless localhost / private-range markers readable (skip redaction).
IP_KEEP = re.compile(r"^(127\.0\.0\.1|0\.0\.0\.0|255\.|::1)")


def redact(text: str) -> tuple[str, Counter]:
    counts: Counter = Counter()

    def sub_simple(label, m):
        counts[label] += 1
        return f"[REDACTED_{label}]"

    for label, rx in PATTERNS:
        if label == "IPV4":
            def _ip(m):
                if IP_KEEP.match(m.group(0)):
                    return m.group(0)
                counts[label] += 1
                return "[REDACTED_IPV4]"
            text = rx.sub(_ip, text)
        elif label == "BEARER":
            def _b(m):
                counts[label] += 1
                return f"{m.group(1)} [REDACTED_TOKEN]"
            text = rx.sub(_b, text)
        elif label == "SECRET_ASSIGN":
            def _s(m):
                counts[label] += 1
                return f"{m.group(1)}{m.group(2)}[REDACTED_{m.group(1).upper()}]"
            text = rx.sub(_s, text)
        else:
            text = rx.sub(lambda m, l=label: sub_simple(l, m), text)
    return text, counts


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    to_stdout = "--stdout" in args
    args = [a for a in args if a != "--stdout"]
    src = args[0]

    if src == "-":
        raw = sys.stdin.read()
        out, counts = redact(raw)
        sys.stdout.write(out)
    else:
        with open(src, encoding="utf-8", errors="replace") as f:
            raw = f.read()
        out, counts = redact(raw)
        if to_stdout:
            sys.stdout.write(out)
        else:
            dst = src + ".redacted"
            with open(dst, "w", encoding="utf-8") as f:
                f.write(out)
            print(f"wrote {dst}", file=sys.stderr)

    total = sum(counts.values())
    summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "none"
    print(f"redactions: {total} ({summary})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
