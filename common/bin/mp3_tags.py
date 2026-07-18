#!/usr/bin/env python3
"""mp3-tags: set ONLY Artist + Title on an MP3 from its filename.

The filename must follow "[ARTIST] - [TITLE].mp3" (ARTIST = everything before
the first " - ", TITLE = everything after). The script sets only Artist (TPE1)
and Title (TIT2) and empties every other tag field (all other ID3v2 frames,
ID3v1, and any APEv2 tag).

It backs the file up first, then:
  - on success, deletes the backup;
  - on failure, restores the file from the backup and deletes it.

Exit codes:
  0  success        (tags written, backup deleted)
  1  tagging failed (file restored from backup, backup deleted)
  2  usage error    (bad args / not a file / 'mutagen' not installed)
  3  pattern error  (filename does not match "[ARTIST] - [TITLE].mp3")
"""
import os
import shutil
import sys
import tempfile

SEP = " - "  # split on the FIRST occurrence, so a TITLE may itself contain " - "


def parse_name(path):
    """Return (artist, title), or None if the name doesn't match the pattern."""
    root, ext = os.path.splitext(os.path.basename(path))
    if ext.lower() != ".mp3":
        return None
    artist, sep, title = root.partition(SEP)
    artist, title = artist.strip(), title.strip()
    if not sep or not artist or not title:
        return None
    return artist, title


def write_tags(path, artist, title):
    """Replace all tags on `path` with exactly Artist (TPE1) and Title (TIT2)."""
    from mutagen.apev2 import APEv2, APENoHeaderError
    from mutagen.id3 import ID3, TIT2, TPE1

    # Drop an APEv2 tag if present (the ID3 path below won't touch it).
    try:
        APEv2(path).delete()
    except APENoHeaderError:
        pass

    # A fresh ID3 object saved to the file replaces the on-disk ID3v2 tag
    # wholesale, so only the two frames we add survive. v1=0 strips ID3v1.
    tags = ID3()
    tags.add(TPE1(encoding=3, text=[artist]))  # 3 = UTF-8
    tags.add(TIT2(encoding=3, text=[title]))
    tags.save(path, v1=0, v2_version=4)


def main(argv):
    if len(argv) != 2:
        print("usage: mp3_tags.py <file.mp3>", file=sys.stderr)
        return 2
    path = argv[1]
    if not os.path.isfile(path):
        print(f"ERROR: not a file: {path}", file=sys.stderr)
        return 2

    parsed = parse_name(path)
    if parsed is None:
        print(
            'PATTERN: filename does not follow "[ARTIST] - [TITLE].mp3": '
            f"{os.path.basename(path)}",
            file=sys.stderr,
        )
        return 3
    artist, title = parsed

    try:
        import mutagen  # noqa: F401  (import checked before we touch the file)
    except ImportError:
        print(
            "ERROR: the 'mutagen' package is required "
            "(pip install --user mutagen).",
            file=sys.stderr,
        )
        return 2

    # Back up in the same directory so the restore (os.replace) is atomic.
    directory = os.path.dirname(os.path.abspath(path))
    fd, backup = tempfile.mkstemp(prefix=".mp3tags-", suffix=".bak", dir=directory)
    os.close(fd)
    shutil.copy2(path, backup)  # copies content + mode + mtime

    try:
        write_tags(path, artist, title)
    except Exception as e:
        os.replace(backup, path)  # restore content and remove the backup
        print(
            f"FAILED: {type(e).__name__}: {e}\n"
            "  File restored from backup; backup deleted.",
            file=sys.stderr,
        )
        return 1

    os.remove(backup)  # success -> drop the backup
    print(
        f'OK: "{os.path.basename(path)}"\n'
        f"  Artist = {artist}\n"
        f"  Title  = {title}\n"
        "  all other tag fields emptied; backup deleted."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
