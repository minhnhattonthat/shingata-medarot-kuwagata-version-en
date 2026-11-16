"""Prove every scene of tools/debug/scenes.txt from a cold boot and regenerate work/states/<scene>.mss.

usage: python -X utf8 tools/debug/prove.py [ROM] [--only a,b] [--jobs 4] [--no-states] [--qa DIR]
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


def text_ranges(rom):
    """GBA address ranges holding the strings of ROM's build (its .strings.tsv), else the original text region."""
    tsv = Path(rom).with_suffix(".strings.tsv")
    ranges = ["8464000-8512000"]
    if tsv.exists():
        moved = [int(ln.split("\t")[1], 16) for ln in tsv.read_text(encoding="utf-8").splitlines()
                 if int(ln.split("\t")[1], 16) >= 0x08800000]
        if moved:
            ranges.append(f"{min(moved):X}-{max(moved) + 0x200:X}")
    return ",".join(ranges)


def run(name, a):
    out = a.qa / name
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(a.rom), "--out", str(out),
           "--frames", "15000", "--timeout", "600", "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--var", f"SCENE='{name}'", "--var", "STOP=1"]
    if a.probes:
        # text coverage (every string's first-byte read, textcover.py) + who sets the alternate-font flag state+0x27
        cmd += ["--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "textcover.lua"),
                "--var", f"RANGES='{text_ranges(a.rom)}'",
                "--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "watch.lua"),
                "--var", "WATCH_LO=0x03000547"]
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
    ap.add_argument("--probes", action="store_true",
                    help="log text reads (TEXT lines for textcover.py) and writes to state+0x27 (0x03000547)")
    ap.add_argument("--qa", type=Path, default=ROOT / "work" / "qa" / "scenes",
                    help="output dir (another ROM: keep the original's shots, e.g. work/qa/scenes_poison)")
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
    shot_dir = a.qa / "shots"
    shot_dir.mkdir(parents=True, exist_ok=True)
    for n, ok, _ in res:
        if ok:
            shutil.copyfile(a.qa / n / "arrived.png", shot_dir / f"{n}.png")
    names = set(scene_names())
    shots = [str(p) for p in sorted(shot_dir.glob("*.png")) if p.stem in names]
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), *shots,
                        "--out", str(a.qa / "sheet.png")])
    print(f"{len(res) - bad}/{len(res)} scenes arrived")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
