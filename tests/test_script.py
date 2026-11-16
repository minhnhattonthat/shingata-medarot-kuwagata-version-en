"""Phase 4: script/*.json is the whole script of the original ROM, byte-exact, and the script region is fully explained.

- roundtrip: encoding every string's `jp` through tbl/jp.tbl gives the original bytes at its id;
- the files match a fresh tools/extract.py dump (slots, kind, jp): nothing stale, nothing missing;
- coverage: every byte of 0x464000-0x512000 is a string, a text table, a DATA range or padding (tools/textmap.py),
  and no DATA range overlaps a string.
"""
import json
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import extract  # noqa: E402
import rombuild  # noqa: E402
import texttables  # noqa: E402
import textmap  # noqa: E402
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
need_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")
FIELDS = {"id", "slots", "kind", "bytes", "jp", "en", "status", "notes"}


def docs():
    return {p.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "script").glob("*.json"))}


def entries():
    return [e for d in docs().values() for e in d["strings"]]


@pytest.fixture(scope="module")
def orig():
    return ROM.read_bytes()


def test_entries_well_formed():
    es = entries()
    assert len(es) > 8000
    ids = [e["id"] for e in es]
    assert len(ids) == len(set(ids)), "an id is in two files"
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    for e in es:
        assert FIELDS <= e.keys(), e["id"]
        assert e["kind"] in ("ff", "fe")
        assert e["jp"].endswith("{item}" if e["kind"] == "fe" else ""), e["id"]
        assert len(t.encode(e["jp"])) == e["bytes"], e["id"]


@need_rom
def test_every_string_roundtrips(orig):
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    for e in entries():
        off = int(e["id"], 16)
        assert t.encode(e["jp"]) == orig[off:off + e["bytes"]], e["id"]
        assert texttables.string_at(orig, off) == orig[off:off + e["bytes"]], e["id"]
        for s in e["slots"]:
            assert struct.unpack_from("<I", orig, int(s, 16))[0] - texttables.GBA == off, (e["id"], s)


@need_rom
def test_script_matches_fresh_dump(orig):
    fresh = extract.dump(orig)
    have = docs()
    assert fresh.keys() == have.keys()
    for name, doc in fresh.items():
        old = {e["id"]: e for e in have[name]["strings"]}
        assert [e["id"] for e in doc["strings"]] == list(old), name
        for e in doc["strings"]:
            o = old[e["id"]]
            assert (o["slots"], o["kind"], o["bytes"], o["jp"]) == (e["slots"], e["kind"], e["bytes"], e["jp"]), e["id"]


@need_rom
def test_script_has_every_table_slot(orig):
    tables = texttables.find_tables(orig)
    script_slots = {int(s, 16) for e in entries() for s in e["slots"]}
    assert script_slots == {s for tt in tables for s in tt.slots}


@need_rom
def test_region_fully_covered(orig):
    tables = texttables.find_tables(orig)
    assert textmap.coverage(orig, tables) == []
    assert textmap.overlaps(orig, tables) == []


def test_load_script_takes_en_over_jp(tmp_path):
    doc = {"table": "000000", "about": "", "strings": [
        {"id": "50A0C9", "slots": ["50C2A0"], "kind": "ff", "bytes": 3, "jp": "あ{end:00}", "en": "A{end:00}",
         "status": "new", "notes": ""},
        {"id": "50A0D0", "slots": ["50C2A4"], "kind": "ff", "bytes": 3, "jp": "い{end:00}", "en": "",
         "status": "new", "notes": ""},
        {"id": "4C7566", "slots": [], "kind": "ff", "bytes": 3, "jp": "う{end:00}", "en": "", "status": "new",
         "notes": ""}]}
    (tmp_path / "x.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    got = rombuild.load_script("en", tmp_path)
    assert got == [(0x50A0C9, [0x50C2A0], "A{end:00}"), (0x50A0D0, [0x50C2A4], "い{end:00}")]
