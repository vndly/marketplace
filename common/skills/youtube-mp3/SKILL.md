---
name: youtube-mp3
description: Download the MP3 audio from a YouTube (or any yt-dlp-supported) video URL. Use whenever the user gives a video URL and wants the audio — "download the audio", "get the mp3", "youtube to mp3", "download this song/track". Auto-installs yt-dlp and the deno JS runtime if they are missing.
---

# YouTube → MP3

Downloads best-quality MP3 audio from a video URL using the bundled `download-audio.sh`,
which also installs any missing dependencies.

## How to run

```bash
download-audio.sh "<VIDEO_URL>" [OUTPUT_DIR]
```

> If `download-audio.sh` isn't found on PATH (e.g. just after a plugin update), it's
> bundled in this plugin's `bin/` directory — run it from there.

- `<VIDEO_URL>` — required. The YouTube (or other yt-dlp-supported) URL.
- `[OUTPUT_DIR]` — optional. Defaults to `~/Downloads`.

The script prints the absolute path of the resulting `.mp3` on its **last stdout line**.
Everything else (status, install messages) goes to stderr. Report that path to the user.

## What the script does

1. Requires `ffmpeg` (errors with install guidance if absent — it needs root).
2. Installs `yt-dlp` to `~/.local/bin` if missing.
3. Installs the `deno` JS runtime to `~/.deno` if missing. **This is required** —
   yt-dlp uses it to solve YouTube's signature challenge; without it, downloads
   fail with `HTTP 403 Forbidden`.
4. Extracts best-quality audio and converts to MP3 (`--audio-quality 0`, ~245 kbps VBR).

Re-running is safe and idempotent: already-installed tools are reused.

## Verify (optional)

```bash
ffprobe -v error -show_entries format=duration,bit_rate,format_name \
  -of default=noprint_wrappers=1 "<output.mp3>"
```

## Notes

- Scope is specifically **MP3**. To keep YouTube's native audio without re-encoding,
  drop `--audio-format mp3` from the yt-dlp call (that's a different need).
- On failure with a 403 or "no JavaScript runtime" error, confirm deno is present
  (`~/.deno/bin/deno --version`); the script installs it, but a stale PATH can hide it.
