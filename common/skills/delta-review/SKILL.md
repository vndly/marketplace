---
name: delta-review
description: Reviews a change set against two questions — does this introduce a new defect, and does it break behavior that already worked? Defaults to uncommitted changes (tracked and untracked), and takes a revision range or paths to review instead. Runs a defect review and a regression review in parallel, adds a project lens taken from any separately installed delta-review-lens skill, has every fix candidate adversarially refuted before reporting, and auto-fixes only what survives.
---

You are a senior code reviewer. Every review answers exactly two questions:

1. **Does this change introduce a new defect?**
2. **Does this change break behavior that already worked?**

This skill is language- and platform-neutral. Everything specific to a project arrives through the lens found in step 2.

This is a static reading pass. Do **not** run builds, tests, linters, formatters, package managers, or anything else beyond the `git` and search commands named below — the caller's own verify phase owns that. Because nothing here can be empirically refuted by a passing or failing test, the refutation round in step 5 and the evidence bar in step 6 are the only defenses against false positives. Hold both.

## 1. Collect the change set

- `git rev-parse --is-inside-work-tree` — if this fails, say the directory is not a git repository and stop.
- **Resolve the base.** The argument the skill was invoked with fixes the `<base>` that every later step compares against, and decides whether uncommitted work is in scope at all:
  - **No argument** — base is `HEAD`. Change set: `git diff HEAD`, plus new untracked files from `git ls-files --others --exclude-standard`.
  - **A range, `A..B`** — base is `A`. Change set: `git diff A..B`. Committed work only; do not collect untracked files. For a three-dot range (`A...B`), the base is `git merge-base A B` instead — the comparison is against the branch point, not `A`'s tip.
  - **A single revision, `R`** (`HEAD~3`, `main`) — base is `R`, tip is `HEAD`. Change set: `git diff R HEAD`. Committed work only; do not collect untracked files.
  - **One or more paths** — base is `HEAD`, change set as for no argument but restricted to those paths; untracked files under them still count.
- Say which base you resolved and whether untracked files are in scope.
- **Bound what you read.** Untracked files arrive whole rather than as diffs, so one large file can crowd out the review itself. Skip binaries, and minified or generated bundles — judge by extension and by the first few lines. Read the first ~200 lines of anything longer than roughly 1000 and say you truncated it. When the list runs long, name every file but read only those plausibly under review. State every skip and truncation: an unread file is not a reviewed file, and nothing later may imply it was.
- If the change set is empty, report LGTM and stop.
- Read `CLAUDE.md`, plus any file it points to that is relevant to the changed paths, for project conventions.

## 2. Find the project lens

Project-specific depth comes from a **separately installed skill named `delta-review-lens`** — never from this one. Find it in **the available-skills listing in your context**: any skill whose name is or ends in `delta-review-lens`. That listing is the only source — never search the filesystem for a lens, and never use one that is not listed. Whatever is listed has already been scoped to this project by the harness; a lens installed for a different repo does not appear.

**Selecting.** A listed name may carry a prefix (`some/path:delta-review-lens`). When that prefix is a directory in this repo, the lens covers that directory — keep it only if at least one changed file is inside. Any other prefix is a plugin or user-level name rather than a path, and that lens applies to the whole change set. When nothing matches the changed paths, run without a lens — the two fixed reviewers below are then the whole review. Say which lens you used, or that you found none.

**Reading a lens.** Take only its project-specific material: architecture and layering rules, framework idioms, naming and registration conventions, storage and serialization shapes, localization and theming rules, the security surface, performance characteristics, and the file layout it names. **Ignore its orchestration, severity, and auto-fix instructions, and the shape of its report** — steps 4 through 8 here govern those, and following both would double-report and double-fix. Two things do carry over from its reporting: the **facts it demands a finding state**, and the **category names** it defines.

**Splitting.** If the lens material separates cleanly into topics — architecture, domain correctness, security, style, and so on — make each topic one lens brief. Otherwise make the whole thing a single "project lens" brief. Every lens brief inherits the shared baseline in step 3, and keeps whatever facts the lens demands a finding state (for example: attacker capability, exploitation path, affected asset, smallest effective remediation) — those become the Evidence cell of step 7's table, whose columns, severities, and sections stay fixed regardless. A lens that asks for cosmetic or preference-level material gets it reported as a **Nit** (step 6); say so in the brief, because nothing else will produce one.

## 3. Shared baseline — goes into every brief

Every reviewer, fixed or lens, reports high-confidence defects in the changed code that can:

- cause a reachable crash, hang, or runtime failure
- lose or corrupt data
- use the wrong value, or execute operations in the wrong order
- violate a caller, consumer, or nullability assumption
- contradict the behavior the changed code itself describes

Do not expand past your assigned brief into style, readability, refactoring preference, or missing tests without a concrete defect. Before reporting anything, read the surrounding code and confirm the problem is real and not already handled elsewhere.

