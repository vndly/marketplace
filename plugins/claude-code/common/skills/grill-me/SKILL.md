---
name: grill-me
description: Interview the user relentlessly about a plan or design, one question at a time, until every branch of the decision tree is resolved and their constraints and priorities are explicit. Use when the user wants to stress-test a plan, think through a half-formed idea, surface edge cases and unstated assumptions, or mentions "grill me".
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding.

First, establish what I'm optimizing for and what's fixed: the constraint I won't trade away, the budget (time, effort, complexity), and what "done" looks like. Judge every later option against those.

Map the plan as a design tree: every decision branches into the decisions that hang off it. Ask the highest-fanout question first — the one whose answer constrains or invalidates the most other decisions. Each answer reshapes the tree: a settled decision pushes the frontier outward and unblocks the questions that depended on it. Recompute the frontier after every answer and pick again. Cheap-to-reverse details go last, or not at all.

Ask questions one at a time. For each question:

- Present your recommended answer first, with a brief justification, then list alternatives
- Provide 2-4 concrete options that differ in consequence, not in wording — say what each one costs or rules out
- Name the silent default: what we'd end up with if this were never asked
- Use the AskUserQuestion tool so I can select or override; the option list is never closed — the tool's built-in `Other` always lets me answer in my own words, so don't add an `Other` option yourself

When I reject your recommendation, say what that tells you about my priorities and which other decisions it changes. Propagate it before moving on.

Track decisions as you go — if a later answer invalidates an earlier one, flag the conflict and revisit. Restate the resolved set compactly every few decisions.

Never ask me for a fact you can find yourself. When a frontier question depends on one, go get it: delegate broad or open-ended lookups to a sub-agent, read narrow ones directly. Don't block on either — a pending lookup is just an unsettled prerequisite, so only the questions downstream of it wait. Ask the rest of the frontier now. If two options are equivalent for my purposes, pick one and tell me.

Stop when remaining questions no longer change what gets built. Whatever you skip as inconsequential, say so and state the assumption it locks in — nothing gets silently assumed, but not every branch has to be interrogated either. Then write out the resolved design and the decisions it rests on, and wait for me to confirm we've reached a shared understanding before acting on any of it.
