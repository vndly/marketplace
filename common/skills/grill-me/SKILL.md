---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
disable-model-invocation: true
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding.

Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

Ask the questions one at a time. For each question:
- Provide a set of possible answers to choose from
- Provide your recommended answer and justify it
- Use the AskUserQuestion tool to let me choose between the options or provide my own answer

If a question can be answered by exploring the codebase, explore the codebase instead.