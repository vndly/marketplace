---
name: apocalypse-bug-review
description: Run an extremely strict, exhaustive defect hunt over a selectable scope (whole codebase or a diff/path subset) for bugs, correctness errors, inconsistencies, security flaws, and edge-case failures.
---

# Apocalypse Bug Review

Use this skill for an unusually strict, exhaustive hunt for defects: bugs, correctness errors, inconsistencies, edge-case failures, and security flaws that can cause incorrect application, build, release, deployment, migration, operational, security, or data behavior.

Be adversarial about behavior. Read the code looking for the input, sequence, state, environment, or interleaving that makes it fail. Do not spend effort on abstractions, naming, file size, or style unless they directly cause incorrect behavior.

## Operating Rules

- Assume behavior is unverified until its contracts and failure paths have been inspected.
- Cast a wide net during discovery, but report only defects whose reachable failure path and incorrect result survive verification. Validate each finding twice: first establish its reachability and incorrect result, then perform a separate refutation attempt that tries to disprove the suspected defect.
- For change-based scopes, report only defects the reviewed changes introduce. A candidate whose incorrect behavior reproduces unchanged in the baseline state is pre-existing: record its disposition and do not report it as a finding, however severe it is.
- Treat the worktree as read-only by default. Do not fix product code or configuration.
- Perform verification only against local, isolated, or explicitly approved test environments.
- Never deploy, mutate production data, run destructive migrations, exploit live systems, expose secrets, or contact external services without explicit user approval.
- Preserve all pre-existing tracked and untracked work. Except for an explicitly approved `BUG_FINDINGS.md` replacement under the Output contract, never delete, revert, overwrite, or clean up pre-existing state or user-authored changes.
- Make the first audit workflow action an initial worktree snapshot, before substantive inspection of the audit target or any verification. Store snapshot metadata outside the repository. Record the branch and commit; tracked and untracked status; hashes of the initial staged and unstaged tracked diffs; and a manifest of every initially non-clean tracked path and initially untracked path. Include ignored paths that verification might touch, or explicitly exclude them from the preservation guarantee. For every manifested path, record its existence, type, and mode, plus its content hash or symlink target when applicable.
- Run commands expected or reasonably likely to create, delete, or modify files only in a disposable verification workspace outside the repository. Construct it from a copy of the audited source state after capturing the snapshot; exclude `.git` internals and unnecessary secret-bearing files; and record material differences from the audited worktree. If representative verification cannot be performed there safely, skip it and record the limitation.
- Treat `BUG_FINDINGS.md` as the sole permitted repository change, subject to the existing-report approval rule in the Output contract. Do not claim preservation of ignored or otherwise excluded paths unless they were captured and compared.

## Scope

Audit the user-selected scope, determined at the start of the run (see Phase 0, step 3). The scope is one of:

- **Whole codebase:** every included first-party file.
- **Branch diff:** first-party files changed between the current branch and a base ref, computed from the merge-base diff. The base ref is detected from the current branch's divergence point (see Phase 0, step 2) and can be overridden by the user.
- **From commit:** first-party files changed by a user-named commit and every commit after it, through `HEAD`. Uncommitted work is excluded; use _Uncommitted changes_ for that.
- **Uncommitted changes:** tracked modifications plus untracked first-party files in the working tree.
- **Unpushed commits:** changes in local commits ahead of the upstream branch.
- **Session changes:** first-party files modified during the current chat session.
- **Named paths:** the files, directories, or globs the user provides.

The selected scope defines the **seed set** of files. For every scope except _Whole codebase_, the **included set** is the seed set plus its direct first-party dependents — callers of changed functions and consumers of changed types, schemas, or configuration — expanded one hop out, so defects the change introduces in other files remain in scope. Meaningful flows that traverse the seed set are traced end to end even where they extend beyond one hop. For _Whole codebase_, the included set is every included first-party file and the meaningful-flow inventory is every meaningful flow.

