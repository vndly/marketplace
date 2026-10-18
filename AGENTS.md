# Marketplace

One plugin, `common`, published for three tools. Each tool has its own copy of the skills:

| Tool        | Plugin directory             | Manifest                           |
| ----------- | ---------------------------- | ---------------------------------- |
| Claude Code | `plugins/claude-code/common` | `.claude-plugin/plugin.json`       |
| Codex       | `plugins/codex/common`       | `.codex-plugin/plugin.json`        |
| Antigravity | `plugins/antigravity/common` | `plugin.json` (at the plugin root) |

## Claude Code is the master

- Make every change in the Claude Code copy first, then mirror it to the Codex and Antigravity copies in the same turn. Don't wait to be asked.
- Mirror means port, not copy. Keep the same rules and structure, and adapt only what the tool needs:
  - Wording: "me / my" becomes "the user / their".
  - Frontmatter: drop `argument-hint`; the description may be reworded for the tool.
  - Question tool: `AskUserQuestion` becomes `request_user_input` (Codex) or `ask_question` (Antigravity), with a numbered-message fallback when the tool is unavailable.
  - Codex only: each user-invoked skill has `agents/openai.yaml` (display name, short description, default prompt, `allow_implicit_invocation`). Create or update it when the skill changes.
- Claude-only skills stay Claude-only: `youtube-mp3`, `youtube-mp4`, `mp3-tags` (they depend on `bin/`). `frontend-design` exists only in the Codex and Antigravity copies.
- After mirroring, diff the three skill folders (`diff -rq`) and confirm every remaining difference is one of the adaptations above.

## Versions

- All three manifests carry the same version. Bump them together, in the same change, to the same number. Never leave them on different versions.
- New skill or new behavior: bump the minor (`2.9.2` → `2.10.0`). Wording fix or small tweak to an existing skill: bump the patch (`2.9.2` → `2.9.3`).
- Bump once per change set, not once per file.
- Don't edit the marketplace indexes (`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`) for a version bump; they don't hold the version.
