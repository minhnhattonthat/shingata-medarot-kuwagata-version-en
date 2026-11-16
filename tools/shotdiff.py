"""shotdiff.py: compare two dirs of same-named shots (e.g. prove.py runs of two ROMs), pixel by pixel.

    python -X utf8 tools/shotdiff.py work/qa/scenes/shots work/qa/scenes_poison/shots [--out work/qa/shotdiff]

Prints one line per name: identical, or the share of differing pixels and their bounding box. With --out, writes a
side-by-side pair (sheet.py --compare) for every differing name. Exit 1 if any pair differs or a name is missing.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill import SKILL  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    names = sorted({p.name for p in a.a.glob("*.png")} | {p.name for p in a.b.glob("*.png")})
    bad = 0
    for n in names:
        pa, pb = a.a / n, a.b / n
        if not (pa.exists() and pb.exists()):
            print(f"MISSING  {n} ({'b' if pa.exists() else 'a'} side)")
            bad += 1
            continue
        ia, ib = Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")
        if ia.size != ib.size:
            print(f"SIZE     {n} {ia.size} vs {ib.size}")
            bad += 1
            continue
        d = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v else 0)
        box = d.getbbox()
        if not box:
            print(f"same     {n}")
            continue
        share = sum(d.histogram()[255:]) / (ia.size[0] * ia.size[1])
        print(f"DIFF     {n} {share:.2%} box={box}")
        bad += 1
        if a.out:
            a.out.mkdir(parents=True, exist_ok=True)
            subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), str(pa),
                            "--compare", str(pb), "--out", str(a.out / n)], capture_output=True)
    print(f"{len(names) - bad}/{len(names)} identical")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
