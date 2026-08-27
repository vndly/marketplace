# AI marketplaces

Provider-native skills for Claude Code and Codex live in separate packages so each skill can use its provider's tools, conventions, and metadata directly.

| Provider    | Marketplace catalog                | Package                      | Version source               |
| ----------- | ---------------------------------- | ---------------------------- | ---------------------------- |
| Claude Code | `.claude-plugin/marketplace.json`  | `plugins/claude-code/common` | `.claude-plugin/plugin.json` |
| Codex       | `.agents/plugins/marketplace.json` | `plugins/codex/common`       | `.codex-plugin/plugin.json`  |

Both packages carry `apocalypse-bug-review`, `delta-review`, and `grill-me` — same skill names and expected outcomes, but separate `SKILL.md` files. They are released independently: the Claude Code package is at `1.8.0`, while the Codex package starts at `0.1.0`.

`mp3-tags` and `youtube-mp3` ship **for Claude Code only, on purpose**. Both are thin wrappers around a bundled script, and their value depends on the script running unattended: Claude Code puts the plugin's `bin/` on `PATH` and lets `youtube-mp3` install its own `yt-dlp` and `deno`. Under Codex's sandbox every network fetch and every write outside the workspace needs an up-front approval, and a skill may not install its own dependencies — so the Codex ports were mostly instructions about requesting authorization, wrapped around a script that refuses to do the one thing that made the skill worth having. Rather than maintain a worse second copy, audio work stays on Claude Code.

## Install for Claude Code

```text
/plugin marketplace add vndly/marketplace
/plugin install common@vndly
```

## Install for Codex

```sh
codex plugin marketplace add vndly/marketplace
codex plugin add common@vndly-codex
```

For local development from this checkout:

```sh
codex plugin marketplace add .
codex plugin add common@vndly-codex
```

Start a new conversation after installing or updating a plugin so the provider reloads its skills.
