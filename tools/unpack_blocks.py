"""Decompress every LZ77 (0x10) and "Le" block the ROM points at into OUTDIR, for vramfind.py.

    python -X utf8 tools/unpack_blocks.py work/blocks
    python -X utf8 $SKILL/scripts/vramfind.py DUMP.vram.bin work/blocks --tile 32

Files are named <codec>_<rom offset hex>.bin, so a vramfind hit names the block to patch.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import le  # noqa: E402
import lz77  # noqa: E402

ROM = Path(__file__).resolve().parent.parent / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    data = ROM.read_bytes()
    n = 0
    for name, mod in (("lz", lz77), ("le", le)):
        for off in mod.scan(data):
            raw, _ = mod.decompress(data, off)
            (out / f"{name}_{off:06X}.bin").write_bytes(raw)
            n += 1
    print(f"{n} blocks -> {out}")


if __name__ == "__main__":
    main()
