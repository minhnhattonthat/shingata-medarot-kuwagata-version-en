"""font.py: the dialogue font (docs/re/text.md §Font) as a PNG sheet, and back.

    python -X utf8 tools/font.py render OUT.png [--rom ROM] [--zoom 3]   # 16x16 grid of codes 00-FF, labelled
    python -X utf8 tools/font.py widths                                  # the width table, code: advance

Font: 0x548E7C, 64 bytes per code = 16 rows of one u32 (8 px, 4bpp, px 0 in the low nibble). Width table 0x4645B8:
2 bytes per code, byte 0 = advance in px (the VWF adds it to the pen x; word wrap sums it).
Glyph source for the English cells: font/en_glyphs.png (read by fontdata()).
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
FONT = 0x548E7C
ALT_FONT = 0x54FEA0
WIDTHS = 0x4645B8
ALT_WIDTHS = 0x4647B8
GLYPHS = 0xF7  # codes 00-F6 are glyphs (F7-FF are control codes)
CELL = 64


def glyph_pixels(data, code, base=FONT):
    """16 rows of 8 colour indices."""
    rows = []
    for r in range(16):
        w = struct.unpack_from("<I", data, base + code * CELL + r * 4)[0]
        rows.append([(w >> (4 * x)) & 15 for x in range(8)])
    return rows


def glyph_bytes(rows):
    out = bytearray()
    for row in rows:
        w = 0
        for x, v in enumerate(row):
            w |= (v & 15) << (4 * x)
        out += struct.pack("<I", w)
    return bytes(out)


GLYPH_FILE = ROOT / "font" / "en_glyphs.txt"
TOP = 5  # first cell row of a glyph in GLYPH_FILE
INK = {"#": 15, "+": 8, ".": 1}
# literal-pool words in the text engine that hold the font base 0x08548E7C (disasm.py xref, all in 0x08041xxx)
FONT_REFS = (0x041170, 0x0415BC, 0x041668, 0x0416FC, 0x041874, 0x041920, 0x0419B4, 0x041B54, 0x041FE0)


def load_glyphs(path=GLYPH_FILE):
    """{code: (char, advance, 16 rows of 8 colour indices)}."""
    out, cur = {}, None

    def close():
        if cur is None:
            return
        code, ch, adv, rows = cur
        if len(rows) > 16 - TOP:
            raise ValueError(f"{path}: glyph {code:02X} has {len(rows)} rows (max {16 - TOP})")
        width = max((len(r.rstrip(".")) for r in rows), default=0)
        if width > 8 or any(len(r) > 8 for r in rows):
            raise ValueError(f"{path}: glyph {code:02X} is wider than 8 px")
        cells = [[1] * 8 for _ in range(16)]
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c not in INK:
                    raise ValueError(f"{path}: glyph {code:02X}: bad pixel {c!r}")
                cells[TOP + y][x] = INK[c]
        if code in out:
            raise ValueError(f"{path}: glyph {code:02X} defined twice")
        out[code] = (ch, adv if adv is not None else width + 1, cells)

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#") and not set(line) <= set("#.+"):
            continue
        if line.startswith("@"):
            close()
            parts = line[1:].split()
            code = int(parts[0], 16)
            if code >= GLYPHS:
                raise ValueError(f"{path}: {code:02X} is a control code, not a glyph")
            cur = (code, parts[1], int(parts[2]) if len(parts) > 2 else None, [])
        else:
            cur[3].append(line.strip())
    close()
    return out


def font_stage(rom, free, glyphs=None):
    """Copy the font to `free` with the English glyphs drawn in, point the text engine at it, write the widths.
    rom: rombuild.Rom. Returns the end of the new font."""
    glyphs = load_glyphs() if glyphs is None else glyphs
    want = struct.pack("<I", 0x08000000 + FONT)
    for ref in FONT_REFS:
        if rom.orig[ref:ref + 4] != want:
            raise ValueError(f"font: literal at {ref:06X} is not the font base (wrong ROM revision?)")
    cells = bytearray(rom.orig[FONT:FONT + GLYPHS * CELL])
    for code, (_, adv, rows) in glyphs.items():
        cells[code * CELL:(code + 1) * CELL] = glyph_bytes(rows)
    rom.write(free, bytes(cells), "font")
    for ref in FONT_REFS:
        rom.write(ref, struct.pack("<I", 0x08000000 + free), f"font ptr {ref:06X}")
    for code, (_, adv, _) in sorted(glyphs.items()):
        rom.write(WIDTHS + 2 * code, bytes([adv]), f"width {code:02X}")
    return free + len(cells)


# Menu-name sprite charset (docs/re/text.md §Font, "Second renderer"): Le block, 8x8 4bpp, one tile per code 01-CF
# (tile = code - 1), loaded at OBJ tile 0x320; colour 0 = transparent, F = ink. 29 literal-pool words point at it.
NAMES = 0x5518A0
NAMES_CODES = 0xCF
NAMES_FILE = ROOT / "font" / "en_names_8x8.txt"
NAMES_INK = {1: 0}  # dialogue background -> transparent; other colours keep their index


def names_refs(data):
    want = struct.pack("<I", 0x08000000 + NAMES)
    return [p for p in range(0, len(data) - 3, 4) if data[p:p + 4] == want]


def names_tile(rows):
    """8x8 4bpp tile from dialogue-cell rows y5..y12."""
    out = bytearray()
    for row in rows[TOP:TOP + 8]:
        for x in range(0, 8, 2):
            lo, hi = (NAMES_INK.get(v, v) for v in row[x:x + 2])
            out.append(lo | hi << 4)
    return bytes(out)


def names_tiles(glyphs=None, overrides=None):
    """{code: 32-byte tile} for every English glyph the charset can hold."""
    glyphs = load_glyphs() if glyphs is None else glyphs
    overrides = load_glyphs(NAMES_FILE) if overrides is None else overrides
    out = {}
    for code, (_, _, rows) in glyphs.items():
        if not 1 <= code <= NAMES_CODES:
            raise ValueError(f"names charset: {code:02X} is outside 01-{NAMES_CODES:02X}")
        if code not in overrides and any(v != 1 for v in rows[TOP + 8]):
            raise ValueError(f"names charset: {code:02X} has ink below y12; draw it in {NAMES_FILE.name}")
        out[code] = names_tile(overrides.get(code, (None, None, rows))[2])
    for code, (_, _, rows) in overrides.items():  # charset-only glyphs, e.g. C5 円 -> ¥ in money boxes
        if code not in out:
            out[code] = names_tile(rows)
    return out


def names_stage(rom, free, glyphs=None):
    """Recompress the name charset with the English tiles at `free` (4-aligned) and repoint it. Returns the end."""
    import le
    raw, _ = le.decompress(rom.orig, NAMES)
    if len(raw) != NAMES_CODES * 32:
        raise ValueError(f"names charset: {len(raw)} bytes, expected {NAMES_CODES * 32}")
    raw = bytearray(raw)
    for code, tile in names_tiles(glyphs).items():
        raw[(code - 1) * 32:code * 32] = tile
    free = (free + 3) & ~3
    packed = le.compress(bytes(raw))
    rom.write(free, packed, "names charset")
    refs = names_refs(rom.orig)
    if len(refs) != 29:
        raise ValueError(f"names charset: {len(refs)} pointers, expected 29")
    for ref in refs:
        rom.write(ref, struct.pack("<I", 0x08000000 + free), f"names ptr {ref:06X}")
    return free + len(packed)


PALETTE = {0:(255, 255, 255), 1: (0, 0, 0), 2: (120, 120, 200), 3: (200, 120, 120)}


def render(data, out, zoom=3, base=FONT):
    from PIL import Image, ImageDraw
    cw, ch = 8 * zoom + 4, 16 * zoom + 14
    img = Image.new("RGB", (16 * cw, 16 * ch), (60, 60, 60))
    d = ImageDraw.Draw(img)
    for code in range(GLYPHS):
        gx, gy = (code % 16) * cw, (code // 16) * ch
        d.text((gx + 1, gy), f"{code:02X}", fill=(255, 255, 0))
        for y, row in enumerate(glyph_pixels(data, code, base)):
            for x, v in enumerate(row):
                c = PALETTE.get(v, (255, 0, 255))
                d.rectangle([gx + 2 + x * zoom, gy + 12 + y * zoom, gx + 1 + (x + 1) * zoom, gy + 11 + (y + 1) * zoom], fill=c)
    img.save(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("out")
    r.add_argument("--rom", default=str(ROM))
    r.add_argument("--zoom", type=int, default=3)
    r.add_argument("--alt", action="store_true", help="the alternate font at 0x54FEA0")
    w = sub.add_parser("widths")
    w.add_argument("--rom", default=str(ROM))
    a = ap.parse_args(argv)
    data = Path(a.rom).read_bytes()
    if a.cmd == "render":
        render(data, a.out, a.zoom, ALT_FONT if a.alt else FONT)
    else:
        for code in range(0x100):
            print(f"{code:02X}:{data[WIDTHS + 2 * code]}/{data[WIDTHS + 2 * code + 1]}", end="\n" if code % 16 == 15 else " ")


if __name__ == "__main__":
    sys.exit(main())