The initial worktree snapshot and every preservation guarantee always cover the entire worktree regardless of scope: scope narrows only what is inspected, never what is preserved. The include and exclude rules below act as filters within the included set, the coverage invariants apply to the included set, and for non-whole scopes the meaningful-flow inventory consists of the flows that traverse the seed set.

_Branch diff_, _From commit_, _Uncommitted changes_, _Unpushed commits_, and _Session changes_ are **change-based scopes**. Each has a **baseline state**, the committed or worktree state the reviewed changes are measured against:

- **Branch diff:** the merge-base commit of the base ref and `HEAD`.
- **From commit:** the named commit's first parent, `<commit>~1`. When the named commit is a merge, `~1` selects its first parent. When `<commit>~1` does not resolve, check `git rev-parse --is-shallow-repository` before concluding the commit is the root: in a shallow repository an unresolvable parent means the parents were never fetched, and a boundary commit is indistinguishable from a root commit by parent lookup alone, so deepen with `git fetch --unshallow` or refuse the scope and re-ask, and never substitute the empty tree there. Only in a non-shallow repository, where the commit genuinely has no parent, use the empty tree `4b825dc642cb6eb9a060e54bf8d69288fbee4904` as the baseline and state the substitution in the chat summary.
- **Uncommitted changes:** `HEAD`.
- **Unpushed commits:** the upstream commit `@{upstream}`.
- **Session changes:** the worktree state at the start of the session. When it cannot be reconstructed, use the closest available baseline, normally `HEAD`, and state the substitution in the chat summary.

For a change-based scope, report only **introduced defects**. A defect is introduced when its incorrect behavior does not occur in the baseline state: the changed code is new, the change altered previously correct behavior, or the change made an existing latent defect reachable, an existing contract violated, or an existing guard ineffective. A defect whose incorrect behavior reproduces unchanged in the baseline state is **pre-existing** and is never a finding, however severe it is, and regardless of whether it sits in a changed file or in a one-hop dependent. _Whole codebase_ and _Named paths_ have no baseline: every defect established within their included set is reportable.

For this audit:

- **First-party file:** a repository-owned file that defines, validates, builds, releases, deploys, migrates, configures, documents, or tests shipped behavior, including documentation that records an authoritative or asserted behavioral contract.
- **Inspected file:** a file whose relevant contents and role have been reviewed at least once.
- **Skipped file:** an included first-party file that was not inspected.
- **Meaningful flow:** an externally invocable operation or independently triggered user-visible or operational behavior traced from an entry point through its material contracts, state changes, side effects, result, and error handling. Split flows when authorization, persistence, side effects, or failure handling materially differ. Do not count internal helper calls as separate flows.
- **Traced or skipped flow:** a meaningful flow is traced when its material contracts, state changes, side effects, result, and error handling were reviewed; otherwise it is skipped.

Include:

- Application, library, service, and command-line source.
- First-party scripts, migrations, build logic, CI workflows, infrastructure definitions, and configuration that can affect shipped behavior, releases, deployments, operations, or data.
- Tests, documentation, schemas, and interface definitions as evidence of intended contracts. Report a defect in such an artifact only when it directly causes incorrect shipped behavior, asserts an incorrect authoritative contract, or demonstrably conceals an established shipped defect. Missing coverage or unclear documentation alone is not a finding.
- Checked-in generated artifacts that are shipped, deployed, consumed directly, or used to validate behavior. Attribute the finding to the first-party generator or source configuration when that is the root cause.

Exclude:

- Vendored, minified, dependency, cache, and disposable build output such as `node_modules`, `vendor/`, `build/`, `dist/`, `target/`, and `.git`, unless a generated artifact is checked in and directly shipped, deployed, consumed, or used to validate behavior. The inclusion rule for such generated artifacts takes precedence over this exclusion.
- Generated artifacts that are neither checked in nor consumed as part of shipped behavior.
- Pure maintainability concerns with no demonstrated behavioral consequence.

