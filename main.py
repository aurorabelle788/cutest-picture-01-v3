#!/usr/bin/env python3
"""cutest-picture-01, entry v3.

Ships one picture: entry.png next to this file, a tiny kitten in a
fluffy panda hood, huge sparkling blue eyes, pink scarf, a toy panda
with bamboo, a lit lantern under a full moon. The file itself is a
JPEG (the competition allows JPEG bytes under the name entry.png).

Running this file copies that picture to the output directory
($MAKEFUN_OUTPUT_DIR, or /output when the variable is absent) and
then refuses to finish quietly unless the copy is a faithful,
gate-passing picture: whole file, right format, within size limits.
Same input bytes always give the same output bytes.
"""

import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PICTURE = HERE / "entry.png"

LIMIT_BYTES = 1_048_576  # 1 MiB, the competition cap
LIMIT_SIDE = 1_024  # longest side in pixels
PNG_HEAD = b"\x89PNG\r\n\x1a\n"
JPEG_HEAD = b"\xff\xd8"
JPEG_TAIL = b"\xff\xd9"


def jpeg_size(blob):
    """Width and height out of a JPEG blob, from its first SOF marker."""
    pos = 2
    while pos + 9 < len(blob):
        if blob[pos] != 0xFF:
            pos += 1
            continue
        tag = blob[pos + 1]
        if tag in (0xC0, 0xC1, 0xC2):
            tall, wide = struct.unpack(">HH", blob[pos + 5:pos + 9])
            return wide, tall
        span = struct.unpack(">H", blob[pos + 2:pos + 4])[0]
        pos += 2 + span
    raise SystemExit("cannot find a JPEG size marker (SOF0/SOF2)")


def describe(blob):
    """Return (format, width, height) for a PNG or JPEG blob."""
    if blob[:8] == PNG_HEAD:
        if not blob.rstrip(b"\x00").endswith(b"IEND\xaeB`\x82"):
            raise SystemExit("PNG stops before its IEND chunk")
        wide, tall = struct.unpack(">II", blob[16:24])
        return "PNG", wide, tall
    if blob[:2] == JPEG_HEAD:
        if blob[-2:] != JPEG_TAIL:
            raise SystemExit("JPEG stops before its end marker")
        wide, tall = jpeg_size(blob)
        return "JPEG", wide, tall
    raise SystemExit("not a PNG or a JPEG file")


def verify_copy(dest):
    """Check the written copy against the gate, then report it."""
    blob = dest.read_bytes()
    if len(blob) > LIMIT_BYTES:
        raise SystemExit(
            f"copy is {len(blob)} bytes, past the {LIMIT_BYTES} byte cap"
        )
    kind, wide, tall = describe(blob)
    if wide > LIMIT_SIDE or tall > LIMIT_SIDE:
        raise SystemExit(
            f"copy is {wide}x{tall}, past the {LIMIT_SIDE}x{LIMIT_SIDE} cap"
        )
    if blob != PICTURE.read_bytes():
        raise SystemExit("copy is not byte-for-byte the shipped picture")
    print(f"wrote {dest} ({kind} {wide}x{tall}, {len(blob)} bytes)",
          file=sys.stderr)


def run():
    target = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target.mkdir(parents=True, exist_ok=True)
    dest = target / "entry.png"
    shutil.copyfile(PICTURE, dest)
    verify_copy(dest)


if __name__ == "__main__":
    run()
