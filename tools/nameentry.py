"""nameentry.py: the name-entry letter grid in English (phase 8, docs/graphics-todo.md).

The grid's input codes are a ROM table at 0x0C1414 (read by 0x080639A4 through r1 when A types a cell): 3 pages
(katakana, hiragana, alphanumeric) x 5 rows x 24 bytes. Each row is 23 cells + FE; FF = gap the cursor skips,
FB/FC/FD = the page tabs (cols 18-22 of rows 3-5), 00 = a blank cell. The cell at column k is drawn at
x = 28 + 8k, row r at y = 57 + 16r (BG1 map lz_73163C for page 1, BG0 map lz_7313EC rows 7-15 for page 2 and rows
21-29 for page 3); the labels that draw them are "name_entry.grid*" in gfx/labels.json (their "cells" rows must
equal PAGES, tests/test_gfx.py checks it).

English pages: ABC (capitals), abc (lowercase), 123 (digits and symbols). Codes from tbl/en.tbl, so the typed name
shows in the names charset (font.names_stage) and in dialogue alike. A space in PAGES is a gap (FF).

The hero's default name ガンマ (FE string at 0x50C620, pointed to only by the word at 0x50C624, read through the
literal at 0x62FC4 by 0x08062FA0) becomes "Gamma" (glossary.md), written past 8 MiB.
"""
import struct

TABLE = 0x0C1414
DEFAULT_JP, DEFAULT_PTR, DEFAULT_EN = 0x50C620, 0x50C624, "Gamma"
ROWS, COLS = 5, 23
TABS = (0xFB, 0xFC, 0xFD)  # rows 3-5, cols 18-22, on every page

_PUNCT = "!?&/: ()\";+"  # no ~: font/en_glyphs.txt has no glyph for it
PAGES = {
    "ABC": ["ABCDE FGHIJ KLMNO PQRST",
            "UVWXY Z.,'- 01234 56789",
            _PUNCT],
    "abc": ["abcde fghij klmno pqrst",
            "uvwxy z.,'- 01234 56789",
            _PUNCT],
    "123": ["0123456789 .,'\"-:;()&/%",
            "!?+…"],
}


def page_rows(name):
    """The 5 rows of a page as 23-character strings (tab cells blank)."""
    rows = [r.ljust(COLS) for r in PAGES[name]]
    rows += [" " * COLS] * (ROWS - len(rows))
    for r in rows:
        if len(r) != COLS:
            raise ValueError(f"nameentry: page {name} row {r!r} is not {COLS} cells")
    for r in rows[2:]:
        if r[18:].strip():
            raise ValueError(f"nameentry: page {name} row {r!r} has a glyph in the tab column")
    return rows


def table_bytes():
    import rombuild
    tbl = rombuild.en_table()
    out = bytearray()
    for name in PAGES:
        for r, row in enumerate(page_rows(name)):
            for k, ch in enumerate(row):
                if r >= 2 and k >= 18:
                    out.append(TABS[r - 2])
                elif ch == " ":
                    out.append(0xFF)
                else:
                    code = tbl.encode(ch)
                    if len(code) != 1 or not 0x01 <= code[0] <= 0xCF:
                        raise ValueError(f"nameentry: {ch!r} has no names-charset code ({code.hex()})")
                    out += code
            out.append(0xFE)
    return bytes(out)


def stage(rom, free):
    """Rewrite the grid table in place; write the default name at `free` and repoint it. Returns the new end."""
    import rombuild
    new = table_bytes()
    old = rom.orig[TABLE:TABLE + len(new)]
    if len(new) != 3 * ROWS * (COLS + 1) or old[COLS::COLS + 1] != b"\xfe" * (3 * ROWS):
        raise ValueError("nameentry: the original grid table is not where expected")
    rom.write(TABLE, new, "nameentry grid")
    if rom.orig[DEFAULT_PTR:DEFAULT_PTR + 4] != struct.pack("<I", 0x08000000 + DEFAULT_JP) or \
            rom.orig[DEFAULT_JP:DEFAULT_JP + 4] != b"\x38\x2e\x1f\xfe":
        raise ValueError("nameentry: the default name ガンマ is not where expected")
    name = rombuild.en_table().encode(DEFAULT_EN) + b"\xfe"
    rom.write(free, name, "nameentry default name")
    rom.write(DEFAULT_PTR, struct.pack("<I", 0x08000000 + free), "nameentry default name ptr")
    return free + len(name)