Record the initial worktree snapshot: repository path, branch, commit, initial tracked modifications, and initial untracked files. Record captured and excluded ignored-path categories, explicit scope exclusions, and any ambiguous ownership decision. Inventory meaningful flows with stable audit-local IDs and record exact total, traced, and skipped flow counts.

Count each included file path and each meaningful flow exactly once. Maintain these coverage invariants:

- `included first-party files = inspected files + skipped files`
- `total meaningful flows = traced flows + skipped flows`

## Candidate Versus Finding

- A **candidate** is a suspicious pattern that requires investigation.
- A **finding** is a candidate whose code-path reachability and incorrect result are established under a concrete or plausible stated trigger and that, in a change-based scope, the reviewed changes introduce. Every such verified root cause must be represented in `BUG_FINDINGS.md`; merge candidates that share the same root cause into one finding.
- A candidate is **refuted** when a guard, invariant, caller contract, unreachable state, or other evidence prevents the suspected incorrect behavior.
- A candidate is **pre-existing** when its defect path is established but the same incorrect behavior reproduces in the baseline state of a change-based scope, so the reviewed changes did not introduce it.
- A candidate is **unverified** when verification is blocked or cannot establish the defect path. Do not report it as a finding; state the location, suspected risk, blocker, and unresolved question in the chat summary.

Assign each candidate a stable audit-local ID such as `C-001`. Keep a transient candidate ledger in memory or outside the repository. For each candidate, record its ID, location, taxonomy category, suspected trigger and failure path, verification evidence, and final disposition:

- **Finding:** became one unique reported finding.
- **Merged:** shares a root cause with another candidate and maps to that candidate's finding.
- **Refuted:** evidence disproved the suspected defect path.
- **Pre-existing:** the defect path is real, but the reviewed changes did not introduce it.
- **Unverified:** verification remained blocked or inconclusive.

Maintain this accounting invariant, where each term counts candidates with that disposition: `total candidates = findings + merged + refuted + pre-existing + unverified`. The reported finding list must reconcile with the ledger: `reported findings = findings`, since each Finding-disposition candidate becomes exactly one reported finding while merged candidates fold into an existing finding rather than adding new ones. The ledger stays transient and is never written to `BUG_FINDINGS.md`; report only its disposition counts, in the chat summary. Pre-existing candidates are never reported as findings and are never described anywhere in the report or the chat summary; they survive only inside the aggregate disposition counts.

## Defect Taxonomy

Inspect every category in all three taxonomy tiers. Assign each finding the tier and category that most directly describe its root cause; the tiers classify defects and do not imply severity or inspection order.

### Tier A - Runtime Correctness

- **Logic errors:** off-by-one errors, inverted conditions, wrong operators or variables, swapped arguments, incorrect units, precedence mistakes, stale copy-paste logic, wrong loop bounds, integer division, negative modulo behavior, and skipped side effects.
- **Null and numeric hazards:** unchecked absence, force-unwrapping, absent values confused with empty or zero values, null collection elements, NaN propagation, overflow, underflow, division by zero, narrowing conversions, and precision loss.
- **Boundary and encoding cases:** empty, singleton, duplicate, sorted, zero, negative, maximum, malformed, or very large inputs; whitespace; Unicode and combining characters; time zones, DST, leap years, and date boundaries.
- **Error handling:** swallowed or over-broad errors, ignored status codes, failure reported as success, partial state without rollback, cleanup masking the original error, and unbounded retries.
- **Concurrency:** races, deadlocks, livelocks, missing synchronization, wrong executors, unhandled cancellation, non-atomic check-then-act sequences, unsafe lazy initialization, and failures hidden by fire-and-forget work.
- **Resource management:** leaked handles, streams, sockets, listeners, subscriptions, timers, temporary files, unbounded collections, and missing cleanup on failure paths.
- **State and lifecycle:** stale state, invalid transitions, use-after-dispose, initialization-order errors, reentrancy, cache invalidation, double initialization, and mutation during iteration.

### Tier B - Contracts, Data Integrity, and Security

