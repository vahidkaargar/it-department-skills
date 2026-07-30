# Architecture / Context — Global Default

This is the global fallback context. Per-project `.ai/context.md` overrides it.

## Machine
<!-- Describe this machine's role, e.g. "MacBook Pro — primary dev machine" -->
- [MACHINE_DESCRIPTION]

## Default stacks on this machine
<!-- List the stacks you use most, e.g. "TypeScript/Node — backend services" -->
- [STACK_1]
- [STACK_2]

## Hard rules (never break)
<!-- Machine-wide constraints agents must never violate, e.g.
     "Never bind internal service ports to 0.0.0.0" -->
- [HARD_RULE_1]

## When starting a new project
Create a project-local `.ai/context.md` with: domain, stack, entry points,
data model, external services, and test/build commands. This global file is the
fallback when no project context exists.
