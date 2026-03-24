---
name: testing
description: Project testing patterns. Activated when the user asks to create tests, test, or check coverage.
allowed tools: Read, Grep, Glob, Write
---

# Testing Patterns

## Structure
[SPEC] Define project test patterns. Example:
- Pattern: `describe` + `it` + AAA (Arrange, Act, Assert)
- Fixtures: factory pattern
- Mocks: [mock framework]
- E2E: [e2e framework]

## Rules
- Every PR needs tests for new code
- Minimum coverage: [SPEC]% (suggestion: 80%)
- Tests must run in < [SPEC] seconds (unit) and < [SPEC] minutes (integration)

## Test strategy
See `docs/specs/testing-strategy/` if the module is active.
