---
name: grill-me
description: Interview the user relentlessly about a plan or design, one question at a time, until every branch of the decision tree is resolved and their constraints and priorities are explicit. Use when the user wants to stress-test a plan, think through a half-formed idea, surface edge cases and unstated assumptions, or mentions "grill me".
---

Interview the user relentlessly about every aspect of their plan until you reach a shared understanding.

First, establish what the user is optimizing for and what is fixed: the constraint they will not trade away, the budget (time, effort, complexity), and what "done" looks like. Judge every later option against those.

Map the plan as a design tree: every decision branches into the decisions that hang off it. Ask the highest-fanout question first — the one whose answer constrains or invalidates the most other decisions. Each answer reshapes the tree: a settled decision pushes the frontier outward and unblocks the questions that depended on it. Recompute the frontier after every answer and pick again. Cheap-to-reverse details go last, or not at all.

Ask questions one at a time. For each question:
- Present your recommended answer first, with a brief justification, then list alternatives
- Provide 2-3 mutually exclusive options that differ in consequence, not wording; say what each costs or rules out
- Name the silent default: what the user would get if the question were never asked
- When `request_user_input` is available, call it with exactly one question. Put the recommended option first, append `(Recommended)` to its label, keep the header to 12 characters or fewer, and use each option's description to explain its impact. Do not add an `Other` option; the tool supplies the free-form choice.
- When `request_user_input` is unavailable, ask the same single question directly in prose, with the stakes, silent default, recommendation, and options. Explicitly allow a free-form answer, then end the turn and wait.

When the user rejects your recommendation, say what that reveals about their priorities and which other decisions it changes. Propagate it before moving on.

Track decisions as you go — if a later answer invalidates an earlier one, flag the conflict and revisit. Restate the resolved set compactly every few decisions.

Never ask the user for a fact you can find yourself. When a frontier question depends on one, use available read-only tools for narrow lookups and, when authorized and available, a collaboration subagent for broad independent research. A pending lookup is an unsettled prerequisite: defer only its downstream questions and continue elsewhere on the frontier. If two options are equivalent for the user's purposes, pick one and say so.

Stop when remaining questions no longer change what gets built. For each skipped inconsequential branch, state the assumption it locks in; nothing is silently assumed, but not every branch needs interrogation. Then write out the resolved design and the decisions it rests on, and wait for the user to confirm the shared understanding before acting on it.
