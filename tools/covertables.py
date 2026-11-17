"""Text coverage per script table: textcover.py's shown/missing strings grouped by the script/<table>.json they belong to.

    python -X utf8 tools/covertables.py LOGDIR [LOGDIR ..] [--strings build/medarot_kuwagata_en.strings.tsv]
                                       [--waive docs/text_unshown.tsv] [--list TABLE]

Reads every log.txt under the LOGDIRs (TEXT <hex address> lines from prove.py --probes / eventtour.py), maps the build's
string addresses (mask 0x1FFFFFF) back to their ids and prints, per table: shown / total / waived, and its "about".
--list TABLE prints that table's never-shown ids with their English, to pick scenes or write waivers.
--write-waivers rewrites docs/text_unshown.tsv: one line per `fe` name-list entry (drawn by list/strcpy code, which
tools/debug/sweep.py can't drive) and per unused.json string (no pointer reaches it), keyed by string id, so the
file holds for every build. `ff` strings get no waiver: sweep.py shows each in the dialogue box.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = re.compile(r"^TEXT ([0-9A-Fa-f]+)", re.M)
MASK = 0x1FFFFFF


def shown(dirs):
    out = set()
    for d in dirs:
        for f in Path(d).rglob("log.txt"):
            out.update(int(a, 16) & MASK for a in TEXT.findall(f.read_text(encoding="utf-8", errors="replace")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logdirs", nargs="+")
    ap.add_argument("--strings", default=str(ROOT / "build" / "medarot_kuwagata_en.strings.tsv"))
    ap.add_argument("--waive", default=str(ROOT / "docs" / "text_unshown.tsv"))
    ap.add_argument("--list")
    ap.add_argument("--write-waivers", action="store_true")
    a = ap.parse_args()
    if a.write_waivers:
        rows = ["# id\treason (tools/covertables.py --write-waivers; textcover.py --waive)\n"]
        for f in sorted((ROOT / "script").glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            about = d.get("about") or f"table {f.stem}"
            for s in d["strings"]:
                if f.stem == "unused":
                    rows.append(f"{s['id']}\tunused.json: no pointer reaches this string, the game never shows it\n")
                elif s.get("kind") == "fe":
                    rows.append(f"{s['id']}\tFE list entry ({about}): drawn by list/strcpy/sprite code, not the "
                                f"dialogue runner, so sweep.py can't show it; width checked by lint, the list's "
                                f"screen seen in the scene tour\n")
        Path(a.waive).write_text("".join(rows), encoding="utf-8")
        print(f"{len(rows) - 1} waivers -> {a.waive}")
        return
    addr = {}
    for ln in Path(a.strings).read_text(encoding="utf-8").splitlines():
        if ln.strip():
            i, h = ln.split("\t")[:2]
            addr[i] = int(h, 16) & MASK
    waived = set()
    if Path(a.waive).exists():
        for ln in Path(a.waive).read_text(encoding="utf-8").splitlines():
            p = ln.split("\t")
            if len(p) >= 2 and p[1].strip() and not ln.startswith("#"):
                waived.add(p[0])
    seen = shown(a.logdirs)
    tot = [0, 0, 0]
    for f in sorted((ROOT / "script").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        ids = [s["id"] for s in d["strings"] if s["id"] in addr]
        if not ids:
            continue
        ok = [i for i in ids if addr[i] in seen]
        wv = [i for i in ids if addr[i] not in seen and i in waived]
        tot[0] += len(ok)
        tot[1] += len(ids)
        tot[2] += len(wv)
        if a.list:
            if f.stem == a.list:
                for s in d["strings"]:
                    if s["id"] in addr and addr[s["id"]] not in seen and s["id"] not in waived:
                        print(f"{s['id']}\t{s.get('en', '')[:100]}")
            continue
        print(f"{f.stem:8} {len(ok):5}/{len(ids):<5} waived {len(wv):5}  {d.get('about', '')[:60]}")
    if not a.list:
        print(f"total    {tot[0]:5}/{tot[1]:<5} waived {tot[2]:5}, open {tot[1] - tot[0] - tot[2]}")


if __name__ == "__main__":
    main()
