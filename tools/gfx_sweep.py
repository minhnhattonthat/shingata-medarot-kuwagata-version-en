"""gfx_sweep.py: static graphics sweep (phase 1). Decompress every pointed-to LZ77 and Le block, render the ones that
look like tiles into numbered grey-scale 4bpp sheets with an offset index, and print every block skipped and why.

    python -X utf8 tools/gfx_sweep.py OUTDIR [--fmt gba4|gba8] [--zoom 2] [--rows 48]

OUTDIR/sheet_NNN.png + OUTDIR/index.tsv (sheet, row, block offset, codec, size, width) + OUTDIR/skipped.tsv.
Each block starts on a new tile row with a red bar at its left edge; index.tsv maps sheet rows back to offsets.
Each block gets the tile width (32, 30, 16, 8, 4, 2) whose rows join best (pick_width); narrow blocks are folded into
side-by-side bands of that width. Review the sheets with tools/sweep_review.py.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import le  # noqa: E402
import lz77  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
COLS = 32


def classify(raw):
    """'tiles' or a skip reason."""
    n = len(raw)
    if n < 64:
        return "tiny (<64 B)"
    if n == 32 or (n == 512 and all(raw[i + 1] < 0x80 for i in range(0, n, 2))):
        return "palette (32 B or 512 B of BGR555)"
    # Sizes that aren't a multiple of 32 (2064 = 16-byte header + tiles, etc.) are rendered truncated.
    # Tilemap: 16-bit entries whose tile numbers are small and palette bits uniform-ish.
    words = [raw[i] | raw[i + 1] << 8 for i in range(0, n, 2)]
    if max(w & 0x3FF for w in words) < 0x200 and sum(1 for w in words if (w >> 10) & 3) < len(words) // 8:
        hi = {w >> 12 for w in words}
        if len(hi) <= 4:
            return "tilemap-like (16-bit entries, small tile ids)"
    return "tiles"


def tile_img(raw, i, fmt):
    img = Image.new("L", (8, 8))
    px = img.load()
    if fmt == "gba4":
        t = raw[i * 32:i * 32 + 32]
        for y in range(8):
            for x in range(8):
                b = t[y * 4 + x // 2]
                v = (b >> 4) if x & 1 else (b & 15)
                px[x, y] = 255 - v * 17
    else:
        t = raw[i * 64:i * 64 + 64]
        for y in range(8):
            for x in range(8):
                px[x, y] = 255 - t[y * 8 + x]
    return img


def tile_px(raw, i, fmt):
    """Rows of palette indices for tile i (8 lists of 8)."""
    if fmt == "gba4":
        t = raw[i * 32:i * 32 + 32]
        return [[(t[y * 4 + x // 2] >> 4) if x & 1 else (t[y * 4 + x // 2] & 15) for x in range(8)] for y in range(8)]
    t = raw[i * 64:i * 64 + 64]
    return [list(t[y * 8:y * 8 + 8]) for y in range(8)]


WIDTHS = (32, 30, 16, 8, 4, 2)


def pick_width(raw, fmt):
    """Tile columns that make the block's rows join best: mean pixel jump from the bottom row of tile i to the top row
    of tile i+w, over tiles that aren't blank. Images stored row-major (30-wide full screens, 4-wide sprites) come out
    whole. Narrow widths compare tiles that sit close in memory and score a little better on any data, so a width must
    beat 32 by a clear margin (25%) to win; otherwise the block stays 32 wide."""
    tsize = 32 if fmt == "gba4" else 64
    n = len(raw) // tsize
    px = [tile_px(raw, i, fmt) for i in range(n)]
    scores = {}
    for w in WIDTHS:
        if n < 2 * w:
            continue
        tot = cnt = 0
        for i in range(n - w):
            a, b = px[i][7], px[i + w][0]
            if not any(a) and not any(b):
                continue
            tot += sum(x != y for x, y in zip(a, b))
            cnt += 8
        if cnt:
            scores[w] = tot / cnt
    base = scores.get(32)
    if base is None or base == 0:
        return 32
    w = min(scores, key=lambda k: (scores[k], -k))
    return w if scores[w] < 0.75 * base else 32


def layout(ntiles, w):
    """(tile index, col, row) placements on the 32-column sheet and the row count. A block narrower than 32 that
    divides it is folded into side-by-side bands of w columns, so a 4-wide sprite strip doesn't fill 8x the rows."""
    rows = (ntiles + w - 1) // w
    bands = 32 // w if 32 % w == 0 else 1
    h = (rows + bands - 1) // bands
    place = []
    for ti in range(ntiles):
        r, c = divmod(ti, w)
        band, y = divmod(r, h)
        place.append((ti, band * w + c, y))
    return place, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--fmt", default="gba4", choices=["gba4", "gba8"])
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--rows", type=int, default=48, help="tile rows per sheet")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    data = ROM.read_bytes()
    blocks = [(o, "lz77") for o in lz77.scan(data)] + [(o, "le") for o in le.scan(data)]
    blocks.sort()
    tsize = 32 if a.fmt == "gba4" else 64
    sheets, cur, rows_used = [], [], 0
    index, skipped = [], []
    for off, codec in blocks:
        raw = (lz77 if codec == "lz77" else le).decompress(data, off)[0]
        why = classify(raw)
        if why != "tiles":
            skipped.append((off, codec, len(raw), why))
            continue
        ntiles = len(raw) // tsize
        w = pick_width(raw, a.fmt)
        place, rows = layout(ntiles, w)
        start = 0
        while start < rows:
            take = min(rows - start, a.rows - rows_used)
            if take == 0:
                sheets.append(cur)
                cur, rows_used = [], 0
                continue
            cur.append((raw, [p for p in place if start <= p[2] < start + take], start, take, rows_used))
            index.append((len(sheets), rows_used, off, codec, len(raw), start, w))
            rows_used += take
            start += take
    if cur:
        sheets.append(cur)
    z = a.zoom
    for si, parts in enumerate(sheets):
        img = Image.new("RGB", (COLS * 8 * z + 6, a.rows * 8 * z), (40, 0, 60))
        dr = ImageDraw.Draw(img)
        for raw, place, start, take, row0 in parts:
            for ti, c, y in place:
                t = tile_img(raw, ti, a.fmt).resize((8 * z, 8 * z), Image.NEAREST).convert("RGB")
                img.paste(t, (6 + c * 8 * z, (row0 + y - start) * 8 * z))
            if start == 0:
                dr.rectangle([0, row0 * 8 * z, 3, (row0 + take) * 8 * z - 1], fill=(255, 0, 0))
        img.save(out / f"sheet_{si:03d}.png")
    with open(out / "index.tsv", "w", encoding="utf-8") as f:
        f.write("sheet\trow\toffset\tcodec\tsize\tfirst_block_row\twidth\n")
        for s, r, o, c, n, st, w in index:
            f.write(f"{s:03d}\t{r}\t{o:07X}\t{c}\t{n}\t{st}\t{w}\n")
    with open(out / "skipped.tsv", "w", encoding="utf-8") as f:
        f.write("offset\tcodec\tsize\treason\n")
        for o, c, n, why in skipped:
            f.write(f"{o:07X}\t{c}\t{n}\t{why}\n")
    print(f"{len(blocks)} blocks, {len(blocks) - len(skipped)} rendered on {len(sheets)} sheets, {len(skipped)} skipped "
          f"(see {out / 'skipped.tsv'})")


if __name__ == "__main__":
    main()
