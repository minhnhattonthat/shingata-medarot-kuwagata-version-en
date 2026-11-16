"""Map tour: warp to every map id from a field state and take one shot each (area banners, signs, map graphics).

usage: python -X utf8 tools/debug/maptour.py [--from 0 --to 140] [--jobs 2] [--state work/states/home_2f.mss]
       [--hold 90] [ROM]
Each map is its own run of warp.lua (MAP=n, X/Y = the first door entry of that map that leads in, else 5,5) from
the state. Shots: work/qa/maps/m<nnn>/arrived.png (+ f<frame>.png every 30 frames for the banner);
sheet: work/qa/maps/sheet*.png. Exit 1 if any map run did not log ARRIVED.
"""
import argparse
import shutil
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
DOORS = 0x4B6248  # u32 pointer per map id -> 8-byte entries, 0xFF-terminated (docs/re/debug.md §Door warps)


def arrivals(rom, nmaps=141):
    """map id -> (x, y): the destination tile of the first door that leads into it."""
    dest = {}
    for m in range(nmaps):
        p = struct.unpack_from("<I", rom, DOORS + 4 * m)[0] - 0x08000000
        if not 0 <= p < len(rom):
            continue
        for k in range(64):
            e = rom[p + 8 * k:p + 8 * k + 8]
            if len(e) < 8 or e[0] == 0xFF:
                break
            dest.setdefault(e[2], (e[6], e[7]))
    return dest


def run(m, xy, a):
    out = ROOT / "work" / "qa" / "maps" / f"m{m:03d}"
    x, y = xy
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(a.rom), "--out", str(out),
           "--state-in", str(Path(a.state).resolve()), "--frames", "900", "--timeout", "300", "--shot-every", "30",
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"MAP={m}", "--var", f"X={x}",
           "--var", f"Y={y}", "--var", f"HOLD={a.hold}", "--var", "STOP=1", "--var", "NOENC=1"]
    subprocess.run(cmd, capture_output=True, text=True)
    log = out / "log.txt"
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    arrived = [ln for ln in text.splitlines() if ln.startswith("ARRIVED")]
    return m, bool(arrived), arrived[0] if arrived else text[-160:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(DEFAULT_ROM))
    ap.add_argument("--from", dest="lo", type=int, default=0)
    ap.add_argument("--to", dest="hi", type=int, default=140)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--hold", type=int, default=90)
    ap.add_argument("--state", default=str(ROOT / "work" / "states" / "home_2f.mss"))
    a = ap.parse_args()
    dest = arrivals(Path(a.rom).read_bytes())
    maps = list(range(a.lo, a.hi + 1))
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda m: run(m, dest.get(m, (5, 5)), a), maps))
    bad = 0
    for m, ok, info in res:
        print(f"{'ok  ' if ok else 'FAIL'} map {m:3d} {dest.get(m, (5, 5))} {info.strip()}")
        bad += not ok
    shots = []
    for m, ok, _ in res:  # one file per map, named so the sheet labels each tile with its map id
        if ok:
            dst = ROOT / "work" / "qa" / "maps" / "shots" / f"m{m:03d}.png"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / "work" / "qa" / "maps" / f"m{m:03d}" / "arrived.png", dst)
            shots.append(str(dst))
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), *shots,
                        "--out", str(ROOT / "work" / "qa" / "maps" / "sheet.png")])
    print(f"{len(res) - bad}/{len(res)} maps arrived")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