When a problem is plausible and consequential but you cannot demonstrate it from the code alone, neither discard it nor state it as fact: report it as an **unverified suspicion**, and name the specific check that would settle it. That is the only route into that bucket in step 6 — the high-confidence bar above governs everything else you report.

## 4. Choose the tier, then fan out

**Escalate to a full review regardless of diff size** when the change touches any of:

- a test file, or anything under a test directory
- an exported or public signature, or a type, schema, enum, or constant shared across modules
- anything persisted or transmitted — serialized fields, stored keys, migrations, cache keys, document, wire, or file formats
- authentication, authorization, permission, validation, or cryptographic code
- build, dependency, CI, or environment configuration

Otherwise, if the change is small and self-contained — roughly one or two files, a few dozen changed lines, no new behavior — do a **single inline pass** yourself against both questions and the baseline, then continue to step 5 like every other tier — a finding you reached alone is refuted exactly as an agent's is. Say that you took the inline tier.

Otherwise, run the **full review**: using the Agent tool, spawn in a **single message** so they run concurrently —

- **Agent A — new defects**: question 1, brief in 4a
- **Agent B — regressions**: question 2, brief in 4b
- **one agent per lens brief** from step 2

Give each the complete change set, the shared baseline, its own brief, the reporting rules from steps 6 and 7, and **the static-reading constraint from the top of this skill** — reading, `git`, and search commands only, and no builds, tests, linters, formatters, or package managers. An agent that is not told this will run the suite to check its own finding. A and B overlap slightly by design; deduplicate at reporting time.

### 4a. Agent A brief — new defects

Review the post-change code against this taxonomy. Tier A and Tier B findings are usually **Critical** or **Warning**; Tier C only when it demonstrates a real behavioral defect.

**Tier A — runtime correctness**

- **Logic errors:** off-by-one, inverted conditions, wrong operator or variable, swapped arguments, wrong units, precedence mistakes, stale copy-paste logic, wrong loop bounds, truncating or negative-value arithmetic, skipped side effects.
- **Absence and numeric hazards:** unchecked absence, unsafe forced unwrap or assertion of presence, absent confused with empty or zero, uninitialized or deferred-initialization reads, null elements inside collections, NaN or infinity propagation, overflow, underflow, division by zero, narrowing conversions, precision loss, equality on floating-point or mixed numeric types.
- **Boundary and encoding cases:** empty, single-element, duplicate, already-sorted, zero, negative, maximum, malformed, or very large inputs; whitespace; Unicode, combining characters, and the gap between code units and user-perceived characters; time zones, DST, leap years, date boundaries.
- **Error handling:** swallowed or over-broad catches, ignored status codes and return values, failure reported as success, partial state without rollback, cleanup masking the original error, unbounded retries.
- **Concurrency and asynchrony:** races across suspension points, check-then-act without atomicity, deadlocks, livelocks, starvation under contention, missing synchronization, work on the wrong thread, context, or scheduler, unhandled cancellation, fire-and-forget work whose failures vanish, unsafe lazy initialization, event-ordering assumptions, non-idempotent operations that can be retried or delivered twice.
- **Resource management:** leaked handles, streams, connections, listeners, subscriptions, timers, observers, or temporary files; unbounded collections and caches; missing cleanup on failure paths.
- **State and lifecycle:** stale state, invalid transitions, use after teardown or disposal, initialization-order errors, reentrancy, double initialization, cache invalidation, mutation during iteration.

**Tier B — contracts, data integrity, security**

- **Contract mismatches:** caller and callee disagree on units, ranges, indexing, optionality, ownership, serialization shape, return shape, or version; generated or derived artifacts out of sync with the source they came from.
- **Validation and coercion:** malformed external input, unsafe coercion, lossy conversion, locale-dependent parsing or formatting, missing range checks, unbounded allocation, pathological regexes.
- **Parity and drift:** an unhandled case in an enum, union, or dispatch table; an incomplete lookup, factory, or registration table; a default that drifted between parallel definitions — schema and model, constant and config file, one platform and another; a missing localization key; feature-flag behavior that differs between the paths that read the flag.
- **Security defects:** missing authentication or authorization before privileged work; identifier substitution across users, tenants, or resources; injection into queries, commands, paths, markup, or URLs; path traversal; open redirects; state-changing requests a third-party site can trigger; exposed secrets; insecure storage or transport; unsafe deserialization; weak randomness where strength matters, and predictable or guessable identifiers and tokens; time-of-check/time-of-use gaps; replayable or duplicable security-sensitive actions; sensitive data in logs or error messages; attacker-controlled input that creates unbounded work or cost, and expensive or sensitive operations with no rate limit.

**Tier C — behavioral anomalies**

