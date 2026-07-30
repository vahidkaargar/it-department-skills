#!/usr/bin/env python3
"""Build skills + rules index for the skills catalog.

Scans skill sources, dedupes by realpath, assigns categories/triggers,
writes index.json + rules-index.json and regenerates CATALOG.md.

Stdlib only. Run: build-index.py [--quiet]
"""
import json
import os
import re
import sys
import time

HOME = os.path.expanduser("~")
CATALOG_DIR = os.path.join(HOME, ".agents", "skills-catalog")
INDEX_PATH = os.path.join(CATALOG_DIR, "index.json")
RULES_INDEX_PATH = os.path.join(CATALOG_DIR, "rules-index.json")
CATALOG_MD_PATH = os.path.join(CATALOG_DIR, "CATALOG.md")

# scan order = canonical-source preference on realpath collision
SKILL_ROOTS = [
    ("agents", os.path.join(HOME, ".agents"), "active"),
    ("claude", os.path.join(HOME, ".claude", "skills"), "active"),
    ("cursor", os.path.join(HOME, ".cursor", "skills"), "active"),
    ("claude", os.path.join(HOME, ".skills-archive"), "archived"),
    ("plugin", os.path.join(HOME, ".claude", "plugins", "cache"), "active"),
]

RULE_SOURCES = [
    # (path, kind, always_on)  always_on = injected every session
    (os.path.join(HOME, ".claude", "CLAUDE.md"), "claude-global", True),
    (os.path.join(HOME, ".ai", "rules.md"), "cross-tool", True),
    (os.path.join(HOME, ".ai", "context.md"), "cross-tool", False),
    (os.path.join(HOME, ".claude", "absolute-mode.md"), "claude-global", False),
]
RULE_DIRS = [
    # None = read alwaysApply from .mdc frontmatter
    (os.path.join(HOME, ".claude", "rules"), "claude-global", True),
    (os.path.join(HOME, ".cursor", "rules"), "cursor-global", None),
]

STOPWORDS = set("""a an the and or of for to in on with use when this that from your you skill
skills using used it its is are be will can how what into via any all not new file files code
""".split())

# ordered: first match wins. (category-slug, name-prefixes, keywords)
CATEGORY_RULES = [
    ("it-ops", ("it-ops-", "lan-guard", "stack-up"),
     ("ollama", "launchagent", "server ops")),
    ("cursor-meta", ("skills-discovery", "write-a-skill", "skill-tester", "skill-security-auditor", "create-skill",
                     "create-rule", "create-hook", "claude-coach", "remember", "caveman", "hookify"),
     ("author a skill", "skill authoring")),
    ("security-privacy", ("lan-lockdown", "privacy-", "pii-", "red-team", "security-pen",
                          "data-cleanup", "incident-response", "secrets-", "env-secrets"),
     ("penetration", "privacy", "pii", "lockdown", "secrets")),
    ("security-eng", ("ai-security", "cloud-security", "threat-", "detection-engineering",
                      "skill-security", "semgrep", "codeql", "supply-chain", "insecure-defaults"),
     ("vulnerability", "threat detection", "security review", "sarif")),
    ("seo-geo", ("seo", "aeo", "schema-markup", "programmatic-seo", "site-architecture",
                 "analytics-tracking", "app-store-optimization", "google-analytics"),
     ("search engine", "serp", "backlink", "answer engine")),
    ("senior-roles", ("senior-",), ()),
    ("agent-workflow", ("agent", "agenthub", "spawn", "loop", "eval",
                        "cross-eval", "self-eval", "self-improving", "workflow-builder",
                        "autoresearch", "prompt-engineer", "prompt-governance", "llm-",
                        "mcp-server-builder", "context-engine", "company-os"),
     ("multi-agent", "orchestrat", "subagent", "llm pipeline")),
    ("research", ("research", "pulse", "dossier", "brief", "capture", "extract",
                  "knowledge-ops", "decide", "decision-logger", "grill", "challenge",
                  "hard-call", "reflect", "report", "handoff", "resume", "freeze",
                  "promote", "onboard"),
     ("deep research", "summariz")),
    ("atlassian-ms365", ("jira", "confluence", "atlassian", "ms365", "google-workspace", "gcloud"),
     ("jira", "confluence", "sharepoint", "tenant")),
    ("design-content", ("design-system", "md-", "ux-", "apple-hig", "ui-design", "a11y",
                        "markdown-html", "full-page-screenshot", "dev-browser",
                        "browser-automation", "code-tour"),
     ("design system", "wcag", "accessib", "slides")),
    ("data-ml", ("rag-", "sql-", "data-", "database-", "experiment-designer", "firebase",
                 "stripe", "universal-scraping"),
     ("machine learning", "data pipeline", "warehouse", "rag")),
]
FALLBACK_CATEGORY = "engineering"

