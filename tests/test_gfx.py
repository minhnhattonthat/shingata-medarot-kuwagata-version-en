"""Graphics labels (tools/gfx.py, gfx/labels.json): every label fits its box, changes no pixel outside it,
roundtrips through its codec, and its pointer count matches the ROM."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx  # noqa: E402


@pytest.mark.skipif(not gfx.ROM.exists(), reason="needs the original ROM")
def test_labels_check():
    assert gfx.check() == []


def test_font_has_capitals_and_digits():
    font = gfx.load_font("en_label_9")
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !?.-:'/":
        assert ch in font, ch
        assert all(len(r) == len(font[ch][1][0]) for r in font[ch][1]), ch


def test_text_box_overflow_is_an_error():
    spec = gfx.load_spec()
    label = dict(spec["labels"][0], text=[{"s": "MEDAWATCHMEDAWATCH", "x": 19, "style": "menu_pink"}])
    with pytest.raises(ValueError, match="runs out of its box"):
        gfx.compose(gfx.ROM.read_bytes(), label, spec["styles"])