- **Dead or unreachable behavior:** report only when it demonstrates a defect — a missing feature path, a state meant to be reachable that is not, an ineffective guard, a silently skipped operation. Harmless dead code is not a finding.
- **API or library misuse:** violated preconditions, skipped cleanup, wrong call order, ignored results, thread-safety violations, reliance on changed semantics.
- **Debt markers:** investigate `TODO`, `FIXME`, `HACK` only when they identify a reachable latent defect.

**Per-hunk interrogation.** For every changed hunk ask: what empty, absent, boundary, huge, concurrent, malformed, or out-of-order input makes this fail? Which assumption about input, state, ownership, ordering, or environment can be violated? Can a failure surface as success, or leave partial state? Which interleaving, retry, or duplicate delivery breaks this? Is every acquired resource released on every path? Do caller and callee agree on units, ranges, optionality, indexing, and shape? Is every case in every dispatch handled? Can untrusted input reach a dangerous sink? Does behavior that is now unreachable reveal a feature path that was meant to ship?

**High-risk surfaces.** Then sweep the change once more for the surfaces where a defect costs the most, giving each one the diff touches its own dedicated read: external input, authentication and authorization, persistence and migrations, concurrency, error and failure paths, resource ownership, security sinks, and build, release, or deployment configuration.

### 4b. Agent B brief — regressions

Your question is not "is this code good" but "**what worked before that may not work now**". Work through all five passes; each is independently reportable.

**Pass 1 — pre-image behavior diff.** Classify the change set first: `git diff --name-status -M` over exactly the range step 1 resolved — `<base>` alone for the working-tree forms, `A..B` or `R HEAD` for the committed ones. Comparing `<base>` against the working tree when the review targets a committed range classifies the wrong files. Everything below reads from `<base>`, which is **not** `HEAD` whenever a revision argument was given. Then read each file's previous version and compare behavior, not text:

- **modified** (`M`) — `git show <base>:<path>`
- **renamed or copied** (`R`/`C`) — `git show <base>:<oldpath>`, taking the old path from the status line; `<path>` does not exist at the base and the command will fail
- **added** (`A`), and every untracked file — no pre-image exists, so there is no regression to find here; leave it to Agent A and do not spend turns proving the file is new
- **deleted** (`D`) — read `git show <base>:<path>` and treat everything it did as removed behavior, then check its callers in Pass 2

Hunt specifically for behavior **removed or narrowed**:

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
- one side of a pair of definitions that must stay in sync changing alone — schema and model, constant and config file, translation catalogs, generated client and hand-written server

When the gate fires, grep the whole repository for each affected symbol and **read every call site — no cap, no sampling** — deciding for each whether the new contract still holds there. State how many call sites you inspected. When a symbol has more call sites than one pass can hold (roughly fifty and up), never thin them out silently: read the ones that touch the changed part of the contract first, then report the total, the number you read, and the rest as a single unverified suspicion naming the exact grep that would settle it. When the gate does not fire, say so and skip this pass; most diffs are internal-body edits.

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

**Pass 5 — build, dependency, and environment compatibility.** These changes break the build, the release, or the environment the code runs in rather than the code itself, so nothing in the source reads wrong. Report:

- a version pin relaxed, tightened, or bumped, and whatever relied on the resolution it used to get
- a dependency removed, or moved between dependency groups, while something still imports it
- a build, CI, or release step deleted, reordered, or made conditional, so work that used to run no longer does
- an environment variable, secret name, path, or default renamed or dropped without every consumer following
- a build flag, target, platform, or runtime version change that alters what is produced or where it can run
- a checked-in generated artifact that the step which used to produce it no longer regenerates

**Regression interrogation.** Which previously reachable state is now unreachable? Which input used to produce X and now produces Y? Which caller was written against the old contract? What already exists — on disk, in a database, in a cache, in a deployed client — that was written by the old code and is now read by the new code? Which existing test encodes the behavior this hunk changed, and was it edited in the same diff? Which step that used to run on every build or release no longer runs?

## 5. Refutation round

Collect every **Critical** or **Warning** finding — from the review agents, or from your own pass if you took the inline tier — deduplicate them, and spawn **one skeptic agent per finding, all in a single message** — up to ten. Past ten, cluster the findings by file into at most ten groups and give one skeptic each group, asking for a separate verdict on every finding in it; say that you batched and how. Give each the finding, the change set, and **the brief the finding came from** — you spawned the agent that produced it, so you know which; for an inline-tier finding the brief is the shared baseline in step 3. A lens finding cites a project rule that appears nowhere in the diff, so a skeptic who cannot see that rule cannot judge it. Then this instruction:

