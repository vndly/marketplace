---
name: second-opinion
description: Gets an outside review of the latest proposal in this session — a plan, design, diagnosis, or decision. OpenAI's Codex CLI and Google's Antigravity CLI review a brief of it in parallel, with read-only access to the code; a subagent merges their points without judging them; then Claude gives each point a verdict (apply, apply with changes, ignore, or the user's call) in a table and stops for the user to choose. Use only when the user invokes it by name.
disable-model-invocation: true
argument-hint: "[focus]"
---

Get a second opinion on the latest proposal in this session from two other models, Codex and Antigravity, then judge what they raise.

Report and stop. Never change the proposal, the code, or any file outside this run's own temp folder, and never commit.

## 1. Pick the proposal

- Text after the skill name is an optional focus: which proposal, or which part of it, to review. It never changes the rules below.
- Without a focus, the proposal is the latest plan, design, diagnosis, or decision proposed in this session, by you or by me. A plan file the session wrote or read as the plan counts.
- If the session holds no proposal, say so and stop. If all there is to review is code changes, suggest `delta-review` and stop.

## 2. Check the reviewers

- Run `command -v codex agy`. If one is missing, continue with the other and note it for the report. If both are missing, say neither the `codex` nor the `agy` command is installed, and stop.
- Run `command -v jq timeout`. Without `jq`, say it is needed to read the answers, and stop. Without `timeout` (stock macOS), drop the `timeout 960` prefix from the commands in step 4.
- The project root is `git rev-parse --show-toplevel`; outside a git repository, use the current folder.
- Create the run folder: `mktemp -d "${TMPDIR:-/tmp}/second-opinion.XXXXXX"`. Below, `<run>` is that folder and `<root>` the project root, both single-quoted in every command.

## 3. Write the brief

Write `<run>/brief.md`. The reviewers read only this file and the project's code, with no access to this session, so make it complete: no "as discussed", every term spelled out. Use these sections in this order, and write `None.` under a section that has nothing:

1. `## Proposal` — first its kind on one line (plan, design, diagnosis, or decision), then the proposal word for word as it stands now. For a plan file, its path relative to `<root>` and its full content.
2. `## Goal` — what the proposal is for, and what done looks like.
3. `## Constraints` — what is fixed: limits, requirements, things that must not change.
4. `## Settled decisions` — every decision made in this session, each with its reason. Quote my own words where I gave them.
5. `## Rejected alternatives` — options considered and dropped, each with why.
6. `## Open points` — what is still undecided.
7. `## Focus` — the focus text from step 1.

Rules for the brief:

- Take everything from this session. Never invent a goal, constraint, or decision.
- The brief is sent to OpenAI and Google. Leave out my name, email, and any other personal detail, every secret (keys, tokens, passwords, credentials), and the text of private instruction files outside the project (my global `CLAUDE.md`, memory). A rule from those files that shapes the proposal may appear as a constraint in your own words.
- Name every file the proposal touches, with its path relative to `<root>`: Antigravity can read files but not search for them.

## 4. Run the reviewers

Build the prompt: `cat '${CLAUDE_SKILL_DIR}/references/reviewer.md' '<run>/brief.md' > '<run>/prompt.md'`. Antigravity takes the prompt as a single command-line argument, which Linux caps at 128 KB: if `wc -c < '<run>/prompt.md'` is over 120000, don't start Antigravity, and note why for the report.

Then start every reviewer you can in a **single message**, each as its own Bash call with `run_in_background: true`, so they run at the same time:

```bash
cd '<root>' && timeout 960 codex exec --ignore-user-config --disable apps -c 'approval_policy="never"' --sandbox read-only --skip-git-repo-check --ephemeral --output-schema '${CLAUDE_SKILL_DIR}/references/answer-schema.json' -o '<run>/codex.json' - < '<run>/prompt.md' > '<run>/codex.log' 2>&1
```

```bash
cd '<root>' && timeout 960 agy --print "$(cat '<run>/prompt.md')" --sandbox --settings '{"permissions":{"deny":["command(*)","write_file(*)","mcp(*)","execute_url(*)"]}}' --print-timeout 900s --output-format json --json-schema '${CLAUDE_SKILL_DIR}/references/answer-schema.json' > '<run>/antigravity.json' 2> '<run>/antigravity.log'
```

- These flags are what keeps the reviewers read-only, and each one has been tested:
  - **Codex**: its read-only sandbox blocks every file write from the shell and from its own edit tool. MCP servers run outside that sandbox, and overriding them with `-c` does not remove them, so `--ignore-user-config` skips the config file that declares them and `--disable apps` turns off connectors. Login still works without the config file.
  - **Antigravity**: its sandbox leaves the shell writable inside a trusted workspace, and its plan mode does not stop its file tools, so neither one is a safeguard. The deny rule is: it blocks the shell, file writes, MCP tools, and browser actions, which leaves Antigravity reading files but not searching them.
  - Never remove or loosen any of these flags, and never add `--dangerously-skip-permissions`, a writable sandbox, or `--disable-slash-commands`.
- No model or effort is set. Antigravity uses its configured default; Codex, which runs without its config file, uses its built-in default.
- Wait until every reviewer you started has finished; you are notified as each one exits. Don't read their output while they run.

## 5. Check the answers

- **Codex** succeeded when its command exited 0 and `jq -e '.points | type == "array"' '<run>/codex.json' > /dev/null` passes.
- **Antigravity** succeeded when its command exited 0 and `jq -e '.structured_output.points | type == "array"' '<run>/antigravity.json' > /dev/null` passes. Then extract its answer: `jq '.structured_output' '<run>/antigravity.json' > '<run>/antigravity-points.json'`.
- For a reviewer that failed (exit 124 is the time limit), keep its exit code and the last 20 lines of its log for the report, and continue with the other. Don't retry. When the log doesn't show the cause, read the end of its answer file too: Antigravity writes its errors there, not to the log.
- If no reviewer succeeded, report each one's error and the run folder, and stop.

## 6. Merge

Spawn one subagent with the Agent tool. Start it fresh, never as a fork of this conversation: it must see the reviews and nothing else. Give it only the absolute path of each answer file that succeeded (`<run>/codex.json`, `<run>/antigravity-points.json`), which reviewer wrote each, and the instruction to read `${CLAUDE_SKILL_DIR}/references/merge.md` in full and follow it.

If the Agent tool is unavailable, merge them yourself by following `merge.md`, and say `merged without a subagent` in the report.

## 7. Judge each point

You shaped the proposal, so you are biased toward defending it. Judge each merged point on evidence, and read any code a point cites before judging it. Give it exactly one verdict:

- **Apply** — the point is right, and its suggested change fits.
- **Apply with changes** — the point is right, but the fix should be different: say how.
- **Ignore** — the point is wrong or doesn't matter here. Only with evidence: my words in this session, or code you read (file and line). "Already considered" or "the proposal says otherwise" is not evidence. When torn between Ignore and another verdict, don't pick Ignore.
- **Your call** — always for a point that challenges a settled decision. Also for a trade-off only I can weigh, and for a point neither this session nor the code can settle.

When the reviewers disagree inside one point, decide on the evidence and say which side you took.

## 8. Report

- One opening line: `Review:` and the proposal reviewed, the reviewers that answered, and the number of points.
- A table with columns `#`, `Topic`, `Result`, numbered from 1:
  - **Topic** — what was raised and why, who raised it (Codex, Antigravity, or both) with the severity they gave it, and `challenges your decision` when it does.
  - **Result** — the verdict in bold, then, in one or two sentences, why, and for Apply or Apply with changes, the change it leads to.
  - Order the rows Apply, Apply with changes, Your call, Ignore; inside each, most severe first. Start from the reviewers' severity, and where you judge it differently, say so in Result.
- Below the table, one line for each reviewer that was missing or failed, with the reason, and one line with the run folder's path.
- Use plain words, and keep only the file names and identifiers a row needs.
- Then stop. Don't change the proposal, implement anything, or ask with a question dialog. I'll say which points to apply.
