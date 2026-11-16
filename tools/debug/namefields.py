"""namefields.py: where the menu-name sprites sit on a screen (width gate for list fields).

    python -X utf8 tools/debug/namefields.py SCENE [SCENE..] [--rom ROM]

Loads work/states/<scene>.mss, dumps OAM, and prints every row of name-charset sprites (8x8 tiles 0x320-0x3EE, the
sprite charset of docs/re/text.md §Font): y, first x, last x + 8, char count, and the decoded text (jp.tbl). The
field budget is the x of the next thing on the row minus the first x; read that off the shot printed beside it.
"""
import argparse
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402
import tbl  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
BASE, LAST = 0x320, 0x3EE


def rows(oam, table):
    found = {}
    for i in range(128):
        a0, a1, a2 = struct.unpack_from("<HHH", oam, i * 8)
        if a0 & 0x300 == 0x200 or (a0 >> 14) or (a1 >> 14):
            continue
        t = a2 & 0x3FF
        if BASE <= t <= LAST:
            found.setdefault(a0 & 0xFF, []).append((a1 & 0x1FF, t - BASE + 1))
    for y, cells in sorted(found.items()):
        cells.sort()
        runs, cur = [], [cells[0]]
        for c in cells[1:]:  # a gap wider than one cell starts another field (name, then price)
            if c[0] - cur[-1][0] > 12:
                runs.append(cur)
                cur = []
            cur.append(c)
        runs.append(cur)
        for i, run in enumerate(runs):
            text = table.decode(bytes(c for _, c in run), length=len(run))[0]
            nxt = runs[i + 1][0][0] if i + 1 < len(runs) else None
            yield y, run[0][0], run[-1][0] + 8, len(run), text, nxt


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="+")
    ap.add_argument("--rom", default=str(ROM))
    a = ap.parse_args()
    table = tbl.Table.load(ROOT / "tbl" / "jp.tbl")
    for scene in a.scenes:
        out = ROOT / "work" / "qa" / "namefields" / scene
        out.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), a.rom, "--out", str(out),
               "--state-in", str(ROOT / "work" / "states" / f"{scene}.mss"), "--frames", "30",
               "--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "ppudump.lua")]
        subprocess.run(cmd, check=True, capture_output=True)
        oam = (out / "ppu_000029.oam.bin").read_bytes()
        print(f"{scene}: shot {out / 'final.png'}")
        for y, x0, x1, n, text, nxt in rows(oam, table):
            after = f"  next sprite field at x={nxt}" if nxt is not None else ""
            print(f"  y={y:3} x={x0:3}..{x1:3} ({x1 - x0:3} px, {n:2} chars) {text}{after}")


if __name__ == "__main__":
    main()
