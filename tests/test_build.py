"""Phase 7: the English build passes the ROM-level checks (references/pipeline.md §Checks), built fresh here.

romdiff with the write log (no unlogged byte, right original bytes, no overlap), every write inside
data/allowed_ranges.txt or a pointer word, and every slot of a translated string reaching its English bytes.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import rombuild  # noqa: E402
import romcheck  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
need_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@pytest.fixture(scope="module")
def built():
    orig = ROM.read_bytes()
    data, report = rombuild.build(orig)
    return orig, data, report


@need_rom
def test_writes_logged_and_in_range(built):
    orig, data, report = built
    assert report.moved > 7000
    assert romcheck.problems(orig, data, report.writes) == []


@need_rom
def test_every_translated_slot_reaches_its_english(built):
    _, data, _ = built
    table = rombuild.en_table()
    want = {}
    for path in (ROOT / "script").glob("*.json"):
        for e in json.loads(path.read_text(encoding="utf-8"))["strings"]:
            if e.get("en"):
                for slot in e["slots"]:
                    want[int(slot, 16)] = table.encode(e["en"])
    assert len(want) > 8000
    assert romcheck.slot_problems(data, want) == []
