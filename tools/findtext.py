"""findtext.py: find words in the original ROM, encoded with the game's table and as Shift-JIS.

    python -X utf8 tools/findtext.py ならびかえ しょうさい ...

Text the extractor missed shows as a table hit outside script/ tables; no hit at all usually means graphics.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rombuild  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"


def hits(data, needle, limit=6):
    out, i = [], data.find(needle)
    while i >= 0 and len(out) < limit:
        out.append(i)
        i = data.find(needle, i + 1)
    return out


def main(words):
    table = rombuild.en_table()
    rom = ROM.read_bytes()
    for w in words:
        b = table.encode(w)
        sj = hits(rom, w.encode("shift_jis"))
        print(w, b.hex(), [hex(h) for h in hits(rom, b)], "sjis", [hex(h) for h in sj] or "-")


if __name__ == "__main__":
    main(sys.argv[1:])