- **Contract mismatches:** callers and callees disagree on units, ranges, indexing, nullability, ownership, serialization, return shape, or version.
- **Validation and coercion:** malformed external input, unsafe coercion, lossy conversion, locale-dependent parsing, missing range checks, unbounded allocations, and pathological regexes.
- **Resource and configuration parity:** missing enum or switch cases, incomplete lookup tables, drifted defaults, missing localization keys, and inconsistent feature-flag behavior.
- **Security defects:** injection, path traversal, missing authentication or authorization, exposed secrets, insecure storage or transport, unsafe deserialization, weak security randomness, time-of-check/time-of-use gaps, request forgery, open redirects, insecure direct object references, missing rate limits, predictable tokens, and sensitive logs.

### Tier C - Broader Behavioral Anomalies

- **Dead or unreachable behavior:** report only when it demonstrates a behavioral defect, such as a missing feature path, impossible intended state transition, ineffective guard, or silently skipped operation. Do not report harmless dead code by itself.
- **API or library misuse:** violated preconditions, skipped cleanup, wrong lifecycle or call order, ignored status values, thread-safety violations, or reliance on changed semantics.
- **Debt markers:** investigate `TODO`, `FIXME`, and `HACK` only when they identify a reachable latent defect. Do not turn this into a debt inventory.

## Audit Workflow

Use Codex collaboration agents in parallel when they are available and permitted. Spawn bounded, independent tasks with `spawn_agent`, collect their results before synthesis, and use `send_message` or `followup_task` only to clarify an existing assignment. Agents may inspect files, trace flows, and propose or refute candidates, but they must not write repository files or run commands expected to modify repository or external state. Discovery agents may over-report candidates, but only the coordinating agent writes `BUG_FINDINGS.md`.

### Phase 0 - Orient and Inventory

1. As the first audit workflow action, capture the initial worktree snapshot specified in Operating Rules before substantive inspection or verification. The snapshot always covers the entire worktree, independent of the scope selected next.
2. Detect the base ref for a branch diff before asking anything, using read-only git queries. Build the candidate list from the local or remote branches `develop`, `main`, and `master` that exist; the remote default branch reported by `git symbolic-ref --quiet refs/remotes/origin/HEAD`; and the configured upstream from `git rev-parse --abbrev-ref --symbolic-full-name @{upstream}` when it names a branch other than the current one. Drop the current branch from the candidates. For each remaining candidate, compute `git merge-base <candidate> HEAD` and `git rev-list --count <merge-base>..HEAD`, and discard any candidate whose merge-base is `HEAD` itself, because its diff would be empty. Select the candidate with the fewest commits ahead, which is the most recent divergence point, breaking ties in the order `develop`, `main`, `master`, remote default, upstream. Record the detected base ref, the candidates considered, and their commit counts, or record that no base ref was detected.
3. Select the audit scope. If the invocation already specifies a scope, use it without asking, first applying the `commit: <sha>` validation below when the invocation supplies one. Otherwise, use `request_user_input` when it is available; if it is unavailable, ask the same questions directly in plain text and wait for the answer:
   - When a base ref was detected, ask a primary question with the options `Diff vs <detected base> (Recommended)`, `Local changes`, and `Whole codebase`. Use the tool-provided free-text `Other` for a different base ref, a starting commit, or named paths, requiring `base: <ref>`, `commit: <sha>`, or `paths: <paths/globs>` so the intent is unambiguous; clarify any unlabeled answer before proceeding. Choosing the first option needs no base follow-up.
   - When no base ref was detected, state that in the question and ask a primary question with the options `Whole codebase (Recommended)`, `Local changes`, and `Diff vs a branch`. Use the tool-provided free-text `Other` for named paths or a starting commit as `commit: <sha>`. If `Diff vs a branch`, ask a follow-up question with the options `develop` and `main`, accepting a user-supplied ref through `Other`.
   - If `Local changes`, ask a follow-up question with the options `uncommitted changes including untracked`, `unpushed commits`, and `this chat session's changes`.
   - Whenever a `commit: <sha>` is in play, from the invocation or from the answer, validate it with `git rev-parse --verify <commit>^{commit}` and confirm it is an ancestor of `HEAD` with `git merge-base --is-ancestor <commit> HEAD`. Both checks are required: a commit outside the current history makes the two-dot seed set and the three-dot attribution diff in Phase 2 measure against different baselines, so a defect on the unrelated branch is shown reversed in the seed set and then silently dispositioned pre-existing. Re-ask when either check fails, or fall back to the default scope below and record the substitution when no interactive response is available. Treat a value that names a branch as `base: <ref>` instead, after confirming with the user. The named commit may be `HEAD` itself, which audits that commit alone.
   - If the free-text answer names paths, confirm the exact paths or globs in prose before resolving them, since a fixed option list cannot capture free-form paths.
     The plain-text fallback must state what the choice changes, list all five concrete scope types, mark the detected branch diff as recommended when one exists (otherwise mark `Whole codebase` as recommended), and explicitly accept a free-form answer. In a non-interactive run where no response can be provided, default to the detected branch diff, or to `Whole codebase` when no base ref was detected. Record the chosen scope.
