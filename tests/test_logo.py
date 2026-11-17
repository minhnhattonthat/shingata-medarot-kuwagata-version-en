"""Title logo (tools/logo.py, gfx/logo/*.png): the new blocks draw exactly the committed PNGs in map rows 0-9 and
change nothing else the title shows (BG0/BG1 rows 10-19, and every tile BG2/BG3 use)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import le  # noqa: E402
import logo  # noqa: E402

pytestmark = pytest.mark.skipif(not logo.ROM.exists(), reason="needs the original ROM")


def test_logo_blocks_draw_the_pngs_and_nothing_else():
    rom = logo.ROM.read_bytes()
    t0, a, b = logo.originals(rom)
    t1, n0, n1, _ = logo.make(rom)
    assert len(t1) == len(t0)  # same tile count: nothing after the block moves
    want = logo.load_layers()
    assert logo.render(t1, n0) == [list(r) for r in want[0]]
    assert logo.render(t1, n1) == [list(r) for r in want[1]]
    for old, new in ((a, n0), (b, n1)):
        for cy in range(logo.ROWS, logo.MH):
            for cx in range(logo.MW):
                e = logo.entry(old, cx, cy) & 1023
                assert logo.entry(new, cx, cy) == logo.entry(old, cx, cy)
                assert t1[e * 32:e * 32 + 32] == t0[e * 32:e * 32 + 32], (cx, cy)
    for off in logo.OTHER_MAPS:
        mp, _ = le.decompress(rom, off)
        for i in range(logo.MW * logo.MH):
            e = logo.entry(mp, i % logo.MW, i // logo.MW) & 1023
            assert t1[e * 32:e * 32 + 32] == t0[e * 32:e * 32 + 32]


def test_logo_blocks_roundtrip_le():
    rom = logo.ROM.read_bytes()
    for raw in logo.make(rom)[:3]:
        assert le.decompress(le.compress(raw), 0)[0] == raw
