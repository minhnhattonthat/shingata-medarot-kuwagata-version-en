"""Advance the story one step: from a state, play a route, then mash A until the player has control again.

usage: python -X utf8 tools/debug/story.py FROM.mss TO_NAME ["48 down;80 right"] [--frames 6000] [--btn a]
Writes work/play/s/TO_NAME.mss and work/play/s/TO_NAME.png (the idle shot) and prints the IDLE / mode log lines.
Route syntax is emu.py's --route-str ("N button;N -"). Used to walk the opening story to the first Medabot
(docs/re/debug.md §Story); helper lua: tools/lua/mash_idle.lua.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("src")
    p.add_argument("name")
    p.add_argument("route", nargs="?", default="")
    p.add_argument("--frames", type=int, default=6000)
    p.add_argument("--btn", default="a")
    p.add_argument("--var", action="append", default=[])
    p.add_argument("--warp", action="store_true", help="also run tools/debug/warp.lua (pass MAP=.. etc. by --var)")
    a = p.parse_args()
    outdir = ROOT / "work" / "play" / "s"
    outdir.mkdir(parents=True, exist_ok=True)
    src = Path(a.src)
    if not src.exists():
        src = outdir / (a.src + ".mss")
    run = ROOT / "work" / "play" / "_run"
    state = (outdir / f"{a.name}.mss").as_posix()
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(ROM), "--out", str(run),
           "--state-in", str(src), "--frames", str(a.frames), "--script",
           str(ROOT / "tools" / "lua" / "mash_idle.lua"), "--var", f"SAVE='{state}'", "--var", f"MASH_BTN='{a.btn}'"]
    if a.warp:  # tools/debug/warp.lua first (MAP=/SCENE= vars), mashing starts at MASH_FROM
        cmd += ["--script", str(ROOT / "tools" / "debug" / "warp.lua")]
    for v in a.var:
        cmd += ["--var", v]
    if a.route:
        cmd += ["--var", f"STEPS='{a.route}'"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    log = (run / "log.txt").read_text(encoding="utf-8", errors="replace") if (run / "log.txt").exists() else ""
    from tbl import Table
    tbl = Table.load(ROOT / "tbl" / "jp.tbl")
    rom = ROM.read_bytes()
    for line in log.splitlines():
        if line.startswith("TXT"):
            off = int(line.split()[2], 16) - 0x08000000
            try:
                text = tbl.decode(rom, off)[0]
            except Exception as e:  # noqa: BLE001 - a bad pointer is still worth a line
                text = f"? {e}"
            print(line.split()[1], text[:160])
        elif line.startswith(("mode", "IDLE", "final", "lua", "Lua", "error")):
            print(line)
    shot = run / "idle.png"
    if not shot.exists():
        shot = run / "final.png"
    if shot.exists():
        shutil.copy(shot, outdir / f"{a.name}.png")
        print(outdir / f"{a.name}.png")
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
