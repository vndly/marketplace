---
name: resolve
description: Walk the user through the 🚨/⚠️/✋/🔍 attention points in the agent's latest reply that has them — one question per point that needs a decision — then carry out every answer in one pass. Use only when the user invokes it by name.
---

Help the user resolve the attention points from your latest reply: ask about each one that needs a decision, then carry out what they chose.

## Find the points

- Walk back from this request through your replies to the user and take the most recent one that contains attention points: list items, or lines, that start with 🚨, ⚠️, ✋, or 🔍. Emojis mid-sentence, in tables, in code blocks, in the user's messages, or in tool output are not points.
- Never walk past the final report of an earlier run of this skill: points in that report are the ones to resolve, and points before it were already resolved.
- Take the points from that one reply only, in their original order.
- If no reply qualifies, say there is nothing to resolve and stop.

## Pick the points to ask about

Ask about a point only when the user's answer changes what you will do: a fix to make or skip, a choice between approaches, a go/no-go such as approving a plan, or running a check that was not run. A point that only states a fact — something done, left out, assumed, or an action only the user can take — gets no question; keep it for the final report.

If no point needs a question, go straight to the final report.

## Ask

- One question per point, in list order.
- Start the question text with the point's own emoji (🚨, ⚠️, ✋, or 🔍), then restate the point in plain words — what is wrong or open, and why it matters — instead of quoting it.
- Give 2–4 options that differ in what you will do. Put the recommended option first, using the point's own recommendation when it has one, and say what each option does and what it costs.
- Offer a "leave it" option only when doing nothing is a real choice.
- When `request_user_input` is available, put as many questions in each call as it accepts, up to 4. Append `(Recommended)` to the recommended label, keep each header to 12 characters or fewer, and explain each option in its description. Do not add an `Other` option; the tool supplies the free-form choice.
- When `request_user_input` is unavailable, ask all the questions in one message, numbered, with their options and recommendations. Explicitly allow free-form answers, then end the turn and wait.
- Follow a free-form answer as written; if it is unclear, ask a follow-up about that point alone.
- Change nothing until every question is answered. Then check the answers against each other; if two conflict or one makes another moot, ask one follow-up naming both, and carry out neither until the user answers.

## Carry out the answers

- Carry out every chosen option in one pass, in list order. Choosing an option is the user's go-ahead for exactly what it says, including commits, pushes, or deletions it names; anything beyond it still needs their permission. Choosing an option also approves the plan its description lays out; if carrying it out needs a decision the option did not cover, do not guess: finish the others and report that decision as a new point.
- Drop the points the user chose to leave.
- If an answer cannot be carried out as chosen, do not improvise a substitute: finish the others and report it.
- The user's usual instructions still apply while you work, including verification.

## Report

Report the outcome the way the user's instructions define. Add one line for each point that needed no question. Any new points this work raises stay in the report for a later run of this skill.
