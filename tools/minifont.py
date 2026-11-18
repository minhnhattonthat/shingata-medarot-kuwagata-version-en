"""minifont.py: the minigame counters (baseball, car_game) in English (phase 8, docs/graphics-todo.md).

The counters (のこり10きゅう, 0てん, のこり60びょう) are not text the engine prints: each minigame copies a glyph list
from the text region (baseball 0x50EB4C, car 0x50EC08; codes in tbl/jp.tbl hiragana order, FE ends it) into fixed
VRAM tile pairs, one 8x16 glyph per code from a raw 4bpp font at base 0x087C49CC + code*64 (literal at 0x77BE8 and
0x788E0; glyphs 16-level grey, ink rows 4-11). The code then lays those tile pairs out in hard-coded cells:

    slots 1-3 | count | slots 9-11      (baseball: のこり 10 きゅう; car: slots 4-6 after the count: のこり 60 びょう)
    score | slots 7-8                   (0 てん)

So the cells stay; their glyphs change. The stage copies the font past 8 MiB with narrow two-letter glyphs (3x7
capitals, two per 8-px cell) drawn over codes 52-59, repoints the two base literals and rewrites the glyph lists in
place (text region, allowed). The digit glyphs keep their own pointers into the original font.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from version import at  # noqa: E402  (Kuwagata offset -> the build's version; constants here are Kuwagata)

BASE = 0x7C49CC         # font base: glyph address = BASE + code * 64
FIRST, LAST = 0x52, 0xFF  # codes copied (the lists use 52..; digits sit at C6..)
REFS = (0x77BE8, 0x788E0)
LISTS = {0x50EB4C: 11, 0x50EC08: 11}  # glyph list -> slot count (the car list's tail "FE C8 C6 FE" is kept)

# 3x7 capitals for the two-letter cells
MINI = {
    " ": ["...", "...", "...", "...", "...", "...", "..."],
    "A": [".#.", "#.#", "#.#", "###", "#.#", "#.#", "#.#"],
    "B": ["##.", "#.#", "#.#", "##.", "#.#", "#.#", "##."],
    "E": ["###", "#..", "#..", "##.", "#..", "#..", "###"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "L": ["#..", "#..", "#..", "#..", "#..", "#..", "###"],
    "M": ["#.#", "###", "###", "#.#", "#.#", "#.#", "#.#"],
    "P": ["##.", "#.#", "#.#", "##.", "#..", "#..", "#.."],
    "S": [".##", "#..", "#..", ".#.", "..#", "..#", "##."],
    "T": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", ".#."],
}
INK, TOP = 0xE, 5  # ink level, first ink row (bottom row 11 = the digits' baseline)

CELLS = {0x52: "  ", 0x53: "BA", 0x54: "LL", 0x55: "S ", 0x56: " P", 0x57: "TI", 0x58: "ME", 0x59: "TS"}
BLANK = 0x52
# English per list, slot by slot (1-3 before the count, 4-6 after it in the car game, 7-8 after the score,
# 9-11 after it in baseball): BALLS 10 / 0 PTS, TIME 60 / 0 PTS
TEXT = {
    0x50EB4C: [0x53, 0x54, 0x55, BLANK, BLANK, BLANK, 0x56, 0x59, BLANK, BLANK, BLANK],
    0x50EC08: [0x57, 0x58, BLANK, BLANK, BLANK, BLANK, 0x56, 0x59, BLANK, BLANK, BLANK],
}


def glyph(pair):
    """64 bytes (top tile, bottom tile) for a two-letter cell."""
    px = [[0] * 8 for _ in range(16)]
    for i, ch in enumerate(pair):
        for y, row in enumerate(MINI[ch]):
            for x, c in enumerate(row):
                if c == "#":
                    px[TOP + y][i * 4 + x] = INK
    out = bytearray()
    for y in range(16):
        for x in range(0, 8, 2):
            out.append(px[y][x] | px[y][x + 1] << 4)
    return bytes(out)


def font_bytes(orig):
    base = at(BASE)
    data = bytearray(orig[base + FIRST * 64:base + (LAST + 1) * 64])
    for code, pair in CELLS.items():
        data[(code - FIRST) * 64:(code - FIRST + 1) * 64] = glyph(pair)
    return bytes(data)


def stage(rom, free):
    """Write the font copy at `free` (4-aligned), repoint, rewrite the lists. Returns the new end."""
    want = struct.pack("<I", 0x08000000 + at(BASE))
    refs = [at(r) for r in REFS]
    for ref in refs:
        if rom.orig[ref:ref + 4] != want:
            raise ValueError(f"minifont: literal at {ref:06X} is not the font base")
    for off, n in LISTS.items():
        off = at(off)
        if rom.orig[off + n] != 0xFE:
            raise ValueError(f"minifont: glyph list at {off:06X} does not end after {n} codes")
    free = (free + 3) & ~3
    data = font_bytes(rom.orig)
    rom.write(free, data, "minifont")
    new_base = 0x08000000 + free - FIRST * 64
    for ref in refs:
        rom.write(ref, struct.pack("<I", new_base), f"minifont ptr {ref:06X}")
    for off, codes in TEXT.items():
        rom.write(at(off), bytes(codes), f"minifont list {at(off):06X}")
    return free + len(data)
