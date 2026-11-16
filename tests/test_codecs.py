import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import le  # noqa: E402
import lz77  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
need_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")

# Sampled real blocks (docs/re/rom.md).
LE_BLOCKS = [0x510FA4, 0x5118CC, 0x51102C]
LZ_BLOCKS = [0x0ACBD8, 0x60ECC0, 0x60ED58]


@need_rom
@pytest.mark.parametrize("off", LE_BLOCKS)
def test_le_roundtrip(off):
    data = ROM.read_bytes()
    raw, _ = le.decompress(data, off)
    assert le.decompress(le.compress(raw))[0] == raw


@need_rom
@pytest.mark.parametrize("off", LZ_BLOCKS)
def test_lz77_roundtrip(off):
    data = ROM.read_bytes()
    raw, _ = lz77.decompress(data, off)
    assert lz77.decompress(lz77.compress(raw))[0] == raw


def test_le_synthetic():
    raw = bytes(range(40)) * 3 + b"\x00" * 70 + b"abcabcabc"
    assert le.decompress(le.compress(raw))[0] == raw
