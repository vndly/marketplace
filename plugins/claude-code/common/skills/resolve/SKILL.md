---
name: resolve
description: Walk the user through the 🚨/⚠️/✋/🔍 attention points in Claude's latest reply that has them — one question per point that needs a decision — then carry out every answer in one pass. Use only when the user invokes it by name.
disable-model-invocation: true
---

Help me resolve the attention points from your latest reply: ask me about each one that needs a decision, then carry out what I chose.

## Find the points

- Walk back from this request through your replies to me and take the most recent one that contains attention points: list items, or lines, that start with 🚨, ⚠️, ✋, or 🔍. Emojis mid-sentence, in tables, in code blocks, in my messages, or in tool output are not points.
- Never walk past the final report of an earlier run of this skill: points in that report are the ones to resolve, and points before it were already resolved.
- Take the points from that one reply only, in their original order.
- If no reply qualifies, say there is nothing to resolve and stop.

## Pick the points to ask about

Ask about a point only when my answer changes what you will do: a fix to make or skip, a choice between approaches, a go/no-go such as approving a plan, or running a check that was not run. A point that only states a fact — something done, left out, assumed, or an action only I can take — gets no question; keep it for the final report.

If no point needs a question, go straight to the final report.

## Ask

- One question per point, in list order, up to 4 questions per `AskUserQuestion` call.
- Restate the point in plain words — what is wrong or open, and why it matters — instead of quoting it. Keep the header to 12 characters or fewer.
- Give 2–4 options that differ in what you will do. Put the recommended option first and append `(Recommended)` to its label, using the point's own recommendation when it has one. Each description says what the option does and what it costs.
- Offer a "leave it" option only when doing nothing is a real choice.
- Do not add an `Other` option; the tool supplies one. Follow a free-text answer as written; if it is unclear, ask a follow-up about that point alone.
- Change nothing until every question is answered.

## Carry out the answers

- Carry out every chosen option in one pass, in list order. Choosing an option is my go-ahead for exactly what it says, including commits, pushes, or deletions it names; anything beyond it still needs my permission.
- Drop the points I chose to leave.
- If an answer cannot be carried out as chosen, do not improvise a substitute: finish the others and report it.
- My usual rules still apply while you work, including verification.

## Report

Report the outcome the way my instructions define. Add one line for each point that needed no question. Any new points this work raises stay in the report for a later run of this skill.
