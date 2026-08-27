#!/usr/bin/env bash
#
# Download best-quality MP3 audio from a YouTube (or any yt-dlp-supported) URL.
# Auto-installs missing dependencies (yt-dlp, deno) into the user's home dir.
#
# Usage: download-audio.sh <video-url> [output-dir]
#   <video-url>   Required. The YouTube (or other supported) URL.
#   [output-dir]  Optional. Defaults to ~/Downloads.
#
# Prints the absolute path of the resulting .mp3 on the final line.

set -euo pipefail

URL="${1:-}"
OUT_DIR="${2:-$HOME/Downloads}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <video-url> [output-dir]" >&2
  exit 2
fi

LOCAL_BIN="$HOME/.local/bin"
DENO_HOME="$HOME/.deno"
# Make home-local installs discoverable regardless of the caller's PATH.
export PATH="$DENO_HOME/bin:$LOCAL_BIN:$PATH"

need() { command -v "$1" >/dev/null 2>&1; }

# ffmpeg is required for audio extraction and generally needs root to install,
# so we don't attempt it automatically — fail with clear guidance instead.
if ! need ffmpeg; then
  echo "ERROR: ffmpeg is required but not installed." >&2
  echo "Install it, e.g.:  sudo apt-get install -y ffmpeg" >&2
  exit 1
fi

# curl is needed to fetch yt-dlp / deno if they're missing.
if ! need curl; then
  echo "ERROR: curl is required to auto-install yt-dlp/deno but is not installed." >&2
  exit 1
fi

# deno is a JS runtime yt-dlp uses to solve YouTube's signature challenge.
# Without it, downloads fail with HTTP 403 Forbidden.
if ! need deno; then
  echo "Installing deno (JS runtime for yt-dlp)..." >&2
  curl -fsSL https://deno.land/install.sh | DENO_INSTALL="$DENO_HOME" sh >/dev/null 2>&1 || true
  hash -r
  if ! need deno; then
    echo "ERROR: failed to install deno automatically. See https://deno.land and re-run." >&2
    exit 1
  fi
fi

# yt-dlp: install the self-contained standalone binary if missing.
if ! need yt-dlp; then
  echo "Installing yt-dlp..." >&2
  mkdir -p "$LOCAL_BIN"
  curl -fsSL -o "$LOCAL_BIN/yt-dlp" \
    https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp
  chmod +x "$LOCAL_BIN/yt-dlp"
  hash -r
fi

mkdir -p "$OUT_DIR"
echo "Downloading MP3 to: $OUT_DIR" >&2

# -x               extract audio
# --audio-format   convert to mp3
# --audio-quality 0  best VBR quality
# --quiet --no-warnings  keep stdout to just the --print path (status/warnings -> stderr)
# --print after_move:filepath  emit the final file path on stdout
yt-dlp \
  -x --audio-format mp3 --audio-quality 0 \
  --quiet --no-warnings --no-progress \
  --print after_move:filepath \
  -P "$OUT_DIR" \
  -o "%(title)s.%(ext)s" \
  -- "$URL"
