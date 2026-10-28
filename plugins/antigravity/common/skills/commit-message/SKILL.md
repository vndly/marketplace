---
name: commit-message
description: Reply with a short, one-line commit message for all uncommitted changes in the current git repository, and nothing else. Use when the user asks for a commit message — "commit message", "suggest a commit message", "what should I commit this as". Not for committing: when the user asks to commit, don't use this skill.
---

Give the user a commit message for their uncommitted changes.

- Read every uncommitted change: staged, unstaged, and new files.
- Write one line in the imperative mood, all lowercase, at most 50 characters, with no trailing period — e.g. `add login form validation`.
- Describe the main change. No type prefix such as `feat:`, `fix:`, or `chore:`, no scope, no body.
- Reply with the message only: no quotes, backticks, intro, or explanation.
- If there are no uncommitted changes, reply `No uncommitted changes.` If this is not a git repository, reply `Not a git repository.`