4. Resolve the scope to the seed set with explicit, recorded commands: the merge-base diff `git diff <base>...HEAD --name-only` for a branch diff; `git diff <commit>~1..HEAD --name-only` for from commit, using the baseline substitution in Scope when `<commit>~1` does not resolve; `git diff HEAD --name-only` plus untracked files from `git status --porcelain` for uncommitted changes; `git diff @{upstream}..HEAD --name-only` for unpushed commits, falling back to whole codebase when no upstream is configured; the files edited during this session for session changes; or the literal paths for named paths. For every scope except whole codebase, expand the seed set one hop to the included set by adding the direct first-party dependents of the seed, and record both the seed set and the expansion. For a change-based scope, also resolve and record the baseline state defined in Scope, as a commit hash where one exists.
5. Read the Codex instruction chain applicable to every included path. In each directory from the repository root toward that path, honor the first non-empty file in Codex precedence order: `AGENTS.override.md`, `AGENTS.md`, then any configured `project_doc_fallback_filenames`; include relevant files those instructions reference. Then read project documentation, architecture material, schemas, and key contracts.
6. Build a path-level inventory of included first-party files, with an inspected or skipped status for every included path, an exact included-file count, and explicit excluded paths or categories, grouped into meaningful modules and flows. Record deterministic selection rules and commands, exact counts per module, and a manifest digest so the included inventory can be reproduced and verified against the initial worktree snapshot.
7. Assign stable audit-local IDs to meaningful flows and record exact total, traced, and skipped flow counts. For each flow, record its entry point, material result or side effect, and status.
8. Identify high-risk surfaces: external input, authentication and authorization, persistence, migrations, concurrency, error handling, resource ownership, security sinks, release logic, and deployment configuration.
9. Record exclusions, ambiguous ownership, and files or flows that cannot be inspected.

### Phase 1 - Discover

1. Inspect every inventoried file and trace every inventoried meaningful flow at least once.
2. Record each candidate in the transient ledger.
3. Trace cross-module contracts and parallel resources that must remain consistent.
4. Run a dedicated high-risk pass covering external input, dangerous sinks, authorization, error paths, concurrency, resource cleanup, boundaries, migrations, and partial updates.

For every meaningful module or flow, ask:

- What empty, null, boundary, huge, concurrent, malformed, or out-of-order input makes this fail?
- Which assumption about input, state, ownership, ordering, or environment can be violated?
- Can a failure surface as success or leave partial state?
- Which concurrency interleaving breaks this?
- Is every acquired resource released on every path?
- Do caller and callee agree on units, ranges, nullability, indexing, and ownership?
- Is every dispatch case handled?
- Can untrusted input reach a dangerous sink?
- Does unreachable behavior reveal missing or ineffective shipped behavior?

### Phase 2 - Verify and Refute

For every candidate:

