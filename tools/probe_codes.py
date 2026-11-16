"""probe_codes.py: build test ROMs that show a run of character codes in place of a known dialogue line.

    python -X utf8 tools/probe_codes.py OUTDIR START [COUNT=12] [PER=12]

Writes OUTDIR/codes_<hex>.gba, each with the 12-byte line at 0x50A0D0 (「したにおりていらっしゃい」, shown after the
player name early in the intro) replaced by PER consecutive codes. Recon only (phase 1): reads rom/, writes work/.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
SITE, LEN = 0x50A0D0, 12

if __name__ == "__main__":
    out = Path(sys.argv[1])
    start = int(sys.argv[2], 16)
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    per = int(sys.argv[4]) if len(sys.argv) > 4 else LEN
    out.mkdir(parents=True, exist_ok=True)
    base = ROM.read_bytes()
    for k in range(count):
        c0 = start + k * per
        codes = bytes((c0 + i) & 0xFF for i in range(per))
        rom = bytearray(base)
        rom[SITE:SITE + LEN] = codes[:LEN].ljust(LEN, b"\x00")
        (out / f"codes_{c0:02X}.gba").write_bytes(rom)
        print(f"codes_{c0:02X}.gba", codes.hex(" "))