# explicit hot skills beyond category defaults (kept small: catalog token budget)
HOT_CATEGORIES = {"it-ops", "cursor-meta"}
HOT_EXTRA = {"lan-lockdown", "privacy-audit", "pii-scrub", "data-cleanup", "incident-response"}


def log(msg, quiet=False):
    if not quiet:
        print(msg, file=sys.stderr)


def parse_frontmatter(path):
    """Return (name, description) from SKILL.md frontmatter; tolerant of folded values."""
    name, desc = None, None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read(16384)
    except OSError:
        return None, None
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if m:
        block = m.group(1)
        for key in ("name", "description"):
            km = re.search(rf"^{key}:[ \t]*(.*)$", block, re.MULTILINE)
            if not km:
                continue
            val = km.group(1).strip().strip("\"'")
            if val in (">", "|", ">-", "|-", ""):  # folded/literal block scalar
                lines = []
                start = block.index(km.group(0)) + len(km.group(0))
                for line in block[start:].splitlines():
                    if line.startswith((" ", "\t")):
                        lines.append(line.strip())
                    elif line.strip():
                        break
                val = " ".join(lines)
            if key == "name":
                name = val
            else:
                desc = val
    if not desc:
        body = re.sub(r"\A---.*?---\s*", "", text, flags=re.DOTALL)
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                desc = line
                break
    return name, (desc or "")[:200]


def derive_triggers(name, desc):
    tokens = [t for t in re.split(r"[^a-z0-9]+", name.lower()) if t and t not in STOPWORDS]
    for w in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{3,}", desc.lower()):
        if w not in STOPWORDS and w not in tokens:
            tokens.append(w)
        if len(tokens) >= 8:
            break
    return tokens[:8]


def categorize(name, desc):
    low_name, low_desc = name.lower(), desc.lower()
    for slug, prefixes, keywords in CATEGORY_RULES:
        if any(low_name == p or low_name.startswith(p) for p in prefixes):
            return slug
        if any(k in low_desc for k in keywords):
            return slug
    return FALLBACK_CATEGORY


def find_skill_files(root, max_depth=7):
    """Yield SKILL.md paths under root, skipping junk dirs."""
    skip = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
    base_depth = root.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=True):
        if dirpath.count(os.sep) - base_depth >= max_depth:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in skip]
        if "SKILL.md" in filenames:
            yield os.path.join(dirpath, "SKILL.md")
            # a skill dir is a leaf: never index fixture/sample skills nested
            # under a real skill (e.g. test assets)
            dirnames[:] = []


def plugin_id_from_path(path):
    """cache/<marketplace>/<plugin>/<version>/... -> plugin@marketplace"""
    parts = path.split(os.sep)
    try:
        i = parts.index("cache")
        return f"{parts[i + 2]}@{parts[i + 1]}"
    except (ValueError, IndexError):
        return "unknown"


def build_skills(quiet):
    records = {}  # realpath -> record
    for source, root, status in SKILL_ROOTS:
        if not os.path.isdir(root):
            continue
        count = 0
        for skill_md in find_skill_files(root):
            real = os.path.realpath(skill_md)
            dir_name = os.path.basename(os.path.dirname(skill_md))
            if real in records:
                rec = records[real]
                if source not in rec["sources"]:
                    rec["sources"].append(source)
                continue
            fm_name, desc = parse_frontmatter(real)
            name = (fm_name or dir_name).strip()
            category = categorize(name, desc)
            priority = ("hot" if (category in HOT_CATEGORIES or name in HOT_EXTRA)
                        and source != "plugin" and status == "active"
                        else "cold" if source == "plugin" or status == "archived"
                        else "warm")
            rec = {
                "name": name,
                "dir": dir_name,
                "sources": [source],
                "status": status,
                "category": category,
                "path": real,
                "triggers": derive_triggers(name, desc),
                "desc": desc,
                "priority": priority,
            }
            if source == "plugin":
                rec["plugin"] = plugin_id_from_path(skill_md)
            records[real] = rec
            count += 1
        log(f"  {root}: {count} new skills", quiet)
    return list(records.values())


