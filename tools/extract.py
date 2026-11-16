"""extract.py: dump the script of the ORIGINAL ROM into script/*.json (phase 4).

One file per text table (`script/<table offset>.json`, texttables.find_tables) plus `script/unused.json` (strings no
pointer reaches, textmap.UNUSED). A string reached from several tables is written once, in the first table's file,
with every slot that points at it. Entry fields:
  id       string offset (hex): stable, address-based
  slots    offsets of the u32 pointer slots that point at it (repointed when the string moves)
  kind     "ff" (dialogue/message, ends `FF xx`) or "fe" (list entry: names, ends `FE`)
  bytes    original length in bytes, terminator included
  tail_of  id of a longer string this one is the tail of (the game shares the bytes), when it is
  jp       the text through tbl/jp.tbl, control codes and terminator included ({end:00}, {item} = FE)
  en       the translation ("" = not translated: the build keeps the Japanese)
  status   new / translated / reviewed ...;  notes  free text
Leading and trailing spaces are text: nothing here strips.

Dump never clobbers a translation: an existing file is skipped; with --force it is rewritten from the ROM, keeping
en/status/notes per id, and ids whose jp changed are listed (re-check their translations).

    python -X utf8 tools/extract.py [--force]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbl import Table  # noqa: E402
import texttables  # noqa: E402
import textmap  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
SCRIPT = ROOT / "script"
LANG_FIELDS = ("en",)          # one text field per target language
KEEP = (*LANG_FIELDS, "status", "notes")

ABOUT = {  # docs/re/text.md §Name lists and §Text ranges
    0x464BDC: "system messages (save data)",
    0x465B8C: "medal names",
    0x465C84: "skill types",
    0x466374: "actions",
    0x466688: "attack names",
    0x468308: "Medabot names",
    0x468A00: "part names",
    0x469450: "part model codes",
    0x46A508: "weapon kinds",
    0x46A6F0: "leg types",
    0x46A744: "terrain",
    0x46E60C: "character names",
    0x46EDA0: "battle menu",
    0x46F0BC: "battle status messages",
    0x4702F0: "battle messages",
    0x4B50CC: "signs and books",
    0x4B7654: "system messages (items, medals, money)",
    0x50A9D8: "text bank A: event dialogue (intro, town)",
    0x50C998: "item names",
    0x50EF18: "tutorial topics",
    0x510C28: "staff credits",
}


def entry(rom, table, off, slots, tail_of):
    s = texttables.string_at(rom, off)
    e = {"id": f"{off:06X}", "slots": [f"{p:06X}" for p in sorted(slots)], "kind": "fe" if s[-1] == 0xFE else "ff",
         "bytes": len(s)}
    if tail_of is not None:
        e["tail_of"] = f"{tail_of:06X}"
    e["jp"] = table.decode(s, 0, len(s))[0]
    for f in LANG_FIELDS:
        e[f] = ""
    e["status"] = "new"
    e["notes"] = ""
    return e


def dump(rom, table=None):
    """{file name: document} for the whole script."""
    table = table or Table.load(ROOT / "tbl" / "jp.tbl")
    tables = texttables.find_tables(rom, table)
    slots_of = {}
    for tt in tables:
        for p in tt.slots:
            slots_of.setdefault(texttables._ptr(rom, p) if tt.addr else
                                int.from_bytes(rom[p:p + 4], "little") - texttables.GBA, set()).add(p)
    spans = sorted((o, o + len(texttables.string_at(rom, o))) for o in slots_of)
    spans += sorted((o, o + len(textmap.unused_at(rom, o))) for o, _ in textmap.UNUSED)

    def tail_of(off):
        for a, b in spans:
            if a < off < b:
                return a
        return None

    docs, seen = {}, set()
    for tt in tables:
        if not tt.addr:
            continue  # code literals: their strings belong to a table; the slots were merged above
        strings = []
        for off in tt.targets:
            if off in seen:
                continue
            seen.add(off)
            strings.append(entry(rom, table, off, slots_of[off], tail_of(off)))
        if strings:
            docs[f"{tt.addr:06X}.json"] = {"table": f"{tt.addr:06X}", "about": ABOUT.get(tt.addr, ""),
                                           "strings": strings}
    notes = dict(textmap.UNUSED)
    unused = []
    for off, _ in textmap.UNUSED:
        e = entry(rom, table, off, [], tail_of(off))
        e["notes"] = notes[off]
        unused.append(e)
    docs["unused.json"] = {"table": None, "about": "strings no pointer reaches (not shown in game; not built)",
                           "strings": unused}
    return docs


def write_doc(path, doc):
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rom", type=Path, default=ROM)
    ap.add_argument("--force", action="store_true", help="rewrite existing files, keeping en/status/notes per id")
    args = ap.parse_args()
    rom = args.rom.read_bytes()
    SCRIPT.mkdir(exist_ok=True)
    wrote = skipped = 0
    changed = []
    for name, doc in dump(rom).items():
        path = SCRIPT / name
        if path.exists():
            if not args.force:
                skipped += 1
                continue
            old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))["strings"]}
            for e in doc["strings"]:
                o = old.get(e["id"])
                if o:
                    for k in KEEP:
                        if k in o:
                            e[k] = o[k]
                    if o["jp"] != e["jp"] and any(o.get(f) for f in LANG_FIELDS):
                        changed.append(e["id"])
        write_doc(path, doc)
        wrote += 1
    print(f"script/: {wrote} files written, {skipped} existing skipped (--force rewrites, keeping translations)")
    if changed:
        print(f"jp changed under an existing translation ({len(changed)}): {' '.join(changed)}")


if __name__ == "__main__":
    main()
