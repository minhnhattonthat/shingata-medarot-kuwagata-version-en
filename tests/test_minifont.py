"""Minigame counter font (tools/minifont.py): the stage finds its literals and lists in the original, the copy keeps
every glyph it does not redraw, and each list keeps its length and FE end."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx  # noqa: E402
import minifont  # noqa: E402
import rombuild  # noqa: E402


def test_cells_use_known_letters():
    for pair in minifont.CELLS.values():
        assert len(pair) == 2 and all(ch in minifont.MINI for ch in pair), pair
    for codes in minifont.TEXT.values():
        assert all(c in minifont.CELLS for c in codes)


@pytest.mark.skipif(not gfx.ROM.exists(), reason="needs the original ROM")
def test_stage_writes():
    orig = gfx.ROM.read_bytes()
    rom = rombuild.Rom(orig)
    free = 0x800000
    end = minifont.stage(rom, free)
    data = rom.buf
    base = struct.unpack_from("<I", data, minifont.REFS[0])[0] - 0x08000000
    assert all(struct.unpack_from("<I", data, r)[0] - 0x08000000 == base for r in minifont.REFS)
    assert end - free == (minifont.LAST - minifont.FIRST + 1) * 64
    for code in range(minifont.FIRST, minifont.LAST + 1):
        new = data[base + code * 64:base + code * 64 + 64]
        if code in minifont.CELLS:
            assert new == minifont.glyph(minifont.CELLS[code])
        else:
            assert new == orig[minifont.BASE + code * 64:minifont.BASE + code * 64 + 64]
    for off, n in minifont.LISTS.items():
        assert data[off:off + n] == bytes(minifont.TEXT[off]) and data[off + n] == 0xFE
