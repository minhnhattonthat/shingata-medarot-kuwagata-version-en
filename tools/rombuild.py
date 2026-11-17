"""rombuild.py: unpack the original ROM's script and repack it. build.py is the command; tests import this.

Text stage: every string of script/*.json (tools/extract.py) is encoded from its `en` text, or its `jp` text while `en`
is empty. A string whose bytes are unchanged stays where it is; any other (or every string, with relocate_all=True) is
written to free space past the original 8 MiB and every slot that pointed at it is repointed. The original bytes of a
moved string are left in place, so a reference the tables don't know about still reads valid text.
Graphics stage: LZ77 and "Le" blocks stay as the original bytes; tools/lz77.py and tools/le.py are not the game's
packer (docs/re/rom.md), so a block is recompressed only when an edited asset replaces it (phase 8).

With no edits the output is byte-identical to the original ROM: tests/test_identity.py.
"""
import json
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbl import Table  # noqa: E402
import texttables  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"
GBA = texttables.GBA
ORIG_SIZE = 0x800000
FREE_START = ORIG_SIZE         # space past the original end (docs/re/rom.md)
MAX_SIZE = 0x1000000           # EEPROM addressing: never past 16 MiB
PAD = 0x100000                 # an expanded ROM is padded with 0xFF to a 1 MiB boundary


@dataclass
class Report:
    strings: int = 0
    in_place: int = 0
    moved: int = 0
    slots_repointed: int = 0
    writes: list = field(default_factory=list)  # (offset, orig bytes, new bytes, writer) for romdiff --writes
    placed: dict = field(default_factory=dict)  # original string offset -> ROM offset the build's slots reach


class Rom:
    """A byte buffer that logs every write against the original."""

    def __init__(self, orig):
        self.orig = bytes(orig)
        self.buf = bytearray(orig)
        self.writes = []

    def write(self, off, data, writer):
        end = off + len(data)
        if end > MAX_SIZE:
            raise ValueError(f"{writer}: write {off:#x}+{len(data)} runs past 16 MiB")
        if end > len(self.buf):
            self.buf += b"\xff" * (end - len(self.buf))
        old = bytes(self.buf[off:end])
        if old != data:
            self.writes.append((off, old, bytes(data), writer))
        self.buf[off:end] = data

    def finish(self):
        if len(self.buf) > len(self.orig):
            size = -(-len(self.buf) // PAD) * PAD
            self.buf += b"\xff" * (size - len(self.buf))
        return bytes(self.buf)


POISON = 0x01  # ア: what a poisoned build shows wherever the game reads a moved string through an unknown reference


def poisoned(s):
    """The string with every glyph byte replaced by POISON; control codes, their arguments and the terminator kept."""
    out = bytearray(s)
    p = 0
    while p < len(s):
        b = s[p]
        if b >= 0xF7:
            p += 1 + texttables.ARGS.get(b, 1 if b == 0xFF else 0)
            continue
        if b != 0x00:          # keep spaces so word wrap is unchanged
            out[p] = POISON
        p += 1
    return bytes(out)


def load_script(lang="en", root=SCRIPT):
    """[(string offset, [slot offsets], text)] from script/*.json: text = the `lang` field, or `jp` while it is empty.
    Strings with no slots (script/unused.json) are left out: nothing reads them."""
    out = []
    for path in sorted(Path(root).glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8"))["strings"]:
            if e["slots"]:
                out.append((int(e["id"], 16), [int(s, 16) for s in e["slots"]], e.get(lang) or e["jp"]))
    if not out:
        raise FileNotFoundError(f"no strings in {root}: run tools/extract.py")
    return out


def text_stage(rom, entries, table, strings=None, relocate_all=False, poison=False, report=None):
    """entries: load_script(). strings: {original string offset: new encoded bytes}, overriding the entry's text.
    poison: overwrite the original copy of every moved string (poisoned()), to find references the tables miss."""
    report = report or Report()
    strings = strings or {}
    slots_of, text_of = {}, {}
    for off, slots, text in entries:
        slots_of.setdefault(off, []).extend(slots)
        text_of[off] = text
    free = max(FREE_START, len(rom.buf))
    moved = []
    for off in sorted(slots_of):
        old = texttables.string_at(rom.orig, off)
        for s in slots_of[off]:
            if struct.unpack_from("<I", rom.orig, s)[0] - GBA != off:
                raise ValueError(f"script: slot {s:06X} of {off:06X} does not point at it in the original ROM")
        new = strings.get(off)
        if new is None:
            new = table.encode(text_of[off])
        report.strings += 1
        if not relocate_all and new == old:
            report.in_place += 1
            report.placed[off] = off
            continue
        report.placed[off] = free
        rom.write(free, new, f"text {off:07X}")
        for s in slots_of[off]:
            rom.write(s, struct.pack("<I", GBA + free), f"ptr {s:07X}->{off:07X}")
            report.slots_repointed += 1
        free += len(new)
        report.moved += 1
        moved.append(off)
    if poison:
        # after all moves: a string can sit inside another (shared tails), so poison from the original bytes
        for off in moved:
            rom.write(off, poisoned(texttables.string_at(rom.orig, off)), f"poison {off:07X}")
    return report


def en_table():
    """tbl/jp.tbl with tbl/en.tbl on top: Japanese text encodes exactly as before (jp lines come first, and the first
    code given for a character wins), and every English character has a code."""
    lines = []
    for name in ("jp.tbl", "en.tbl"):
        lines += (ROOT / "tbl" / name).read_text(encoding="utf-8-sig").splitlines()
    return Table(lines)


def has_lang(lang="en", root=SCRIPT):
    """True once any string of script/ has a `lang` text."""
    return any(e.get(lang) for path in Path(root).glob("*.json")
               for e in json.loads(path.read_text(encoding="utf-8"))["strings"])


def build(orig, strings=None, relocate_all=False, poison=False, lang="en", script=SCRIPT, font=None):
    """Returns (rom bytes, Report). font: put in the English font (tools/font.py); None = only once script/ has
    `lang` text or `strings` is given, so the build stays byte-identical until then."""
    import font as fontmod
    table = en_table()
    rom = Rom(orig)
    if font is None:
        font = bool(strings) or has_lang(lang, script)
    if font:
        end = fontmod.font_stage(rom, max(FREE_START, len(rom.buf)))
        end = fontmod.names_stage(rom, end)
        import gfx
        import minifont
        end = gfx.gfx_stage(rom, end)
        end = minifont.stage(rom, end)
        import nameentry
        nameentry.stage(rom, end)
    entries = load_script(lang, script)
    if font:
        import credits
        credits.stage(rom, entries, table, strings)
    report = text_stage(rom, entries, table, strings, relocate_all, poison)
    report.writes = rom.writes
    return rom.finish(), report


def write_log(report, path):
    with open(path, "w", encoding="utf-8") as f:
        for off, old, new, writer in report.writes:
            f.write(f"{off:07X} {old.hex()} {new.hex()} {writer}\n")
