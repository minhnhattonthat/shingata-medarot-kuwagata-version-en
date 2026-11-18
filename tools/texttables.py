"""texttables.py: the string pointer tables of the script region, found from the ORIGINAL ROM.

A table is a run of >= 3 aligned u32 pointers (0x08000000 | offset) inside the script region whose targets are all
strings: bytes through `FF xx` (dialogue) or through `FE` (name-list entry), whichever comes first, decoding with no
unknown byte through tbl/jp.tbl. Targets that land inside a pointer run are unused slots and are skipped.
EXCLUDE lists runs that pass that rule but hold data records (docs/re/text.md §Tables used by the build).
Code literals that point at one of those strings are added as a last pseudo-table (addr 0).

tools/extract.py dumps these into script/*.json, which the build reads; tests/test_script.py keeps the two in step.

    python -X utf8 tools/texttables.py ROM      # one line per table: address, slots, strings
"""
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbl import Table  # noqa: E402
import version  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GBA = 0x08000000
REGION = (0x464000, 0x512000)
MIN_RUN = 3
CODE_END = 0x0C5000  # code and tables (docs/re/rom.md)
# Runs that pass the rule but point at binary records that decode as kana by chance (docs/re/text.md):
# FE-separated 14-byte records (0x465764, 0x47AEAC), u16 records (0x478958), 3-byte FF-separated commands
# (0x510F0C), ケエヤ+アアアア... records (0x4B0BAC), 13-byte FF-padded index records (0x4B7168). tools/textmap.py
# lists every non-text range of the region.
EXCLUDE = {0x465764, 0x478958, 0x47AEAC, 0x510F0C, 0x4B0BAC, 0x4B7168}
ARGS = {0xF7: 1, 0xF9: 1, 0xFA: 1, 0xFB: 3}  # control codes with argument bytes (FF's one arg ends the string)
MAXLEN = 2048


@dataclass
class TextTable:
    addr: int                                    # ROM offset of the first pointer slot
    slots: list = field(default_factory=list)    # ROM offsets of the pointer slots that point at strings
    targets: list = field(default_factory=list)  # sorted unique string offsets


def string_at(rom, off):
    """The string's bytes: through `FF xx` or `FE`, whichever comes first. None if neither within MAXLEN."""
    p = off
    while p - off < MAXLEN and p < len(rom):
        b = rom[p]
        if b == 0xFF:
            return bytes(rom[off:p + 2])
        if b == 0xFE:
            return bytes(rom[off:p + 1])
        p += 1 + ARGS.get(b, 0)
    return None


def region():
    """REGION in the current version (tools/version.py; the constants above are Kuwagata offsets)."""
    return version.at(REGION[0]), version.at(REGION[1])


def _ptr(rom, p):
    v = struct.unpack_from("<I", rom, p)[0] - GBA
    lo, hi = region()
    return v if lo <= v < hi else None


def pointer_runs(rom):
    runs = []
    lo, hi = region()
    for p in range(lo, hi, 4):
        if _ptr(rom, p) is None:
            continue
        if runs and runs[-1][1] == p:
            runs[-1][1] = p + 4
        else:
            runs.append([p, p + 4])
    return runs


def find_tables(rom, table=None):
    table = table or Table.load(ROOT / "tbl" / "jp.tbl")
    runs = pointer_runs(rom)
    in_run = set()  # bytes of the pointer tables themselves (a lone word in text can look like a pointer)
    for a, b in runs:
        if (b - a) // 4 >= MIN_RUN:
            in_run.update(range(a, b))
    out = []
    exclude = {version.at(x) for x in EXCLUDE}
    for a, b in runs:
        if (b - a) // 4 < MIN_RUN or a in exclude:
            continue
        slots = [p for p in range(a, b, 4) if _ptr(rom, p) not in in_run]
        targets = sorted({_ptr(rom, p) for p in slots})
        ok = True
        for t in targets:
            s = string_at(rom, t)
            if s is None or "[" in table.decode(s, 0, len(s))[0] or not in_run.isdisjoint(range(t, t + len(s))):
                ok = False
                break
        if ok and targets:
            out.append(TextTable(a, slots, targets))
    out.append(code_literals(rom, {x for tt in out for x in tt.targets}))
    return out


def code_literals(rom, targets):
    """Literal-pool words in the code region that hold a table string's exact start (the parts shop clerk's line,
    0x660AC -> 0x50D0F8, found by the poison build). Words pointing mid-string there are Thumb opcodes, not pointers.
    Returned as a pseudo-table with addr 0."""
    slots = [p for p in range(0, version.at(CODE_END), 4)
             if struct.unpack_from("<I", rom, p)[0] - GBA in targets]
    return TextTable(0, slots, sorted({struct.unpack_from("<I", rom, p)[0] - GBA for p in slots}))


if __name__ == "__main__":
    rom = Path(sys.argv[1]).read_bytes()
    tables = find_tables(rom)
    for tt in tables:
        print(f"{tt.addr:07X} slots={len(tt.slots):5d} strings={len(tt.targets):5d}")
    print(f"{len(tables)} tables, {sum(len(t.slots) for t in tables)} slots, "
          f"{len({x for t in tables for x in t.targets})} strings")
