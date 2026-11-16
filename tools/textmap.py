"""textmap.py: what every byte of the script region 0x464000-0x512000 is (phase 4 coverage).

A byte is one of:
  - a string of a text table (texttables.find_tables) or an UNUSED string (no pointer reaches it; kept in
    script/unused.json so nothing in the region is unexplained);
  - a text table's pointer run;
  - a DATA range below (binary records that decode as kana by chance: never translate them);
  - zero padding of <= 4 bytes (alignment before a pointer table).
`coverage(rom)` returns the bytes that are none of those; tests/test_script.py asserts it is empty on the original ROM.
How each range was classified: docs/re/text.md §Coverage.

    python -X utf8 tools/textmap.py ROM     # coverage summary and any unexplained gap
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import texttables  # noqa: E402

REGION = texttables.REGION

# (start, end, what). Pointer runs into the region that find_tables rejects sit inside these ranges.
DATA = [
    (0x464000, 0x4645B8, "u16 records + 8-pointer table 0x464598 into them"),
    (0x4645B8, 0x4649B8, "glyph width tables 0x4645B8 and 0x4647B8 (2 bytes per code)"),
    (0x464C38, 0x465AFC, "14-byte FE-separated records, pointer table 0x465764, more records"),
    (0x466E4C, 0x467044, "records + 6-pointer table 0x46702C into them"),
    (0x46727C, 0x46817C, "Medabot/part stat records"),
    (0x46A770, 0x46CB58, "team records + 169-pointer table 0x46C8B4"),
    (0x46E2D4, 0x46E384, "records"),
    (0x46E7F0, 0x46ED7C, "records"),
    (0x46F2BC, 0x46F350, "records"),
    (0x4705B0, 0x470AF4, "records + 132-pointer table 0x470854"),
    (0x470B18, 0x4789EC, "records + pointer tables 0x477CC8, 0x478164, 0x478958 (u16 records)"),
    (0x4789EC, 0x478E6C, "byte list of glyph codes in kana order (01 02 03 ...: a code map, not a string)"),
    (0x479060, 0x47AF50, "pointer lists into code/data + 43-pointer table 0x47A99C, FE records 0x47AEAC"),
    (0x47AF50, 0x47DF80, "event engine tables: arg counts 0x47B050, handlers 0x47B160/0x47B618, map event records"),
    (0x47DF80, 0x481CDC, "map event list table 0x47DF80 (141 maps), records, tables 0x47E658 0x48198C 0x481CD0"),
    (0x481CDC, 0x4A231C, "map grids (mostly zero)"),
    (0x4A231C, 0x4A309C, "sprite piece records (FB FF 00 00 08 00 n 00 ...) + 128-pointer table 0x4A2E9C"),
    (0x4A309C, 0x4ABD60, "packed data + 141-pointer table 0x4ABB2C"),
    (0x4ABD60, 0x4B0DE0, "ケエヤ+アアアア records + 141-pointer table 0x4B0BAC"),
    (0x4B0DE0, 0x4B2450, "u16 records + 141-pointer table 0x4B221C"),
    (0x4B57A4, 0x4B7278, "per-map records + 331-pointer table 0x4B6248, 13-byte FF-padded index records "
                         "(tables 0x4B6478 0x4B6658 0x4B7168)"),
    (0x4F83B8, 0x4F83FC, "16-pointer table 0x4F83BC (into pointer runs)"),
    (0x4F873C, 0x4FCE18, "event scripts + event table 0x4FC358 (688 events, docs/re/debug.md §Events)"),
    (0x50C378, 0x50C878, "pointer list into data"),
    (0x50D684, 0x50DC38, "pointer list, records + 8-pointer table 0x50DA8C"),
    (0x50E940, 0x50EE2C, "pointer list into data"),
    (0x5102A4, 0x510AEC, "pointer lists into code + 8-pointer table 0x510A04, records"),
    (0x510D48, 0x512000, "pointer lists, 3-byte command records (table 0x510F0C), Le blocks from 0x510FA4"),
]

# Strings no pointer reaches, found after a table string's terminator (start, note). Extracted to script/unused.json.
UNUSED = [
    (0x4C7566, "エラー！！ x6, after table 0x4F4B14's strings"),
    (0x4C756D, ""), (0x4C7574, ""), (0x4C757B, ""), (0x4C7582, ""), (0x4C7589, ""),
    (0x505E26, "dialogue line between two used lines"),
    (0x50740E, "dialogue line between two used lines"),
    (0x5097A0, "head of a line: the table points at 0x5097AF, its second half"),
]


def unused_at(rom, off):
    """The unused string's bytes: through its terminator (0x5097A0 runs into the used string at 0x5097AF)."""
    return texttables.string_at(rom, off)


def coverage(rom, tables=None):
    """Unexplained (start, end) gaps in REGION; [] when every byte is a string, a text table, DATA or padding."""
    tables = tables if tables is not None else texttables.find_tables(rom)
    cov = bytearray(REGION[1] - REGION[0])

    def mark(a, b):
        a, b = max(a, REGION[0]), min(b, REGION[1])
        if a < b:
            cov[a - REGION[0]:b - REGION[0]] = b"\1" * (b - a)

    runs = dict(texttables.pointer_runs(rom))
    for tt in tables:
        if tt.addr:
            mark(tt.addr, runs[tt.addr])
        for s in tt.targets:
            mark(s, s + len(texttables.string_at(rom, s)))
    for off, _ in UNUSED:
        mark(off, off + len(unused_at(rom, off)))
    for a, b, _ in DATA:
        mark(a, b)
    gaps, p = [], 0
    while p < len(cov):
        if cov[p]:
            p += 1
            continue
        q = p
        while q < len(cov) and not cov[q]:
            q += 1
        a, b = p + REGION[0], q + REGION[0]
        if not (b - a <= 4 and not any(rom[a:b])):
            gaps.append((a, b))
        p = q
    return gaps


def overlaps(rom, tables=None):
    """DATA ranges that overlap a string: a DATA range must never hold text."""
    tables = tables if tables is not None else texttables.find_tables(rom)
    spans = [(s, s + len(texttables.string_at(rom, s))) for tt in tables for s in tt.targets]
    spans += [(o, o + len(unused_at(rom, o))) for o, _ in UNUSED]
    return [(a, b, s, e) for a, b, _ in DATA for s, e in spans if s < b and a < e]


if __name__ == "__main__":
    rom = Path(sys.argv[1]).read_bytes()
    tables = texttables.find_tables(rom)
    gaps = coverage(rom, tables)
    print(f"DATA {len(DATA)} ranges, {sum(b - a for a, b, _ in DATA):#x} bytes; unexplained gaps: {len(gaps)}")
    for a, b in gaps:
        print(f"  {a:07X}-{b:07X} {rom[a:min(b, a + 16)].hex()}")
    for a, b, s, e in overlaps(rom, tables):
        print(f"  DATA {a:07X}-{b:07X} overlaps string {s:07X}-{e:07X}")