1. Trace its real callers, data flow, guards, contracts, and state transitions.
2. Establish a concrete or plausible trigger and the resulting incorrect behavior.
3. Try to refute it by finding a preventing invariant, guard, contract, or unreachable condition.
4. For a change-based scope, attribute it: decide whether the same incorrect behavior occurs in the baseline state, by reading the baseline version of every location on the defect path with `git show <baseline>:<path>` or `git diff <baseline>...HEAD -- <path>` and, where safe and useful, by exercising the baseline in the disposable verification workspace. Dispose of it as `Pre-existing` when the baseline exhibits the same incorrect behavior, and record the baseline evidence for that decision. Treat it as introduced when the baseline is correct because the defect path was unreachable, the guard was effective, or the contract held there.
5. Where safe and useful, confirm it with an existing test, isolated scratch test, REPL, or focused command.
6. Record evidence and assign a disposition in the candidate ledger.

Verification commands run in the audited worktree must be read-only and must not be expected to rewrite files or modify external state. Run any command expected or reasonably likely to write in the disposable verification workspace. Immediately before and after each verification command or logically inseparable command batch run in the audited worktree, compare the worktree status, staged- and unstaged-diff hashes, and captured file manifest with the initial snapshot, excluding the permitted skill-owned `BUG_FINDINGS.md`. Remove only scratch artifacts created by the audit. If an unexpected change cannot be restored exactly without disturbing pre-existing work, stop that verification path and record the limitation.

When independent collaboration agents are available and permitted, use `spawn_agent` to assign the refutation pass to a different agent and collect its result before dispositioning the candidate. Otherwise, perform and document a separate self-refutation pass after the initial reachability analysis. This separate refutation attempt is the second validation required by Operating Rules; a second reproduction is not required.

### Phase 3 - Complete and Synthesize

Repeat additional discovery passes until one produces no new candidates; designate that last pass as the final discovery pass. If constraints prevent another pass, mark the audit Partial. Resolve every candidate as finding, merged, refuted, pre-existing, or unverified. Verify the candidate accounting invariant and record exact disposition counts. Then deduplicate findings, merge shared root causes, assign final confidence and severity, and write the report. Before completion, perform a final comparison against the initial worktree snapshot, state its result and the snapshot-manifest digest in the chat summary, and remove external snapshot metadata, the disposable verification workspace, and the candidate ledger.

Assign one audit status:

- **Complete:** within the selected scope, the included-file inventory and meaningful-flow inventory are enumerated with exact counts; every included file was inspected; every meaningful flow was traced; every candidate became a finding, was merged, was refuted, or was dispositioned pre-existing against the baseline state; no unverified candidates remain; the dedicated high-risk pass and all taxonomy-category inspections were completed; a separate refutation attempt was performed for every finding; a final discovery pass produced no new candidates; and the final worktree comparison confirmed that no non-exempt captured pre-existing state changed. The audit must retain enough inventory, flow, and candidate-disposition evidence to reproduce every count stated in the chat summary.
- **Partial:** any Complete condition was not met. State each unmet condition in the chat summary and do not claim the audit was exhaustive or complete.

## Verification and Ranking

### Confidence - How Strong Is the Evidence?

Reachability and incorrect behavior must be established for every finding. Confidence describes remaining uncertainty about the stated conditions, environment, frequency, or impact, not whether the defect path exists.

- **High:** the trigger and failure path were reproduced or fully traced, with no material uncertainty remaining.
- **Medium:** the defect path is established, but one material uncertainty remains about its stated conditions, environment, trigger frequency, or impact.
- **Low:** the defect path is established, but multiple material uncertainties remain about its stated conditions, environment, trigger frequency, or impact. State each assumption explicitly.

Do not promote an unverified candidate to a Low-confidence finding.

### Severity - What Is the Worst Credible Impact?

Assign severity from the worst impact supported by a realistic trigger and stated preconditions. Keep occurrence frequency and confidence separate from severity.

