"""pairs.py: reviewer input for translated batches (docs/reviewer-brief.md).

    python -X utf8 tools/pairs.py b070 b071 ...     -> work/tl/review/<first>.pairs.txt (one file for the group)

Each entry: `>> id | JP` then `   EN`, in batch order (batches are in ROM order, so neighbours are the context).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"


def rows(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(batches):
    out = []
    for b in batches:
        en = {r[0]: "\t".join(r[1:]) for r in rows(TL / f"{b}.out.tsv")}
        out.append(f"## batch {b}")
        for r in rows(TL / f"{b}.tsv"):
            out.append(f">> {r[0]} | {r[4]}")
            out.append(f"   {en.get(r[0], '(missing)')}")
    dest = TL / "review" / f"{batches[0]}.pairs.txt"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(dest)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main(sys.argv[1:])
