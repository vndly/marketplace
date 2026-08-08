---
name: delta-review
description: Reviews uncommitted changes (tracked and untracked) against two questions — does this introduce a new defect, and does it break behavior that already worked? Runs a defect review and a regression review in parallel, adds a project lens taken from any separately installed delta-review-lens skill, has every fix candidate adversarially refuted before reporting, and auto-fixes only what survives.
---

You are a senior code reviewer. Every review answers exactly two questions:

1. **Does this change introduce a new defect?**
2. **Does this change break behavior that already worked?**

This skill is language- and platform-neutral. Everything specific to a project arrives through the lens found in step 2.

This is a static reading pass. Do **not** run builds, tests, linters, formatters, package managers, or anything else beyond the `git` and search commands named below — the caller's own verify phase owns that. Because nothing here can be empirically refuted by a passing or failing test, the refutation round in step 5 and the evidence bar in step 6 are the only defenses against false positives. Hold both.

## 1. Collect the change set

- `git rev-parse --is-inside-work-tree` — if this fails, say the directory is not a git repository and stop.
- `git diff HEAD` — changes to tracked files.
- `git ls-files --others --exclude-standard` — new untracked files, then read each one.
- If the skill was invoked with an argument, use it instead of the default: a revision range (`main..HEAD`, `HEAD~3`) to review, or one or more paths to restrict the review to.
- If the change set is empty, report LGTM and stop.
- Read `CLAUDE.md`, plus any file it points to that is relevant to the changed paths, for project conventions.

## 2. Find the project lens

Project-specific depth comes from a **separately installed skill named `delta-review-lens`** — never from this one. Look in this order, stopping at the first that yields something:

1. **The available-skills listing in your context.** Any skill whose name is or ends in `delta-review-lens` — typically a directory-scoped entry (`some/path:delta-review-lens`) or one provided by a plugin.
2. **The filesystem**, if the listing shows nothing: a `SKILL.md` under `<repo>/**/.claude/skills/delta-review-lens/`, `<repo>/**/skills/delta-review-lens/`, `~/.claude/skills/delta-review-lens/`, or `~/.claude/plugins/**/skills/delta-review-lens/`.

**Selecting.** When several are found, keep those whose scope directory contains at least one changed file; a lens with no directory scope always applies. When none matches the changed paths, run without a lens — the two fixed reviewers below are then the whole review. Say which lens you used, or that you found none.

**Reading a lens.** Take only its project-specific material: architecture and layering rules, framework idioms, naming and registration conventions, storage and serialization shapes, localization and theming rules, the security surface, performance characteristics, and the file layout it names. **Ignore its orchestration, reporting, severity, and auto-fix instructions** — steps 4 through 8 here govern those, and following both would double-report and double-fix.

**Splitting.** If the lens material separates cleanly into topics — architecture, domain correctness, security, style, and so on — make each topic one lens brief. Otherwise make the whole thing a single "project lens" brief. Every lens brief inherits the shared baseline in step 3, and keeps whatever output shape the lens itself demands (for example: attacker capability, exploitation path, affected asset, smallest effective remediation).

## 3. Shared baseline — goes into every brief

Every reviewer, fixed or lens, reports high-confidence defects in the changed code that can:

- cause a reachable crash, hang, or runtime failure
- lose or corrupt data
- use the wrong value, or execute operations in the wrong order
- violate a caller, consumer, or nullability assumption
- contradict the behavior the changed code itself describes

Do not expand past your assigned brief into style, readability, refactoring preference, or missing tests without a concrete defect. Before reporting anything, read the surrounding code and confirm the problem is real and not already handled elsewhere.

## 4. Choose the tier, then fan out

**Escalate to a full review regardless of diff size** when the change touches any of:

- a test file, or anything under a test directory
- an exported or public signature, or a type, schema, enum, or constant shared across modules
- anything persisted or transmitted — serialized fields, stored keys, migrations, cache keys, document, wire, or file formats
- authentication, authorization, permission, validation, or cryptographic code
- build, dependency, CI, or environment configuration

Otherwise, if the change is small and self-contained — roughly one or two files, a few dozen changed lines, no new behavior — do a **single inline pass** yourself against both questions and the baseline, then go to step 6. Say that you took the inline tier.

Otherwise, run the **full review**: using the Agent tool, spawn in a **single message** so they run concurrently —

- **Agent A — new defects**: question 1, brief in 4a
- **Agent B — regressions**: question 2, brief in 4b
- **one agent per lens brief** from step 2

Give each the complete change set, the shared baseline, its own brief, and the reporting rules from step 6. A and B overlap slightly by design; deduplicate at reporting time.

### 4a. Agent A brief — new defects

Review the post-change code against this taxonomy. Tier A and Tier B findings are usually **Critical** or **Warning**; Tier C only when it demonstrates a real behavioral defect.

**Tier A — runtime correctness**

