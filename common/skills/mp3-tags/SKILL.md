---
name: mp3-tags
description: Set an MP3 file's ID3 tags from its "[ARTIST] - [TITLE].mp3" filename — fills only Artist and Title and empties every other tag field. Use when given the path to a single MP3 whose tags should be normalized from its filename. Validates the name first, backs the file up, and restores it on failure.
---

# mp3-tags

Normalizes the tags of one MP3 file whose name follows `[ARTIST] - [TITLE].mp3`.
It sets **only** Artist (`TPE1`) and Title (`TIT2`) and empties every other tag
field (all other ID3v2 frames, ID3v1, and any APEv2 tag). The file is backed up
before any change and restored automatically if the process fails.

## Input
The path to one `.mp3` file. The filename must match `[ARTIST] - [TITLE].mp3`:
ARTIST is everything before the **first** ` - `, TITLE is everything after (so a
title may itself contain ` - `).

## How to run
Run the bundled script with the file path — it does the whole job atomically
(validate → back up → rewrite tags → delete backup on success / restore on
failure). Do **not** tag by hand or with other tools; always use the script so
the backup/restore guarantees hold.

```bash
mp3_tags.py "<path/to/ARTIST - TITLE.mp3>"
```

> If `mp3_tags.py` isn't found on PATH (e.g. just after a plugin update), it's
> bundled in this plugin's `bin/` directory — run it with `python3` and its full path.

## Report the result to the user by exit code
- **0 — success.** Tell the user Artist and Title were set and all other fields
  emptied (the backup was already deleted). The script prints the values used.
- **3 — pattern error.** The filename does **not** follow
  `[ARTIST] - [TITLE].mp3`. **Interrupt and tell the user** the file doesn't
  follow the required pattern. Do not retry, rename, or guess values.
- **1 — tagging failed.** The file was restored from the backup and the backup
  deleted, so the file is unchanged. Relay the printed error.
- **2 — usage error.** File not found, or `mutagen` is missing
  (`pip install --user mutagen`).

## Dependencies
Python 3 and the `mutagen` package (`pip install --user mutagen`).