- **Critical:** credible broad security compromise, irreversible or widespread data loss or corruption, safety impact, or prolonged total system-wide outage.
- **High:** major loss of core functionality, materially incorrect core results, serious contained security or data-integrity failure, or a recoverable system-wide outage.
- **Medium:** recoverable incorrect behavior, degraded non-core functionality, or failure limited to an edge case with meaningful impact.
- **Low:** minor behavioral defect with limited impact.

## Output

- **Report only.** Do not fix product code or configuration.
- **Introduced defects only.** For a change-based scope, report only defects the reviewed changes introduce. Pre-existing defects are never described in the findings, the summary, or the chat response; they survive only inside the aggregate disposition counts.
- `BUG_FINDINGS.md` is the sole permitted persistent report artifact. At snapshot time, detect and hash any existing report, then read it to retain stable IDs for recurring root causes.
- Do not replace a pre-existing `BUG_FINDINGS.md` without explicit user approval; approval may be supplied with the skill invocation. If approval is unavailable or denied, do not modify it, mark the audit Partial, and provide the blocked report summary in chat. Otherwise, replace its contents and write it even when no findings survive. Immediately before replacement, verify that its current hash still matches the snapshot; if it appeared or changed after the snapshot, treat it as user-authored work and obtain new approval before replacing it.
- Do not intentionally modify any other pre-existing file. Remove only temporary artifacts created by the audit, and preserve the captured initial worktree state.
- Order findings by Severity (`Critical`, `High`, `Medium`, `Low`), then by Confidence (`High`, `Medium`, `Low`) within each severity section.

Use stable IDs in the form `[<tier>/<category>/<component>/<defect-slug>]`, separating the four fields with `/` and using lowercase ASCII kebab-case within each field so field boundaries stay unambiguous:

- Encode `<tier>` as `a`, `b`, or `c`. Encode the taxonomy category heading as lowercase kebab-case, such as `error-handling` or `contract-mismatches`.
- Use the primary root-cause tier and category.
- Use a stable logical component or subsystem, not a file path.
- Describe the root cause, not the report position or observed symptom.
- Keep an existing ID when the same root cause moves files.
- Example: `[a/error-handling/file-operations/failure-reported-as-success]`.

Each finding must contain:

- A heading with its stable ID and short title.
- **Location:** one primary `path/to/file:line` and any related locations needed to trace the defect.
- **Severity:** Critical | High | Medium | Low.
- **Confidence:** High | Medium | Low.
- **Defect:** what is wrong and the incorrect resulting behavior.
- **Trigger:** the input, sequence, state, environment, or interleaving that activates it.
- **Evidence / verification:** the traced path, reproduction, command, refutation attempt, and any remaining assumptions.
- **Suggested fix:** the change described in prose; apply no diff.

Use this top-level structure for `BUG_FINDINGS.md`, omitting only severity sections that contain no findings:

```markdown
# Bug Findings

## Critical

### [stable-id] Short title

...

## High

...

## Medium

...

## Low

...

## Summary
```

Populate the final report section as follows:

- **Summary:** finding counts by severity, finding counts by confidence, and a severity-confidence matrix. Use a matrix table with severity rows and `High`, `Medium`, and `Low` confidence columns; include no row or column totals, no affected-file list, and nothing else. Everything else the audit established — status, scope resolution, coverage counts, candidate dispositions, verification performed, exclusions, and limitations — belongs in the chat summary, never in `BUG_FINDINGS.md`.

End the chat response with an inline summary containing the audit status and, for a Partial audit, each unmet condition; finding counts by severity and confidence; candidate disposition counts; included, inspected, and skipped file and flow counts; the affected-file count and most important affected files; every unverified candidate with its location, suspected risk, and blocker; any baseline substitution; skipped areas, unavailable tooling, and blocked verification; the result of the final worktree comparison and the snapshot-manifest digest; top findings; and a link to `BUG_FINDINGS.md` when it was written. This summary is the only place the audit trail is reported, so it must be complete enough to reproduce every count it states. If no findings survive, say so plainly and summarize coverage and limitations without claiming the codebase is universally bug-free.
