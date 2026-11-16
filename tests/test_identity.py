"""Phase 3 identity build: unpack -> repack with no edits gives the original ROM byte for byte (keep green forever).

Also proves the pointer writer: with every string moved past 8 MiB, each slot reaches the same bytes it did before.
"""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import rombuild  # noqa: E402
import texttables  # noqa: E402
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
need_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@pytest.fixture(scope="module")
def orig():
    return ROM.read_bytes()


@pytest.fixture(scope="module")
def tables(orig):
    return texttables.find_tables(orig)


@need_rom
def test_identity_build(orig):
    data, report = rombuild.build(orig)
    assert report.strings > 7000 and report.moved == 0
    assert data == orig


@need_rom
def test_every_string_roundtrips(orig, tables):
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    for off in {x for tt in tables for x in tt.targets}:
        s = texttables.string_at(orig, off)
        assert t.encode(t.decode(s, 0, len(s))[0]) == s, f"{off:07X}"


@need_rom
def test_tables_known(tables):
    addrs = {tt.addr for tt in tables}
    # verified tables from docs/re/text.md: bank A (event text), medal, part and Medabot names, credits
    assert {0x50A9D8, 0x465B8C, 0x468A00, 0x468308, 0x510C28} <= addrs
    assert not addrs & texttables.EXCLUDE
    # code literals: the parts shop clerk's greeting (missed until the poison build showed it as ア)
    assert 0x660AC in tables[-1].slots and tables[-1].addr == 0


@need_rom
def test_relocate_all_reaches_same_bytes(orig, tables):
    data, report = rombuild.build(orig, relocate_all=True)
    assert report.in_place == 0 and len(data) <= rombuild.MAX_SIZE
    for tt in tables:
        for slot in tt.slots:
            old = struct.unpack_from("<I", orig, slot)[0] - rombuild.GBA
            new = struct.unpack_from("<I", data, slot)[0] - rombuild.GBA
            assert new >= rombuild.FREE_START
            want = texttables.string_at(orig, old)
            assert data[new:new + len(want)] == want, f"slot {slot:07X}"
    # below 8 MiB only the pointer slots change; the rest of the write log is the new space
    changed = {off for off, *_ in report.writes if off < rombuild.ORIG_SIZE}
    assert changed <= {s for tt in tables for s in tt.slots}
    assert data[:rombuild.ORIG_SIZE] != orig


@need_rom
def test_edited_string_moves_and_repoints(orig, tables):
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    off = tables[0].targets[0]
    new = t.encode("ABC{end:00}")
    data, report = rombuild.build(orig, strings={off: new})
    assert report.moved == 1
    for tt in tables:
        for slot in tt.slots:
            if struct.unpack_from("<I", orig, slot)[0] - rombuild.GBA == off:
                p = struct.unpack_from("<I", data, slot)[0] - rombuild.GBA
                assert data[p:p + len(new)] == new


def test_poisoned_keeps_controls():
    s = bytes([0xFB, 0x01, 0x00, 0x00, 0x52, 0x00, 0x53, 0xF9, 0x00, 0xFD, 0x54, 0xFF, 0x00])
    assert rombuild.poisoned(s) == bytes([0xFB, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0xF9, 0x00, 0xFD, 0x01, 0xFF, 0x00])
