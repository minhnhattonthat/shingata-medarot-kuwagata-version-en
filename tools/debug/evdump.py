"""Dump every field event script (docs/re/debug.md §Events) as one line per command.

usage: python -X utf8 tools/debug/evdump.py [ROM] [--out work/re/events.txt] [--ev 0x1CB]
Event pointer table 0x084FC358 (u32 per event index, 688 events); argument byte counts per command 0x0847B050;
handlers 0x0847B160. A script runs until command 02 (end); it is cut at the next event's start here.
Lines: "EV 01CB @4FB213" then "  +pc cmd args".
"""
import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
EVENTS, ARGC = 0x4FC358, 0x47B050


def events(rom):
    ptrs = []
    i = 0
    while True:
        v = struct.unpack_from("<I", rom, EVENTS + 4 * i)[0]
        if not 0x08000000 <= v < 0x09000000:
            break
        ptrs.append(v - 0x08000000)
        i += 1
    return ptrs


def decode(rom, start, stop):
    argc = rom[ARGC:ARGC + 256]
    p, out = start, []
    while p < stop:
        c = rom[p]
        n = argc[c] if c < 122 else 0
        out.append((p - start, c, rom[p + 1:p + 1 + n]))
        p += 1 + n
        if c == 0x02:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=DEFAULT_ROM)
    ap.add_argument("--out", default=ROOT / "work" / "re" / "events.txt")
    ap.add_argument("--ev", type=lambda s: int(s, 0))
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    ptrs = events(rom)
    ends = sorted(set(ptrs)) + [len(rom)]
    lines = []
    for i, p in enumerate(ptrs):
        if a.ev is not None and i != a.ev:
            continue
        stop = min(e for e in ends if e > p)
        stop = min(stop, p + 0x400)
        lines.append(f"EV {i:04X} @{p:06X}")
        for pc, c, args in decode(rom, p, stop):
            lines.append(f"  +{pc:03X} {c:02X} {args.hex(' ')}")
    text = "\n".join(lines) + "\n"
    if a.ev is not None:
        print(text, end="")
    else:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"{len(ptrs)} events -> {a.out}")


if __name__ == "__main__":
    main()
