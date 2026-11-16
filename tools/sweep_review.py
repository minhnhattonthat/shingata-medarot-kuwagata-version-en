"""sweep_review.py: independent read-only review of the static graphics sweep (phase 1) with `codex exec`.

    python -X utf8 tools/sweep_review.py work/sweep/gba4 [--chunk 10] [--jobs 4] [--only 0,5,9]

For every chunk of sheets it runs one `codex exec` (read-only sandbox) with the sheets attached and writes its answer to
DIR/review/chunk_NNN.tsv: sheet, tile row, what the Japanese says, kind. Chunks with an answer already are skipped,
so a rerun only fills the gaps. Then `--merge` joins the answers with DIR/index.tsv into DIR/review/japanese.tsv
(sheet, row, block offset, codec, text, kind), the list docs/re/graphics.md draws from.
"""
import argparse
import csv
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROMPT = """You are reviewing graphics sheets ripped from a Japanese Game Boy Advance game (Shingata Medarot) for a fan
translation. Each attached image is one sheet, named sheet_NNN.png. A sheet is a grid of 8x8 tiles shown at 2x zoom,
so each tile row is 16 pixels tall: tile row R covers pixel y = 16*R to 16*R+15 (count R from 0 at the top). A red bar
at the left edge marks where a new graphics block starts. Dark purple is empty space. The images are grey-scale
renders of palette indices, so colours are wrong and some blocks look like noise: ignore noise.

List every place where Japanese text (kana or kanji, in any size or style: menu labels, titles, buttons, banners,
logos, font sheets, signs, words written on pictures) is drawn. Text split across tiles still counts. Do not list
English letters, digits or pure symbols unless they sit inside a Japanese word.

Reply with ONLY tab-separated lines, no header, no commentary, one line per text item:
sheet<TAB>row<TAB>text<TAB>kind
- sheet: the 3-digit number from the file name
- row: the tile row (integer) where the item's top is
- text: what it says as best you can read it (use ? for unreadable characters)
- kind: one of font (a whole character set / alphabet in order), label (a word or phrase), logo, other
If a sheet has no Japanese at all, write one line: sheet<TAB>-<TAB>none<TAB>none
"""


def run_chunk(d, idx, sheets, out):
    imgs = [str(p) for p in sheets]
    names = ", ".join(p.name for p in sheets)
    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "-o", str(out)]
    for p in imgs:
        cmd += ["-i", p]
    cmd += ["--", PROMPT + f"\nThe attached sheets are, in order: {names}\n"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
    ok = out.exists() and out.stat().st_size > 0
    return idx, r.returncode, ok


def merge(d):
    index = []
    with open(d / "index.tsv", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            index.append((int(row["sheet"]), int(row["row"]), row["offset"], row["codec"]))

    def block_at(sheet, row):
        best = None
        for s, r, o, c in index:
            if s == sheet and r <= row:
                best = (o, c)
        return best or ("?", "?")

    lines = []
    for p in sorted((d / "review").glob("chunk_*.tsv")):
        for ln in p.read_text(encoding="utf-8").splitlines():
            parts = ln.strip().split("\t")
            if len(parts) < 4 or parts[1] == "-" or not parts[0].isdigit():
                continue
            try:
                s, r = int(parts[0]), int(parts[1])
            except ValueError:
                continue
            o, c = block_at(s, r)
            lines.append((s, r, o, c, parts[2], parts[3]))
    with open(d / "review" / "japanese.tsv", "w", encoding="utf-8") as f:
        f.write("sheet\trow\toffset\tcodec\ttext\tkind\n")
        for t in sorted(lines):
            f.write("%03d\t%d\t%s\t%s\t%s\t%s\n" % t)
    print(f"{len(lines)} items -> {d / 'review' / 'japanese.tsv'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--chunk", type=int, default=10)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", help="comma list of chunk numbers")
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    d = Path(a.dir)
    (d / "review").mkdir(exist_ok=True)
    if a.merge:
        merge(d)
        return
    sheets = sorted(d.glob("sheet_*.png"))
    chunks = [sheets[i:i + a.chunk] for i in range(0, len(sheets), a.chunk)]
    only = {int(x) for x in a.only.split(",")} if a.only else None
    todo = []
    for i, ch in enumerate(chunks):
        out = d / "review" / f"chunk_{i:03d}.tsv"
        if (only is None or i in only) and not (out.exists() and out.stat().st_size > 0):
            todo.append((i, ch, out))
    print(f"{len(todo)} of {len(chunks)} chunks to run", flush=True)
    fails = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for idx, rc, ok in ex.map(lambda t: run_chunk(d, *t), todo):
            print(f"chunk {idx:03d}: rc={rc} {'ok' if ok else 'NO ANSWER'}", flush=True)
            fails += not ok
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