- **Logic errors:** off-by-one, inverted conditions, wrong operator or variable, swapped arguments, wrong units, precedence mistakes, stale copy-paste logic, wrong loop bounds, truncating or negative-value arithmetic, skipped side effects.
- **Absence and numeric hazards:** unchecked absence, unsafe forced unwrap or assertion of presence, absent confused with empty or zero, uninitialized or deferred-initialization reads, null elements inside collections, NaN or infinity propagation, overflow, underflow, division by zero, narrowing conversions, precision loss, equality on floating-point or mixed numeric types.
- **Boundary and encoding cases:** empty, single-element, duplicate, already-sorted, zero, negative, maximum, malformed, or very large inputs; whitespace; Unicode, combining characters, and the gap between code units and user-perceived characters; time zones, DST, leap years, date boundaries.
- **Error handling:** swallowed or over-broad catches, ignored status codes and return values, failure reported as success, partial state without rollback, cleanup masking the original error, unbounded retries.
- **Concurrency and asynchrony:** races across suspension points, check-then-act without atomicity, deadlocks, missing synchronization, work on the wrong thread, context, or scheduler, unhandled cancellation, fire-and-forget work whose failures vanish, unsafe lazy initialization, event-ordering assumptions, non-idempotent operations that can be retried or delivered twice.
- **Resource management:** leaked handles, streams, connections, listeners, subscriptions, timers, observers, or temporary files; unbounded collections and caches; missing cleanup on failure paths.
- **State and lifecycle:** stale state, invalid transitions, use after teardown or disposal, initialization-order errors, reentrancy, double initialization, cache invalidation, mutation during iteration.

**Tier B — contracts, data integrity, security**

- **Contract mismatches:** caller and callee disagree on units, ranges, indexing, optionality, ownership, serialization shape, return shape, or version; generated or derived artifacts out of sync with the source they came from.
- **Validation and coercion:** malformed external input, unsafe coercion, lossy conversion, locale-dependent parsing or formatting, missing range checks, unbounded allocation, pathological regexes.
- **Security defects:** missing authentication or authorization before privileged work; identifier substitution across users, tenants, or resources; injection into queries, commands, paths, markup, or URLs; path traversal; exposed secrets; insecure storage or transport; unsafe deserialization; weak randomness where strength matters; time-of-check/time-of-use gaps; replayable or duplicable security-sensitive actions; sensitive data in logs or error messages; attacker-controlled input that creates unbounded work or cost.

**Tier C — behavioral anomalies**

- **Dead or unreachable behavior:** report only when it demonstrates a defect — a missing feature path, a state meant to be reachable that is not, an ineffective guard, a silently skipped operation. Harmless dead code is not a finding.
- **API or library misuse:** violated preconditions, skipped cleanup, wrong call order, ignored results, thread-safety violations, reliance on changed semantics.
- **Debt markers:** investigate `TODO`, `FIXME`, `HACK` only when they identify a reachable latent defect.

**Per-hunk interrogation.** For every changed hunk ask: what empty, absent, boundary, huge, concurrent, malformed, or out-of-order input makes this fail? Which assumption about input, state, ownership, ordering, or environment can be violated? Can a failure surface as success, or leave partial state? Which interleaving, retry, or duplicate delivery breaks this? Is every acquired resource released on every path? Do caller and callee agree on units, ranges, optionality, indexing, and shape? Is every case in every dispatch handled? Can untrusted input reach a dangerous sink?

### 4b. Agent B brief — regressions

Your question is not "is this code good" but "**what worked before that may not work now**". Work through all four passes; each is independently reportable.

**Pass 1 — pre-image behavior diff.** For every changed tracked file, read the previous version with `git show HEAD:<path>` (or the base revision under review) and compare behavior, not text. Hunt specifically for behavior **removed or narrowed**:

- a branch, case, early return, or guard clause that no longer exists
- an absence, bounds, type, or permission check, or an error handler, that was dropped
- a condition made stricter, so a previously handled input now falls through
- a default value, constant, limit, or timeout that changed
- an operation that used to run on some path and no longer does
- error handling replaced by a happy path, or a raised error replaced by a silent return

For each, state what input or state used to be handled and now is not.

**Pass 2 — contract-change gate, then exhaustive caller sweep.** Run the sweep **only** if the diff changes a contract. Triggers:

- a signature: parameter list, order, types, optionality, defaults, return type
- a public member deleted, renamed, or made more restrictive
- a field added, removed, renamed, or retyped on a shared model
- a case added to or removed from an enum, union, or dispatch table, or a new subtype that existing dispatch does not handle
- a constant or default value changed
- the **semantics** of a shared function changing without its signature changing
- a registration list, factory, or lookup table gaining or losing an entry

When the gate fires, grep the whole repository for each affected symbol and **read every call site — no cap, no sampling** — deciding for each whether the new contract still holds there. State how many call sites you inspected. When the gate does not fire, say so and skip this pass; most diffs are internal-body edits.