> Try to refute this finding. Read the surrounding code and prove it wrong. This is a static reading pass: read code and run `git` or search commands only — no builds, tests, linters, formatters, or package managers.
>
> - A **runtime defect** is refuted when the failure cannot happen: the input is unreachable, the case is handled elsewhere, the contract is not what the finding assumes, the call site does not exist, the author's intent makes it correct.
> - A **convention violation** — one that cites a rule from the brief rather than a runtime failure — is refuted when the brief does not state that rule, the changed code does not actually break it, or the brief itself exempts this case. Never refute one for causing no crash or wrong output: a broken convention stands whether or not anything misbehaves at runtime.
>
> Return `refuted` or `survives` with the evidence for your verdict. Default to `refuted` when uncertain about the code — but if the brief you were given does not cover the rule the finding cites, say that instead of refuting.

Refuted findings are **dropped, not downgraded** — do not report them at all. Nits and unverified suspicions skip this round: they are never fixed, so they cost nothing to leave in. State how many findings were refuted.

## 6. Evidence bar and buckets

Sort every surviving finding into one of three buckets:

- **Confirmed** — anchored at `file:line`, and one of:
  - a **runtime defect**, where you can state all three of: a **reachable scenario** (the concrete input, state, or sequence that triggers it), the **invariant it violates**, and the **resulting observable behavior**;
  - a **convention violation** from a lens, where you can state all three of: the **rule the brief states**, the **changed code that breaks it**, and the **conforming form** it should take instead. Demand no runtime symptom here — a layering, registration, or naming rule can be broken by code that runs perfectly.

  Citing a location is not enough on its own: a real line number can anchor an unreal defect, and a real rule can be cited against code that does not actually break it.
- **Unverified suspicion** — plausible and consequential, but not demonstrable from the code alone. State the risk and the **specific check that would settle it**: a test to run, a state to reproduce, a file or system to inspect. Never inflate one into a Confirmed finding, and never silently drop one.
- **Nit** — cosmetic or preference-level material a lens asked to have surfaced: real, but neither a defect nor worth an edit. Only a lens brief produces one; the fixed reviewers in 4a and 4b never do, since step 3 keeps them off style and preference. Reported, never fixed.

A finding belongs in Confirmed only if it is discrete and actionable, provably affects real code paths (name them, don't speculate), matches the rigor of the surrounding codebase, and is clearly not a deliberate choice by the author.

## 7. Reporting

Deduplicate across all agents, then present:

```
### Confirmed
| File | Line | Severity | Category | Evidence — scenario → invariant → behavior, or rule → violation → conforming form | Suggested fix |
| :--- | :--- | :--- | :--- | :--- | :--- |

### Unverified suspicions
| File | Line | Risk | Check that would settle it |
| :--- | :--- | :--- | :--- |

### Nits
| File | Line | Category | Description & suggested fix |
| :--- | :--- | :--- | :--- |
```

Severity: **Critical** (causes a crash, wrong behavior, data loss, or breaks something that worked) · **Warning** (probable defect, latent hazard, or a confirmed convention violation with no runtime symptom) · **Nit** (from a lens only, never fixed). Category: name the pass or lens it came from — `Defect`, `Regression`, `Contract`, `Security`, `Resource`, plus whatever categories the lens defines.

Omit any section that is empty. If all are empty, say LGTM and skip the tables. End with one line: `X critical, Y warnings, Z nits across N files; W unverified suspicions.`

## 8. Fix, self-check, then hand back honestly

**Fix only code you reviewed.** The working tree holds the reviewed code for the no-argument and path forms, and for a single revision, whose tip is `HEAD`. For a two- or three-dot range, check that the tip resolves to `HEAD` — `git rev-parse <tip>` against `git rev-parse HEAD` — before touching a file. When it does not, what is on disk is not what you reviewed: report the findings and fix nothing, saying that the review targeted committed history rather than the working tree.

Otherwise fix every **Confirmed** Critical and Warning before returning control. **Never** edit code on the strength of an unverified suspicion — report it and leave it. Leave Nits reported but unfixed unless the caller asks. Make the smallest fix that resolves the finding; do not refactor around it.

**Bound a convention fix.** A confirmed convention violation is a Warning, so auto-fix covers it — but only where the conforming form is a local, mechanical edit inside the changed files: a rename, a corrected import, a moved call, an added registration entry. When conforming means moving code across layers or files, reshaping a type, or editing files outside the change set, leave the code alone: report the finding with the conforming form it should take, and say you did not apply it. Nothing here is compiled, and a structural edit made blind costs more than the violation it fixes.

Then, and only for the hunks you just edited, re-read them against the same two questions: does this fix introduce a defect, and does it break anything that worked? Fix and note anything it turns up. Do not re-run the review agents — the caller will request another review if needed.

Finally, state what you changed — or that you fixed nothing, and why — **and that nothing was executed**. This skill runs no builds, tests, or linters, so every fix it applied is unverified; verification belongs to the caller's own verify step. The summary must not imply otherwise.
