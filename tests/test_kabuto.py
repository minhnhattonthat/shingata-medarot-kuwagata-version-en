"""The Kabuto Version build (build.py --version kabuto, docs/re/kabuto.md), built fresh here from the Kabuto dump.

- script_kabuto/ is what tools/kabuto_script.py makes from the two ROMs (every src entry's bytes = its script/ entry)
- the ROM-level checks of tests/test_build.py hold (writes logged, in the mapped allowed ranges or pointer words)
- every slot of the Kabuto tables reaches the English the overlay resolves to
- the shared stages (font, widths, names charset, graphics labels, credit slots) write what the Kuwagata build writes
- the title logo cells (map rows 0-9 of BG0/BG1) come out pixel-identical to the Kuwagata build's
Skipped without the Kabuto dump in rom/.
"""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import version  # noqa: E402
import rombuild  # noqa: E402
import romcheck  # noqa: E402

KAB, KUW = version.VERSIONS["kabuto"], version.VERSIONS["kuwagata"]
need_rom = pytest.mark.skipif(not (KAB.rom.is_file() and KUW.rom.is_file()), reason="no Kabuto + Kuwagata dumps")


def build(v):
    version.select(v.name)
    try:
        orig = v.rom.read_bytes()
        data, report = rombuild.build(orig, script=v.script)
        return orig, data, report
    finally:
        version.select(version.BASE)


@pytest.fixture(scope="module")
def kab():
    return build(KAB)


@pytest.fixture(scope="module")
def kuw():
    return build(KUW)


@pytest.fixture
def as_kabuto():
    version.select("kabuto")
    yield
    version.select(version.BASE)


@need_rom
def test_overlay_up_to_date(as_kabuto):
    import kabuto_script
    docs = kabuto_script.dump(kabuto_script.load_old(KAB.script))
    have = {p.name for p in KAB.script.glob("*.json")}
    assert set(docs) == have
    import json
    for name, doc in docs.items():
        assert json.loads((KAB.script / name).read_text(encoding="utf-8")) == doc, name


@need_rom
def test_writes_logged_and_in_range(kab, as_kabuto):
    orig, data, report = kab
    assert report.moved > 7000
    assert romcheck.problems(orig, data, report.writes) == []


@need_rom
def test_every_slot_reaches_its_english(kab):
    _, data, _ = kab
    table = rombuild.en_table()
    want = {}
    for off, slots, text in rombuild.load_script(root=KAB.script):
        for s in slots:
            want[s] = table.encode(text)
    assert len(want) > 8000
    assert romcheck.slot_problems(data, want) == []


@need_rom
def test_no_untranslated_kabuto_string():
    import lint
    assert lint.untranslated(KAB.script) == []


def _by_writer(report, kinds):
    out = {}
    for off, old, new, w in report.writes:
        if w.startswith(kinds) and " ptr " not in f" {w} ":
            out.setdefault(w, []).append(new)
    return out


@need_rom
def test_shared_stages_write_the_same(kab, kuw):
    kinds = ("font", "width", "names charset", "gfx ", "credits slot", "nameentry", "minifont")
    a, b = _by_writer(kuw[2], kinds), _by_writer(kab[2], kinds)
    a = {k: v for k, v in a.items() if not k.startswith("minifont list")}  # its label holds the list's offset
    b = {k: v for k, v in b.items() if not k.startswith("minifont list")}
    assert sorted(a) == sorted(b)
    import minifont
    glyphs = (0xD0 - minifont.FIRST) * 64  # the copy runs to code FF, but glyphs end at CF (digits C6-CF): past
    a["minifont"] = [a["minifont"][0][:glyphs]]  # them is each version's own end-of-ROM data
    b["minifont"] = [b["minifont"][0][:glyphs]]
    for k in a:
        assert a[k] == b[k], k
    lists = lambda r: [new for _, _, new, w in r.writes if w.startswith("minifont list")]  # noqa: E731
    assert lists(kuw[2]) == lists(kab[2]) and len(lists(kab[2])) == 2


def _logo_cells(orig, data, report):
    """[(palette, 32-byte tile)] for map rows 0-9 of BG0 and BG1 in the built ROM."""
    import le
    import logo
    blocks = {w.split()[1]: off for off, _, _, w in report.writes if w.startswith("logo ") and "ptr" not in w}
    tiles_off, m0_off, m1_off = (blocks[f"{o:06X}"] for o in logo.block_offsets())
    tiles, _ = le.decompress(data, tiles_off)
    out = []
    for moff in (m0_off, m1_off):
        mp, _ = le.decompress(data, moff)
        for i in range(logo.ROWS * logo.MW):
            e = struct.unpack_from("<H", mp, logo.HDR + 2 * i)[0]
            t = e & 1023
            out.append((e >> 10, bytes(tiles[t * 32:t * 32 + 32])))
    return out


@need_rom
def test_logo_same_as_kuwagata(kab, kuw):
    version.select("kabuto")
    try:
        cells_b = _logo_cells(*kab)
    finally:
        version.select(version.BASE)
    assert _logo_cells(*kuw) == cells_b
