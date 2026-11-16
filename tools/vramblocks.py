"""vramblocks.py: which decompressed blocks (tools/unpack_blocks.py output) sit whole in a VRAM dump, and where.

    python -X utf8 tools/vramblocks.py DUMP.vram.bin [--blocks work/blocks] [--min 64]

Prints VRAM address, block file, size and tile count, sorted by address. A label redraw candidate is a block that
lands under the Japanese on screen (BG char base + tile*32, or 0x10000 + tile*32 for sprites); confirm with
tools/gfx.py preview. Blocks smaller than --min bytes or all-zero are skipped (they match everywhere).
"""
import argparse
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("vram")
    ap.add_argument("--blocks", default="work/blocks")
    ap.add_argument("--min", type=int, default=64)
    a = ap.parse_args(argv)
    v = Path(a.vram).read_bytes()
    hits = []
    for p in sorted(Path(a.blocks).glob("*.bin")):
        b = p.read_bytes()
        if len(b) < a.min or not any(b):
            continue
        i = v.find(b)
        while i >= 0:
            hits.append((i, p.stem, len(b)))
            i = v.find(b, i + 1)
    for i, name, n in sorted(hits):
        print(f"{i:05X}-{i + n - 1:05X}  {name:12} {n:6X} bytes  {n // 32} tiles")


if __name__ == "__main__":
    main()
