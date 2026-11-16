"""Diff a RAM range between two savestates (default: the saved field block 0x030048B0-0x03005287).

usage: python -X utf8 tools/debug/ramdiff.py A.mss B.mss [--lo 0x030048B0 --hi 0x03005287] [--ignore 0x030051FF,...]
Prints "addr a->b" per changed byte (field-relative offset too). Uses tools/lua/dumpblock.lua.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"


def dump(state, lo, hi, tag):
    out = ROOT / "work" / "probe" / f"dump_{tag}"
    subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(ROM), "--out", str(out),
                    "--state-in", str(state), "--frames", "20", "--script", str(ROOT / "tools" / "lua" / "dumpblock.lua"),
                    "--var", f"DUMP_LO={lo:#x}", "--var", f"DUMP_HI={hi:#x}"], capture_output=True, text=True)
    mem = {}
    for line in (out / "log.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.split()
        if len(p) == 3 and p[0] == "H":
            a = int(p[1], 16)
            for i in range(0, len(p[2]), 2):
                mem[a + i // 2] = int(p[2][i:i + 2], 16)
    return mem


def main():
    p = argparse.ArgumentParser()
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--lo", type=lambda s: int(s, 0), default=0x030048B0)
    p.add_argument("--hi", type=lambda s: int(s, 0), default=0x03005287)
    p.add_argument("--ignore", default="")
    a = p.parse_args()
    ign = {int(x, 16) for x in a.ignore.split(",") if x}
    ma, mb = dump(a.a, a.lo, a.hi, "a"), dump(a.b, a.lo, a.hi, "b")
    for addr in sorted(ma):
        if addr in ign or ma[addr] == mb.get(addr):
            continue
        print(f"{addr:08X} +{addr - 0x030048B0:03X} {ma[addr]:02X}->{mb.get(addr, 0):02X}")


if __name__ == "__main__":
    main()
