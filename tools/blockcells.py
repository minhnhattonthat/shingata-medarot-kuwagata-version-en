"""blockcells.py: which BG map cells show a block's tiles (for gfx/labels.json block "layout"s).

    python -X utf8 tools/blockcells.py SCENE TILE0 COUNT [--rows 0-20]

Reads the VRAM/IO dump `tools/screenfind.py SCENE` left in work/gfx/s_SCENE/, and prints per enabled BG and map
row the cells whose tile number lies in [TILE0, TILE0+COUNT) as block-relative numbers ('.' = other tile,
h/v = flipped). Copy the rows a label needs into its "layout" (null for cells you must not touch).
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene")
    ap.add_argument("tile0", type=int)
    ap.add_argument("count", type=int)
    ap.add_argument("--rows", default="0-31")
    a = ap.parse_args(argv)
    d = ROOT / "work" / "gfx" / f"s_{a.scene}"
    vram = next(d.glob("*.vram.bin"), None)
    io = next(d.glob("*.io.bin"), None)
    if not vram or not io:
        sys.exit(f"no dump in {d}: run tools/screenfind.py {a.scene} first")
    v, regs = vram.read_bytes(), io.read_bytes()
    r0, r1 = (int(x) for x in a.rows.split("-"))
    dispcnt = struct.unpack_from("<H", regs, 0)[0]
    for bg in range(4):
        if not dispcnt & (0x100 << bg):
            continue
        cnt = struct.unpack_from("<H", regs, 8 + 2 * bg)[0]
        base = ((cnt >> 8) & 31) * 0x800
        lines = []
        for my in range(r0, r1 + 1):
            cells = []
            for mx in range(32):
                e = struct.unpack_from("<H", v, base + (my * 32 + mx) * 2)[0]
                t = e & 0x3FF
                if a.tile0 <= t < a.tile0 + a.count:
                    flip = ("h" if e & 0x400 else "") + ("v" if e & 0x800 else "")
                    cells.append(f"{t - a.tile0}{flip}")
                else:
                    cells.append(".")
            if any(c != "." for c in cells):
                lines.append(f"  row {my:2d}: " + " ".join(cells))
        if lines:
            print(f"BG{bg} (screen {base:05X})")
            print("\n".join(lines))


if __name__ == "__main__":
    main()
