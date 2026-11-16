"""Prove every scene of tools/debug/scenes.txt from a cold boot and regenerate work/states/<scene>.mss.

usage: python -X utf8 tools/debug/prove.py [ROM] [--only a,b] [--jobs 4] [--no-states]
Each scene is its own cold-boot run of warp.lua (new game, intro, then the scene). A scene passes when its log
has "ARRIVED". Shots: work/qa/scenes/<scene>/arrived.png, copied to work/qa/scenes/shots/<scene>.png; sheet of all
proven scenes: work/qa/scenes/sheet*.png. Exit 1 on any failure.
After engine, font or graphics changes, re-run this to regenerate the state library.
"""
import argparse
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
SCENES = ROOT / "tools" / "debug" / "scenes.txt"


def scene_names():
    names = []
    for line in SCENES.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "\t" in line:
            names.append(line.split("\t", 1)[0])
    return names


def run(name, a):
    out = ROOT / "work" / "qa" / "scenes" / name
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(a.rom), "--out", str(out),
           "--frames", "15000", "--timeout", "600", "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--var", f"SCENE='{name}'", "--var", "STOP=1"]
    if not a.no_states:
        state = (ROOT / "work" / "states" / f"{name}.mss").as_posix()
        cmd += ["--var", f"SAVE='{state}'"]
    subprocess.run(cmd, capture_output=True, text=True)
    log = out / "log.txt"
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    arrived = [ln for ln in text.splitlines() if ln.startswith("ARRIVED")]
    return name, bool(arrived) and (out / "arrived.png").exists(), arrived[0] if arrived else text[-200:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(DEFAULT_ROM))
    ap.add_argument("--only")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--no-states", action="store_true")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else scene_names()
    (ROOT / "work" / "states").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda n: run(n, a), names))
    bad = 0
    for name, ok, info in res:
        print(f"{'ok  ' if ok else 'FAIL'} {name:16s} {info.strip()}")
        bad += not ok
    # one named copy per scene, so the sheet labels tiles by scene and an --only run keeps the others on it
    shot_dir = ROOT / "work" / "qa" / "scenes" / "shots"
    shot_dir.mkdir(parents=True, exist_ok=True)
    for n, ok, _ in res:
        if ok:
            shutil.copyfile(ROOT / "work" / "qa" / "scenes" / n / "arrived.png", shot_dir / f"{n}.png")
    names = set(scene_names())
    shots = [str(p) for p in sorted(shot_dir.glob("*.png")) if p.stem in names]
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), *shots,
                        "--out", str(ROOT / "work" / "qa" / "scenes" / "sheet.png")])
    print(f"{len(res) - bad}/{len(res)} scenes arrived")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
