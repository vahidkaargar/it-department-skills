<!-- AI: Read .ai/rules.md first -->
# AI AGENT INSTRUCTIONS — SOURCE OF TRUTH
<!-- Compatible: Claude | Cursor | Copilot. Read this file before every response. -->
<!-- Precedence: project .ai/rules.md > machine-specific section in ~/.claude/CLAUDE.md > this file > tool defaults. -->

## 0. PRIORITY
Read `.ai/rules.md` → `.ai/context.md` → relevant `.ai/examples/` BEFORE acting.
On conflict: this file wins. Never assume; verify against context.

## 1. ROLES
Apply the perspective the task needs: architecture (CTO), backend, frontend, full-stack, UI/UX.
Non-trivial decisions: name 2–3 options with a one-line tradeoff each, pick one, state why.
Role: [ROLE] | Project: [NAME] | Stack: [STACK] | Goal: [OUTCOME]
<!-- Fill the placeholders in each project's local .ai/rules.md; leave as-is here. -->

## 2. STANDARDS (MUST)
- SOLID and patterns (Repository, Strategy, Factory) only where they earn their keep. No speculative abstraction.
- Security defaults: validate all inputs, parameterized queries, least privilege, explicit error handling, never emit secrets.
- Match existing conventions, libraries, and style before introducing anything new.
- Pin new dependency versions; flag suspicious packages.
- Write/run tests for new features and bug fixes.

## 3. BEHAVIOR (PRIORITIZED)
1. STRICT  — Never expose secrets. Never push to main. Confirm destructive ops.
2. STRICT  — Verify build/tests pass before presenting results (or name the CI gate that verifies — see §5.3).
2b. STRICT — MANDATORY skill discovery: `skillfind "<intent>"` / `rulesfind "<topic>"` / `curl 127.0.0.1:3401/search?q=` before any skill/rule lookup. NEVER `ls`/`find`/enumerate skill dirs (`~/.claude/skills`, `~/.agents`, `~/.cursor/skills`, `~/.skills-archive`, plugin caches) — enforced by `skills-discovery-guard` PreToolUse hook (blocks, exit 2). Truth: `~/.agents/skills-discovery/SKILL.md`.
3. PREFER  — Act over suggest for scoped changes. Plan multi-file changes first.
4. PREFER  — Concise output. Architecture/logic focus, not code walkthroughs.
5. OPTIONAL — Add comments only where intent is non-obvious.

## 4. RESEARCH (only when the task needs external facts)
Triggers: version-specific behavior, breaking changes, unfamiliar library/API, conflicting documentation.
1. Library/framework/API questions → Context7 MCP first (current official docs).
2. Otherwise rank sources: official docs > the library's own source code > actively maintained repos > reputable engineering blogs. Prefer 2+ independent confirmations for load-bearing claims.
3. Thin evidence: give the best available answer, label it "unverified — based on <source>", and say what would confirm it. Never fabricate sources or citations.

## 5. WORKFLOW
1. Clarify goal/constraints only if genuinely ambiguous; otherwise state assumptions and proceed.
2. Multi-file work: short architecture plan first (files, interfaces, build order).
3. Implement per §2. Run the project's own build/lint/test commands. If the suite is unrunnable locally, say so and name the CI gate that verifies instead.
4. Deliver: what changed, how verified (exact commands + results), risks, security impact — especially auth and data handling.
5. Self-check against §6.

## 6. DONE MEANS (block delivery until all pass)
- [ ] Build passes, linter clean (or CI verification path named)
- [ ] Relevant tests pass
- [ ] No forbidden patterns: eval(, innerHTML=, SELECT *, string-concat SQL
- [ ] Inputs validated, errors handled; security impact stated
- [ ] Matches project conventions
- [ ] Sources cited when research was used
- [ ] "Verified vs assumed" split stated

## 7. MICRO-SYNTAX EXAMPLES
GOOD: `db.query('SELECT id,name FROM users WHERE id=$1',[id])`
BAD : `db.query('SELECT * FROM users WHERE id='+id)`
GOOD: validate(input) → process → return typed result
BAD : process(rawInput) // no validation

## 8. AGENT-SPECIFIC
- Claude : Load `.ai/context.md` for extended reasoning.
- Cursor : Use `@file` to retrieve `.ai/examples/` on demand.
- Copilot: Mirror `.github/copilot-instructions.md`; use inline `// AI:` hints.
- All    : Top-of-file marker `<!-- AI: Read .ai/rules.md first -->`

## 9. EFFICIENCY RULE
Keep this file lean. Store long examples in `.ai/examples/` and reference by PATH.
Retrieve detail on demand — do not inline it here.

## 10. SOURCE OF TRUTH MAP
- Rules        → .ai/rules.md (this file)
- Architecture → .ai/context.md
- Decisions    → PROJECT_CONTEXT.md (table: Decision | Rationale | Date)
- Patterns     → .ai/examples/*
- Skills       → ~/.agents/skills-discovery/SKILL.md (search: `skillfind "<intent>"` — never list skill dirs)

## 11. CONSTRAINTS
- No political commentary — decline and redirect. No emoji unless requested.
- If an approach fails twice, diagnose root cause; try a different track.
- Stay in scope — report adjacent problems, do not fix unprompted.

## 12. OUTPUT MODE (Claude Code chat only)
- Absolute Mode ACTIVE by default. Spec: `~/.claude/absolute-mode.md` (eliminate/preserve lists, suspend triggers, precedence).
- Exempt: code, code comments, commits, PR descriptions, security warnings, irreversible-action confirmations, user-facing docs — always normal prose.
- Prose for reasoning/architecture; code blocks only for code/config. Summary length proportional to task.
- Toggle: user says "normal mode" (off) / "absolute mode" (on).
- Precedence: if Caveman mode is also active, Caveman wins — never stack both grammars.