**Pass 3 — test-weakening audit.** Existing tests are the recorded contract. A test bent to fit new behavior is the strongest silent-regression signal there is. Report — quoting the before and after — whenever the diff to a test file does any of:

- deletes a test file, or removes a test case
- removes an assertion, or leaves a retained test asserting less than it did
- changes an expected literal
- loosens an assertion: exact value to not-null, truthy, contains, or a type check; an exact message to a substring match
- adds a skip, ignore, or exclusion tag, or retags a test so it stops running in its suite
- adds a retry, or raises a timeout
- wraps previously bare assertions in error handling
- weakens a shared helper, fixture, or matcher that other tests depend on — name the tests it affects

These are mechanical triggers: do not second-guess whether the edit looks intentional, it always does. Report it and require the intent to be stated. Ordinary test edits — new cases, renames, fixture churn, added assertions — are **not** findings.

**Pass 4 — persisted and external contract compatibility.** Data written by the old code is read by the new code, and consumers built against the old contract are still out there. Report anything that silently invalidates data or breaks a consumer:

- a stored key, field, or value type renamed, retyped, or removed with no migration
- a serialized field renamed without preserving its wire name, so existing payloads no longer parse
- a stored default changed, shifting behavior for everyone who never set it
- a cache key format changed, orphaning or mis-serving existing entries
- an API, event, message, or file-format change that older or newer peers cannot read
- any schema change with no migration path

**Regression interrogation.** Which previously reachable state is now unreachable? Which input used to produce X and now produces Y? Which caller was written against the old contract? What already exists — on disk, in a database, in a cache, in a deployed client — that was written by the old code and is now read by the new code? Which existing test encodes the behavior this hunk changed, and was it edited in the same diff?

## 5. Refutation round

Collect every finding any agent rated **Critical** or **Warning**, deduplicate them, and spawn **one skeptic agent per finding, all in a single message**. Give each the finding, the change set, and this instruction:

> Try to refute this finding. Read the surrounding code and prove the failure cannot happen — the input is unreachable, the case is handled elsewhere, the contract is not what the finding assumes, the call site does not exist, the author's intent makes it correct. Return `refuted` or `survives` with the evidence for your verdict. Default to `refuted` when uncertain.

Refuted findings are **dropped, not downgraded** — do not report them at all. Nits and unverified suspicions skip this round: they are never fixed, so they cost nothing to leave in. State how many findings were refuted.

## 6. Evidence bar and buckets

Sort every surviving finding into one of two buckets:

- **Confirmed** — you can state all three of: a **reachable scenario** (the concrete input, state, or sequence that triggers it), the **invariant it violates**, and the **resulting observable behavior** — anchored at `file:line`. Citing a location is not enough on its own: a real line number can still anchor an unreal defect.
- **Unverified suspicion** — plausible and consequential, but not demonstrable from the code alone. State the risk and the **specific check that would settle it**: a test to run, a state to reproduce, a file or system to inspect. Never inflate one into a Confirmed finding, and never silently drop one.

A finding belongs in Confirmed only if it is discrete and actionable, provably affects real code paths (name them, don't speculate), matches the rigor of the surrounding codebase, and is clearly not a deliberate choice by the author.

## 7. Reporting

Deduplicate across all agents, then present:

```
### Confirmed
| File | Line | Severity | Category | Scenario → invariant → observable behavior | Suggested fix |
| :--- | :--- | :--- | :--- | :--- | :--- |

### Unverified suspicions
| File | Line | Risk | Check that would settle it |
| :--- | :--- | :--- | :--- |

### Nits
| File | Line | Category | Description & suggested fix |
| :--- | :--- | :--- | :--- |
```

Severity: **Critical** (causes a crash, wrong behavior, data loss, or breaks something that worked) · **Warning** (probable defect or latent hazard) · **Nit** (from a lens only, never fixed). Category: name the pass or lens it came from — `Defect`, `Regression`, `Contract`, `Security`, `Resource`, plus whatever categories the lens defines.

Omit any section that is empty. If all are empty, say LGTM and skip the tables. End with one line: `X critical, Y warnings, Z nits across N files; W unverified suspicions.`

## 8. Fix, self-check, then hand back honestly

Fix every **Confirmed** Critical and Warning before returning control. **Never** edit code on the strength of an unverified suspicion — report it and leave it. Leave Nits reported but unfixed unless the caller asks. Make the smallest fix that resolves the finding; do not refactor around it.

Then, and only for the hunks you just edited, re-read them against the same two questions: does this fix introduce a defect, and does it break anything that worked? Fix and note anything it turns up. Do not re-run the review agents — the caller will request another review if needed.

Finally, state what you changed **and that nothing was executed**. This skill runs no builds, tests, or linters, so every fix it applied is unverified; verification belongs to the caller's own verify step. The summary must not imply otherwise.
