---
name: tdd
description: Test-driven development, a red → green loop that writes tests worth keeping. Use when the user wants to build a feature test-first, fix a bug however it was reported (their own words, a BUG_FINDINGS.md entry, a PR review comment, a crash report), or add integration tests.
---

# Test-Driven Development

TDD is the red → green loop. This skill is the reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle: consult them before and during the loop, not after.

**Need a task.** If the user gave no concrete behavior to build, fix or cover (and none is clear from the session), ask once, in plain text, what it should be, and stop. Do not infer a task from the repository. A request to "improve" or "clean up" code with no behavior named is not a task. In a non-interactive run, stop and report that no task was given.

## Explore first

Before choosing seams or writing the first test, read what the project already has:

- The project instructions file (`CLAUDE.md` or `AGENTS.md`, whichever it has), for conventions.
- The existing tests: framework, location, naming, helpers, and how they are run. Follow those patterns. If the project has no tests, use the stack's built-in test runner (for example `go test`, `cargo test`, Python `unittest`, `node:test`). If none exists, don't install anything: ask the user which framework to add (in plain text), or if no answer is possible, stop and report that no runnable test setup exists.
- The code you will change and what depends on it: its public interface, structure, and place in the architecture.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification: "user can checkout with valid cart" tells you exactly what capability exists, and it survives refactors because it doesn't care about internal structure.

See `references/tests.md`, next to this file, for examples.

## Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Choose the seams yourself, and write them down first.** Before writing any test, post the list of seams under test in your reply (a short list in chat, no file), each with a one-line note on what it catches and what it misses. Don't ask the user: pick the seams that cover the critical paths and complex logic, not every edge case. No test is written at a seam that isn't on the list.

If a cycle reveals a new seam, add it to the list with its note before writing a test there.

## Anti-patterns

- **Implementation-coupled**: tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological**: the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth: a known-good literal, a worked example, the spec.
- **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first and run it. It must fail for the reason you expect (the missing behavior or the reported bug), not from a typo or setup error. If it passes at once, don't write code for it: check that the test really exercises the behavior. If it does, the behavior already exists, so keep the test only if it guards behavior worth keeping; if it doesn't, fix the test (for a bug, the reproduction is wrong). Say what happened in the final report. Then write only enough code to pass it and run it again. Don't anticipate future tests or add speculative features.
- **Never claim red or green you did not observe.** If the tests can't be run (no runtime, blocked execution), stop after the seam list: write no implementation code, and say in the final report that nothing was run.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** Don't restructure inside a red → green cycle. If the next test can't pass without restructuring first, drop that red test, restructure as a separate step with the existing tests passing before and after, then restart the cycle with the test, and say so in the final report. If no existing tests cover the code to restructure, stop and report that instead of restructuring untested code.

## Final report

Report, in the shape the user's instructions define if they define one: the final seam list with each note, the tests added grouped by seam, and the test-run result (or that the tests could not be run).
