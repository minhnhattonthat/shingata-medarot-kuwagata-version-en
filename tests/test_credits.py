"""Staff credits: every English line gets its own OAM sprite records (tools/credits.py)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import credits  # noqa: E402
import rombuild  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
need_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


def test_banks_fit_the_english():
    table = rombuild.en_table()
    text = {off: t for off, _, t in rombuild.load_script()}
    sizes = [len(table.encode(text[sid])) for _, sid, _ in credits.LINES]
    got = credits.slots(sizes)
    for (page, _, _), first, n in zip(credits.LINES, got, sizes):
        bank = credits.bank_of(page) * credits.BANK_SIZE
        assert bank <= first and first + n <= bank + credits.BANK_SIZE <= 128


def test_overflow_raises():
    with pytest.raises(ValueError):
        credits.slots([40] * len(credits.LINES))


@need_rom
def test_lines_match_the_rom():
    rom = ROM.read_bytes()
    for (page, sid, at), old in zip(credits.LINES, credits.ORIG_SLOTS):
        assert rom[at:at + 2] == bytes([old, 0x21])
    # each page's strings come from the credit tables (roles 0x510C28, sub-roles 0x510C88, names 0x510CE8)
    ptrs = {struct.unpack_from("<I", rom, base + 4 * i)[0] - 0x08000000
            for base in (0x510C28, 0x510C88, 0x510CE8) for i in range(24)}
    assert {sid for _, sid, _ in credits.LINES} <= ptrs
