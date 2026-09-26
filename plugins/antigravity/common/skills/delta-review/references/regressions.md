# Subagent B brief — regressions

Your question is not "is this code good" but "**what worked before that may not work now**". Work through all five passes; each is independently reportable.

**Pass 1 — pre-image behavior diff.** Classify the change set first: `git diff --name-status -M` over exactly the range you were given — `<base>` alone for the working-tree forms, `A..B` or `R HEAD` for the committed ones, with the same `-- <paths>` restriction when the caller gave paths. Comparing `<base>` against the working tree when the review targets a committed range classifies the wrong files. Everything below reads from `<base>`, which is **not** `HEAD` whenever a revision argument was given. Then read each file's previous version and compare behavior, not text:

- **modified** (`M`) — `git show <base>:<path>`
- **renamed or copied** (`R`/`C`) — `git show <base>:<oldpath>`, taking the old path from the status line; `<path>` does not exist at the base and the command will fail
- **added** (`A`), and every untracked file — no pre-image exists, so there is no regression to find here; leave it to Subagent A and do not spend turns proving the file is new
- **deleted** (`D`) — read `git show <base>:<path>` and treat everything it did as removed behavior, then check its callers in Pass 2
- **unmerged** (`U`) — skip it; the orchestrator already reported it as an unresolved conflict

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

These are mechanical triggers: do not second-guess whether the edit looks intentional — it always does. Report each as an **unverified suspicion**, quoting the before and after, with the check `the author states why this test now asserts less`. Ordinary test edits — new cases, renames, fixture churn, added assertions — are **not** findings.

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
