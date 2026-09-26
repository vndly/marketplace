# Agent A brief — new defects

Review the post-change code against this taxonomy. Tier A and Tier B findings are usually **Critical** or **Warning**; Tier C only when it demonstrates a real behavioral defect. Skip every unmerged path you were given; the orchestrator already reported it.

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