def rule_desc(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read(4096)
    except OSError:
        return "", None
    always = None
    m = re.match(r"\A---\s*\n(.*?)\n---", text, re.DOTALL)
    if m:
        am = re.search(r"^alwaysApply:\s*(\S+)", m.group(1), re.MULTILINE)
        if am:
            always = am.group(1).lower() == "true"
        dm = re.search(r"^description:\s*(.+)$", m.group(1), re.MULTILINE)
        if dm:
            return dm.group(1).strip().strip("\"'")[:200], always
    for line in re.sub(r"\A---.*?---\s*", "", text, flags=re.DOTALL).splitlines():
        line = line.strip().lstrip("#").strip()
        if line:
            return line[:200], always
    return "", always


def build_rules(quiet):
    rules, seen = [], set()

    def add(path, kind, always_on):
        real = os.path.realpath(path)
        if real in seen or not os.path.isfile(real):
            return
        seen.add(real)
        desc, fm_always = rule_desc(real)
        rules.append({
            "name": os.path.splitext(os.path.basename(path))[0],
            "kind": kind,
            "path": real,
            "always_on": bool(fm_always) if always_on is None else always_on,
            "desc": desc,
        })

    for path, kind, always in RULE_SOURCES:
        add(path, kind, always)
    for dirpath, kind, always in RULE_DIRS:
        if os.path.isdir(dirpath):
            for fn in sorted(os.listdir(dirpath)):
                if fn.endswith((".md", ".mdc")):
                    add(os.path.join(dirpath, fn), kind, always)
    log(f"  rules: {len(rules)}", quiet)
    return rules


CATALOG_HEADER = """<!-- GENERATED by build-index.py — do NOT hand-edit. Edit skill frontmatter or build-index.py, then rebuild. -->
# Skills quick ref

Rule: NEVER load full skill lists into context. Search first, read ONE SKILL.md.

## How

```
skillfind "<intent>"              # ranked top-5 across all sources
skillfind --category <slug>       # browse one category
skillfind --get <name>            # frontmatter + path of one skill
rulesfind "<topic>"               # rules (.md/.mdc); rulesfind --always = always-on rules
```

Archived skills (~/.skills-archive/) and plugin skills are indexed and searchable —
read their SKILL.md by path. Restore an archived skill:
`mv ~/.skills-archive/<name> ~/.claude/skills/<name>`

"""

CATEGORY_TITLES = {
    "it-ops": "IT ops (always relevant on this machine)",
    "cursor-meta": "Skill/rule authoring + meta",
}


def write_catalog(skills, rules):
    hot = [s for s in skills if s["priority"] == "hot"]
    by_cat = {}
    for s in hot:
        by_cat.setdefault(s["category"], []).append(s)
    lines = [CATALOG_HEADER]
    for cat in ("it-ops", "cursor-meta"):
        entries = sorted(by_cat.pop(cat, []), key=lambda s: s["name"])
        if not entries:
            continue
        lines.append(f"## {CATEGORY_TITLES.get(cat, cat)}\n")
        lines.append("| skill | when |")
        lines.append("|---|---|")
        for s in entries:
            lines.append(f"| {s['name']} | {s['desc'][:90]} |")
        lines.append("")
    extra = sorted((s for v in by_cat.values() for s in v), key=lambda s: s["name"])
    if extra:
        lines.append("## Other hot skills\n")
        lines.append("| skill | when |")
        lines.append("|---|---|")
        for s in extra:
            lines.append(f"| {s['name']} | {s['desc'][:90]} |")
        lines.append("")
    counts = {}
    for s in skills:
        counts[s["category"]] = counts.get(s["category"], 0) + 1
    lines.append("## Everything else — search only\n")
    lines.append(", ".join(f"{c} ({n})" for c, n in sorted(counts.items())) + ".")
    lines.append("\nDo not enumerate plugin/archived skills. `skillfind \"<query>\"`.\n")
    always = [r["name"] for r in rules if r["always_on"]]
    if always:
        lines.append(f"Always-on rules (token cost every session): {', '.join(always)}. "
                     "Audit with `rulesfind --always`.")
    with open(CATALOG_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    quiet = "--quiet" in sys.argv
    log("Scanning skills...", quiet)
    skills = build_skills(quiet)
    rules = build_rules(quiet)
    skills.sort(key=lambda s: (s["category"], s["name"]))
    meta = {
        "built_at": time.time(),
        "built_at_human": time.strftime("%Y-%m-%d %H:%M:%S"),
        "counts": {
            "total": len(skills),
            "active": sum(1 for s in skills if s["status"] == "active"),
            "archived": sum(1 for s in skills if s["status"] == "archived"),
            "hot": sum(1 for s in skills if s["priority"] == "hot"),
            "plugin": sum(1 for s in skills if "plugin" in s),
        },
    }
    os.makedirs(CATALOG_DIR, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "skills": skills}, f, indent=1)
    with open(RULES_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump({"meta": {"built_at": meta["built_at"]}, "rules": rules}, f, indent=1)
    write_catalog(skills, rules)
    log(f"Done: {meta['counts']}", quiet)


if __name__ == "__main__":
    main()
