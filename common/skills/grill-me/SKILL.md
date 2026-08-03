---
name: grill-me
description: Interview the user relentlessly about a plan or design, one question at a time, until every branch of the decision tree is resolved and their constraints and priorities are explicit. Use when the user wants to stress-test a plan, think through a half-formed idea, surface edge cases and unstated assumptions, or mentions "grill me".
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding.

First, establish what I'm optimizing for and what's fixed: the constraint I won't trade away, the budget (time, effort, complexity), and what "done" looks like. Judge every later option against those.

Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. Ask the highest-fanout question first — the one whose answer constrains or invalidates the most other decisions. Cheap-to-reverse details go last, or not at all.

Ask questions one at a time. For each question:
- Present your recommended answer first, with a brief justification, then list alternatives
- Provide 2-4 concrete options that differ in consequence, not in wording — say what each one costs or rules out
- Name the silent default: what we'd end up with if this were never asked
- Use the AskUserQuestion tool so I can select or override; the option list is never closed — the tool's built-in `Other` always lets me answer in my own words, so don't add an `Other` option yourself

When I reject your recommendation, say what that tells you about my priorities and which other decisions it changes. Propagate it before moving on.

Track decisions as you go — if a later answer invalidates an earlier one, flag the conflict and revisit. Restate the resolved set compactly every few decisions.

Don't ask what you can answer yourself: if the codebase settles it, go read it. If two options are equivalent for my purposes, pick one and tell me.

Stop when remaining questions no longer change what gets built, then write out the resolved design and the decisions it rests on.