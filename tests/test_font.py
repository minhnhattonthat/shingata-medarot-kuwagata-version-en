"""The English font: glyph file, en.tbl codes, the font stage's writes, the marker text."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
import marker  # noqa: E402
import rombuild  # noqa: E402

need_rom = pytest.mark.skipif(not font.ROM.exists(), reason="original ROM not in rom/")


def test_glyphs_fit_and_match_en_tbl():
    glyphs = font.load_glyphs()
    t = rombuild.en_table()
    for code, (ch, adv, rows) in glyphs.items():
        assert 1 <= adv <= 8, f"{code:02X} advance {adv}"
        assert t.encode(ch) == bytes([code]), f"{ch!r} does not encode to {code:02X}"
        assert all(rows[y] == [1] * 8 for y in range(font.TOP)), f"{code:02X} draws above row {font.TOP}"
    # every printable character the English text may use has a glyph (or is the space)
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,'\"-:;()&/%!?+…":
        assert ch in {g[0] for g in glyphs.values()}, ch
    assert t.encode(" ") == b"\x00"


def test_jp_text_encodes_as_before():
    jp = rombuild.Table.load(ROOT / "tbl" / "jp.tbl")
    en = rombuild.en_table()
    for code, ch in jp.dec.items():
        assert en.encode(ch) == jp.encode(ch), ch


@need_rom
def test_font_stage_writes():
    orig = font.ROM.read_bytes()
    rom = rombuild.Rom(orig)
    end = font.font_stage(rom, rombuild.FREE_START)
    assert end - rombuild.FREE_START == font.GLYPHS * font.CELL
    new = struct.pack("<I", 0x08000000 + rombuild.FREE_START)
    for ref in font.FONT_REFS:
        assert rom.buf[ref:ref + 4] == new
    glyphs = font.load_glyphs()
    for code in range(font.GLYPHS):
        cell = rom.buf[rombuild.FREE_START + code * font.CELL:][:font.CELL]
        if code in glyphs:
            assert cell == font.glyph_bytes(glyphs[code][2])
            assert rom.buf[font.WIDTHS + 2 * code] == glyphs[code][1]
        else:  # untouched kana keep their bitmaps
            assert cell == orig[font.FONT + code * font.CELL:][:font.CELL]
    # nothing else below 8 MiB changes
    low = {off for off, *_ in rom.writes if off < rombuild.ORIG_SIZE}
    allowed = set(font.FONT_REFS) | {font.WIDTHS + 2 * c for c in glyphs}
    assert low <= allowed


def test_marker_keeps_controls():
    w = marker.widths()
    jp = "{face:005500}ごめんなさい{n}まだ じゅんびちゅうなの{page}メダロットの{end:00}"
    m = marker.marker_text("4FCE18", jp, "ff", False, w)
    assert marker.TOKEN.findall(m) == marker.TOKEN.findall(jp)
    assert m.startswith("{face:005500}4FCE18:")
    full = marker.marker_text("4FCE18", jp, "ff", True, w)
    for line in marker.TOKEN.split(full):
        if line and not line.startswith("{"):
            assert marker.px(line, w) <= marker.WRAP
