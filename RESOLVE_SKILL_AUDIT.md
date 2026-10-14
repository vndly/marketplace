# Audit: `resolve` skill (Claude Code)

- **Date:** 2026-10-14
- **Target:** `plugins/claude-code/common/skills/resolve/SKILL.md` (40 lines) and `plugins/claude-code/common/.claude-plugin/plugin.json`
- **Platform:** Claude Code (`.claude-plugin` manifest, `disable-model-invocation`, `AskUserQuestion`)
- **Method:** static reading and paper dry-runs only; nothing was executed and nothing was edited. Every finding comes from reading the files and tracing scenarios, not from running the skill.
- **Coverage:** 37 scenarios traced, 23 pass. The code reviewer was skipped because the skill has no scripts.
- **Verification:** 17 candidates, each challenged by a skeptic. 5 refuted, 1 rejected, 1 narrowed, 2 recast as improvements, 0 demoted to suspicions, 11 reported. One suspicion was dropped because the finding it qualified was refuted.

**Result:** 0 critical, 7 warnings, 4 improvements (0 high) across 2 files; 2 unverified suspicions.

The skill loads and is invoked as intended. Its frontmatter is valid, the name is free of collisions, and keeping it user-only is right for a skill that can commit, push or delete.

## Defects

| File             | Line   | Severity | Category | Evidence — scenario → behavior → why it is wrong                                                                                                                                                       | Suggested fix |
| :--------------- | :----- | :------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------ |
| resolve/SKILL.md | 33, 36 | Warning  | Logic    | For a non-trivial fix, line 33 treats the choice as the go-ahead while line 36 keeps the user's rule that a plan needs explicit approval, so the agent either skips the plan or stops partway through. | D4            |
| resolve/SKILL.md | 28–29  | Warning  | Logic    | Nothing checks the chosen answers against each other, so "revert the refactor" plus "keep the refactor and add tests" is settled by list order instead of by the user.                                 | D5            |

## Unverified suspicions

| File             | Line  | Risk                                                                                                                                                                                             | Check that would settle it                                                                                      |
| :--------------- | :---- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| resolve/SKILL.md | 11–12 | Points settled after that reply, by later turns or by an earlier run interrupted mid-work that left no report, get asked again, and choosing them again could repeat a commit, push or deletion. | Interrupt a run after it has carried out some answers, run the skill again, and see which points it asks about. |
| resolve/SKILL.md | 11    | "Your replies" may include text written between tool calls, so a passing "⚠️ build failed, retrying" line could be taken as a point.                                                             | Check whether Claude Code shows mid-turn text to the model as separate assistant messages.                      |

## Replacement text

**D1.** Replace line 35 with:

> - If an answer cannot be carried out as chosen — what it names is gone, or its change fails verification — do not improvise a substitute: undo that option's partial edits, skip every option that depends on it, including any commit, push, or deletion, finish the independent ones, and report what failed and what you skipped.

**D2.** Replace the first sentence of line 33 with:

> Carry out every chosen option in one pass: changes first, then the checks I chose and your usual verification, then any commit, push, or deletion; otherwise keep list order.

**D3.** Replace line 14 with:

> - If no reply qualifies, say there is nothing to resolve and stop. If the reply with the points survives only in a summary of earlier conversation, say so, list the points you can recover from it, and confirm them with me in the first question call.

**D4.** Append to line 33:

> Choosing an option also approves the plan its description lays out; if carrying it out needs a decision the option did not cover, do not guess: finish the others and report that decision as a new point.

**D5.** Replace line 29 with:

> - Change nothing until every question is answered. Then check the answers against each other; if two conflict or one makes another moot, ask one follow-up naming both, and carry out neither until I answer.

**I1.** Insert after line 28:

> - If `AskUserQuestion` is unavailable, ask all the questions in one message, numbered, with their options and your recommendation; say I can answer in my own words, then end the turn and wait.

**I2.** Replace line 40 with:

> Report the outcome the way my instructions define; if they define none, give one line per point saying what was done, left, or could not be done. Give each point that needed no question one plain line, not starting with 🚨, ⚠️, ✋, or 🔍, unless it is an action only I can take that is still open. Write any new points this work raises as lines starting with 🚨, ⚠️, ✋, or 🔍 so a later run of this skill can find them.

## Other platform copies

The Codex copy (`plugins/codex/common/skills/resolve/SKILL.md`) and the Antigravity copy (`plugins/antigravity/common/skills/resolve/SKILL.md`) have the same wording on lines 18, 29, 33–35 and 40, so all 7 warnings apply to them too. Both already have the question-tool fallback (I1). The description change (line 3) should not go into the Antigravity copy, where no setting enforces user-only invocation and the sentence it replaces still does that job.
