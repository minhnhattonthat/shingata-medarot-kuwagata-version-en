"""grep_script.py: find script/ entries by regex on their English or Japanese (read-only).

    python -X utf8 tools/grep_script.py --en "Medabot Corp"       ids whose en matches
    python -X utf8 tools/grep_script.py --jp "メダロットしゃ"        ids whose jp matches
    python -X utf8 tools/grep_script.py --id 46E3EC 46E40D          those ids

Prints: id, table, kind, the batch .out.tsv holding the id (or "-" for a merged copy), en, jp.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def batches():
    where = {}
    for p in sorted((ROOT / "work/tl").glob("b*.out.tsv")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if "\t" in line:
                where[line.split("\t", 1)[0]] = p.stem.split(".")[0]
    return where


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    mode, args = argv[0], argv[1:]
    where = batches()
    for path in sorted((ROOT / "script").glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8"))["strings"]:
            en, jp = e.get("en") or "", e.get("jp") or ""
            hit = (mode == "--en" and re.search(args[0], en)) or (mode == "--jp" and re.search(args[0], jp)) \
                or (mode == "--id" and e["id"] in args)
            if hit:
                print(f"{e['id']}\t{path.stem}\t{e['kind']}\t{where.get(e['id'], '-')}\t{en}\t{jp}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
