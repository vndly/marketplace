---
name: youtube-mp4
description: Download a YouTube (or any yt-dlp-supported) video as an MP4 at 720p, or the closest resolution available. Use whenever the user gives a video URL and wants the video itself — "download the video", "get the mp4", "youtube to mp4", "save this video". Auto-installs yt-dlp and the deno JS runtime if they are missing.
---

# YouTube → MP4

Downloads a video as an MP4 from a video URL using the bundled `download-video.sh`, which also installs any missing dependencies.

## How to run

```bash
download-video.sh "<VIDEO_URL>" [OUTPUT_DIR]
```

> If `download-video.sh` isn't found on PATH (e.g. just after a plugin update), it's bundled in this plugin's `bin/` directory — run it from there.

- `<VIDEO_URL>` — required. The YouTube (or other yt-dlp-supported) URL.
- `[OUTPUT_DIR]` — optional. Defaults to `~/Downloads`.

The script prints the absolute path of the resulting `.mp4` on its **last stdout line**. Everything else (status, install messages) goes to stderr. Report that path to the user.

## What the script does

1. Requires `ffmpeg` (errors with install guidance if absent — it needs root).
2. Installs `yt-dlp` to `~/.local/bin` if missing.
3. Installs the `deno` JS runtime to `~/.deno` if missing. **This is required** — yt-dlp uses it to solve YouTube's signature challenge; without it, downloads fail with `HTTP 403 Forbidden`.
4. Picks the largest resolution up to 720p, or the smallest above it if nothing that small exists. Widescreen videos get their 720p tier (e.g. 1280×534) and vertical videos 720×1280.
5. Prefers H.264 video + AAC audio so the MP4 plays everywhere, and merges the streams into an MP4 without re-encoding.
6. Downloads only the linked video, even when the URL carries a playlist (`&list=`). A playlist- or channel-only URL downloads just its first entry.

Re-running is safe and idempotent: already-installed tools are reused.

## Verify (optional)

```bash
ffprobe -v error -show_entries stream=codec_name,width,height \
  -of default=noprint_wrappers=1 "<output.mp4>"
```

## Notes

- Scope is specifically **MP4 at 720p**. For audio only, use the `youtube-mp3` skill instead.
- On failure with a 403 or "no JavaScript runtime" error, confirm deno is present (`~/.deno/bin/deno --version`); the script installs it, but a stale PATH can hide it.
