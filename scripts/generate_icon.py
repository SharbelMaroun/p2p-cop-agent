"""Generate the window icon: the future-style board disc as an app identity (`M8-14`).

Deterministic and dependency-free: the PNG is written with `zlib` and `struct` alone, so
`assets/icon.png` is reproducible from this script on any machine — the same bar every
other committed asset meets. The identity is the live board's own mark: the police-blue
disc with its white ring, on the dark rounded tile the windows wear, with a blocky `P`
because a 32-pixel icon has no room for a font and no need for one.

    uv run python scripts/generate_icon.py    # rewrites assets/icon.png
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIZE = 128
TILE = (0x14, 0x1E, 0x33)
EDGE = (0x23, 0x31, 0x50)
DISC = (0x15, 0x65, 0xC0)
GLOW = (0x22, 0xD3, 0xEE)
RING = (0xFF, 0xFF, 0xFF)
LETTER = (0x0B, 0x12, 0x20)

# A 4x7 block "P", drawn at cell scale 6 so the mark stays crisp when Windows scales
# the icon down to 32 and 16 pixels.
P_ROWS = ("1110", "1001", "1001", "1110", "1000", "1000", "1000")


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], share: float) -> tuple[int, int, int]:
    return tuple(round(x + (y - x) * share) for x, y in zip(a, b, strict=True))


def _inside_tile(x: int, y: int, radius: int = 28) -> bool:
    cx = min(max(x, radius), SIZE - 1 - radius)
    cy = min(max(y, radius), SIZE - 1 - radius)
    return (x - cx) ** 2 + (y - cy) ** 2 <= radius * radius


def _letter_hit(x: int, y: int) -> bool:
    scale, width, height = 6, 4, 7
    left = (SIZE - width * scale) // 2
    top = (SIZE - height * scale) // 2
    column, row = (x - left) // scale, (y - top) // scale
    if 0 <= row < height and 0 <= column < width:
        return P_ROWS[row][column] == "1"
    return False


def _pixel(x: int, y: int) -> tuple[int, int, int, int]:
    if not _inside_tile(x, y):
        return (0, 0, 0, 0)
    centre = (SIZE - 1) / 2
    distance = ((x - centre) ** 2 + (y - centre) ** 2) ** 0.5
    disc_radius = 40
    colour = TILE
    if distance <= disc_radius + 14:  # the faked glow halo
        halo = max(0.0, 1 - (distance - disc_radius) / 14) if distance > disc_radius else 1.0
        colour = _mix(TILE, GLOW, 0.25 * halo)
    if distance <= disc_radius:
        colour = DISC
    if disc_radius - 4 <= distance <= disc_radius:
        colour = RING
    if distance < disc_radius - 4 and _letter_hit(x, y):
        colour = LETTER
    if not _inside_tile(x, y, radius=26):
        colour = _mix(colour, EDGE, 0.5)
    return (*colour, 255)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload)))


def write_icon(destination: Path) -> None:
    rows = b"".join(
        b"\x00" + b"".join(bytes(_pixel(x, y)) for x in range(SIZE))
        for y in range(SIZE)
    )
    header = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    payload = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header)
               + _chunk(b"IDAT", zlib.compress(rows, 9)) + _chunk(b"IEND", b""))
    destination.write_bytes(payload)


def main() -> int:
    destination = ROOT / "assets" / "icon.png"
    destination.parent.mkdir(exist_ok=True)
    write_icon(destination)
    print(f"{destination.name}: {destination.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
