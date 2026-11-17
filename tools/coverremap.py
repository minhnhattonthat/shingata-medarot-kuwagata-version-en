"""Carry text-coverage logs over to a build whose strings moved (a text edit shifts every later string).

    python -X utf8 tools/coverremap.py work/qa/sweep work/qa/sweep/strings_ef19ef1b.tsv \
        build/medarot_kuwagata_en.strings.tsv work/qa/sweep_remap

LOGDIR's log.txt files (any depth) ran on the build whose strings.tsv is OLD ("id<TAB>address"). Every "TEXT addr"
line is mapped old address -> string id -> NEW address and written to OUTDIR/log.txt, which textcover.py reads as
usual. Addresses that were no string start in OLD are dropped. A string counts as shown on the new build when it was
shown on the old one: valid for text-only edits, since the sweep shows each string by id in the same dialogue box.
After code, font or box changes, run a new sweep instead.
"""
import argparse
import glob
import os
import re
from pathlib import Path

TEXT = re.compile(r"^TEXT ([0-9A-Fa-f]+)", re.M)
MASK = 0x1FFFFFF


def table(path):
    rows = (l.split("\t") for l in Path(path).read_text(encoding="utf-8-sig").splitlines())
    return {r[0]: int(r[1], 16) & MASK for r in rows if len(r) > 1 and r[0] and not r[0].startswith("#")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logdir")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("outdir")
    a = ap.parse_args()
    by_addr = {addr: i for i, addr in table(a.old).items()}
    new = table(a.new)
    seen = set()
    for log in glob.glob(os.path.join(a.logdir, "**", "log.txt"), recursive=True):
        text = Path(log).read_text(encoding="utf-8", errors="replace")
        seen.update(by_addr[x] for x in (int(h, 16) & MASK for h in TEXT.findall(text)) if x in by_addr)
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    lines = [f"TEXT {new[i] | 0x8000000:X}" for i in sorted(seen) if i in new]
    (out / "log.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(seen)} string ids shown in {a.logdir}; {len(lines)} written to {out / 'log.txt'}")


if __name__ == "__main__":
    main()
