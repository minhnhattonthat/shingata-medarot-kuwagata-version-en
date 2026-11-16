import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import font  # noqa: E402
import romcheck  # noqa: E402


def write_at(off):
    """A pointer-looking word rewritten at off in a small fake ROM: (orig, data, writes)."""
    orig = bytearray(0x50000)
    struct.pack_into("<I", orig, off, 0x08123456)
    data = bytearray(orig)
    struct.pack_into("<I", data, off, 0x08800000)
    return bytes(orig), bytes(data), [(off, orig[off:off + 4], data[off:off + 4], "test")]


def test_pointer_word_at_a_known_slot_passes():
    assert romcheck.problems(*write_at(font.FONT_REFS[0])) == []


def test_pointer_looking_word_elsewhere_fails():
    assert romcheck.problems(*write_at(0x40000))
