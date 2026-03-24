---
name: implement-prd
description: Implement a feature from a PRD. Activated when the user asks to implement, build, or construct from a product document.
allowed tools: Read, Write, Grep, Glob, Bash
---

# Implement from PRD

## Workflow
1. **Read the PRD** completely in `docs/product/`
2. **Check related ADRs** in `docs/architecture/`
3. **Check applicable specs** in `docs/specs/` (design, compliance, etc.)
4. **Plan Mode** — create implementation plan before coding
5. **Implement** following `CLAUDE.md` conventions
6. **Tests** — create tests following `.claude/skills/testing/SKILL.md`
7. **Spec checks** — verify compliance with active modules
8. **Document** — update docs if needed

## Rules
- Never implement without reading the full PRD first
- If the PRD is ambiguous, ask before assuming
- Always check if an ADR already exists for the technical decision
- Atomic commits per feature/sub-feature
