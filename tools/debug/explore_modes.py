"""Shoot every (mode, sub) pair the main loop can switch to, from the field state, for the scene list.

usage: python -X utf8 tools/debug/explore_modes.py --modes 0-6 --subs 0-31 [--state S] [--frames 300] [--jobs 3]
Writes work/qa/modes/m<mode>_s<sub>/final.png and a contact sheet per mode (work/qa/modes/mode<m>.png).
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"


def rng(s):
    a, _, b = s.partition("-")
    return range(int(a, 0), int(b or a, 0) + 1)


def run(mode, sub, a):
    out = ROOT / "work" / "qa" / "modes" / f"m{mode}_s{sub}"
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(ROM), "--out", str(out),
           "--state-in", str(a.state), "--frames", str(a.frames), "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--var", f"RAWMODE={mode}", "--var", f"RAWSUB={sub}", "--var", f"RAWSTEP={a.step}", "--timeout", "120"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return mode, sub, r.returncode, out / "final.png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", default="0-6")
    ap.add_argument("--subs", default="0-31")
    ap.add_argument("--step", type=int, default=0)
    ap.add_argument("--state", default=str(ROOT / "work" / "states" / "field_home_2f.mss"))
    ap.add_argument("--frames", type=int, default=300)
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    pairs = [(m, s) for m in rng(a.modes) for s in rng(a.subs)]
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda p: run(p[0], p[1], a), pairs))
    for m in rng(a.modes):
        shots = [str(p) for mm, s, rc, p in res if mm == m and p.exists()]
        for mm, s, rc, p in res:
            if mm == m:
                print(f"m{m} s{s} exit {rc}")
        if shots:
            subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), *shots,
                            "--out", str(ROOT / "work" / "qa" / "modes" / f"mode{m}.png")])


if __name__ == "__main__":
    main()
