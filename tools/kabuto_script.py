"""kabuto_script.py: the Kabuto Version's string tables as an overlay on script/ (the Kuwagata script).

Writes script_kabuto/<Kabuto table offset>.json in tools/extract.py's format, one entry per string the Kabuto ROM's
tables reach (ids and slots are Kabuto offsets). An entry whose bytes are identical to a Kuwagata string gets
  "src": "<Kuwagata id>"
and no en of its own: rombuild.load_script() takes the en of that script/ entry, so every Kuwagata fix reaches the
Kabuto build. The source is the Kuwagata string at the same place (data/kabuto_map.tsv), else the identical string
in the same table nearest to it, else anywhere. Strings with no identical Kuwagata string (the version's own lines:
the Kabuto medal, the rhinoceros beetle, the starter's parts) keep their own en/status/notes, and "like" names the
Kuwagata string at their place when there is one (its translation is the model).

Rerunning keeps every own en/status/notes by id; a string that was own and now has a src (or the reverse) is listed.

    python -X utf8 tools/kabuto_script.py            # write script_kabuto/
    python -X utf8 tools/kabuto_script.py --check    # exit 1 if script_kabuto/ is not what the ROMs give
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbl import Table  # noqa: E402
import extract  # noqa: E402
import texttables  # noqa: E402
import version  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OWN = ("en", "status", "notes")


def kuwagata_strings():
    """({Kuwagata string offset: (table offset, bytes)}, {id: script/ entry})."""
    prev = version.current().name
    version.select(version.BASE)
    try:
        rom = version.VERSIONS[version.BASE].rom.read_bytes()
        tables = texttables.find_tables(rom)
    finally:
        version.select(prev)
    out = {}
    for tt in tables:
        for t in tt.targets:
            out.setdefault(t, (tt.addr, texttables.string_at(rom, t)))
    entries = {}
    for path in sorted((ROOT / "script").glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8"))["strings"]:
            entries[e["id"]] = e
    return out, entries


def dump(old=None):
    """{file name: document} for script_kabuto/. old: {id: previous entry} (own fields are kept)."""
    old = old or {}
    version.select("kabuto")
    rom = version.current().rom.read_bytes()
    table = Table.load(ROOT / "tbl" / "jp.tbl")
    kuw, kuw_entries = kuwagata_strings()
    tables = texttables.find_tables(rom, table)

    def at(off):
        try:
            return version.at(off)
        except KeyError:
            return None

    placed = {}       # Kabuto offset -> Kuwagata offset at the same place
    by_bytes = {}     # bytes -> [Kuwagata offsets]
    for o, (_, s) in kuw.items():
        b = at(o)
        if b is not None:
            placed[b] = o
        by_bytes.setdefault(s, []).append(o)
    base_table = {}   # Kabuto table offset -> Kuwagata table offset
    for t in {tt for tt, _ in kuw.values()}:
        if t and at(t) is not None:
            base_table[at(t)] = t

    slots_of = {}
    for tt in tables:
        for p in tt.slots:
            v = int.from_bytes(rom[p:p + 4], "little") - texttables.GBA
            slots_of.setdefault(v, set()).add(p)
    spans = sorted((o, o + len(texttables.string_at(rom, o))) for o in slots_of)

    def tail_of(off):
        for a, b in spans:
            if a < off < b:
                return a
        return None

    docs, seen = {}, set()
    for tt in tables:
        if not tt.addr:
            continue
        strings = []
        for off in tt.targets:
            if off in seen:
                continue
            seen.add(off)
            s = texttables.string_at(rom, off)
            e = extract.entry(rom, table, off, slots_of[off], tail_of(off))
            for f in OWN:
                del e[f]
            src = placed.get(off)
            if src is None or kuw[src][1] != s:
                cands = by_bytes.get(s, [])
                same_table = [c for c in cands if kuw[c][0] == base_table.get(tt.addr)]
                pick = same_table or cands
                src = min(pick, key=lambda c: (abs((at(c) or 1 << 30) - off), c)) if pick else None
            if src is not None:
                e["src"] = f"{src:06X}"
                if f"{src:06X}" not in kuw_entries:
                    raise ValueError(f"{off:06X}: source {src:06X} is not in script/")
            else:
                like = placed.get(off)
                if like is not None:
                    e["like"] = f"{like:06X}"
                o = old.get(e["id"], {})
                for f in OWN:
                    e[f] = o.get(f, "new" if f == "status" else "")
            strings.append(e)
        if strings:
            doc = {"table": f"{tt.addr:06X}", "base_table": f"{base_table[tt.addr]:06X}"
                   if tt.addr in base_table else None,
                   "about": extract.ABOUT.get(base_table.get(tt.addr), ""), "strings": strings}
            docs[f"{tt.addr:06X}.json"] = doc
    return docs


def load_old(root):
    old = {}
    for path in sorted(root.glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8"))["strings"]:
            old[e["id"]] = e
    return old


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    import check_rom
    root = version.VERSIONS["kabuto"].script
    check_rom.check(check_rom.LISTINGS["kabuto"])
    old = load_old(root)
    docs = dump(old)
    if a.check:
        bad = [n for n, d in docs.items() if not (root / n).exists() or
               json.loads((root / n).read_text(encoding="utf-8")) != d]
        bad += [p.name for p in root.glob("*.json") if p.name not in docs]
        if bad:
            print(f"script_kabuto/ out of date ({len(bad)} files): {' '.join(sorted(bad)[:8])}; run tools/kabuto_script.py")
            return 1
        print("script_kabuto/ up to date")
        return 0
    root.mkdir(exist_ok=True)
    for p in root.glob("*.json"):
        if p.name not in docs:
            p.unlink()
    flipped = []
    for name, doc in docs.items():
        for e in doc["strings"]:
            o = old.get(e["id"])
            if o and ("src" in o) != ("src" in e) and (o.get("en") or e.get("en") is not None):
                flipped.append(e["id"])
        extract.write_doc(root / name, doc)
    n = sum(len(d["strings"]) for d in docs.values())
    own = [e for d in docs.values() for e in d["strings"] if "src" not in e]
    print(f"script_kabuto/: {len(docs)} files, {n} strings, {n - len(own)} shared with script/, {len(own)} own "
          f"({sum(1 for e in own if not e['en'])} untranslated)")
    if flipped:
        print(f"src changed for {len(flipped)} ids: {' '.join(flipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
