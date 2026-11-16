"""gfx.py: redraw Japanese graphics labels in English (phase 8, references/graphics.md).

A label lives in one compressed 4bpp block (LZ77 or "Le", found with tools/lua/vramwho.lua or declog.lua and
vramfind.py). gfx/labels.json lists, per block: codec, ROM offset, tile columns, the areas to erase (fill with an
index, or copy a column of the strip it sits on), and the English text with a style (font, fill gradient by row,
outline and halo indices). The build (rombuild.build -> gfx_stage) decompresses the original block, erases, draws the
text, recompresses past 8 MiB and repoints every literal-pool word that held the block's address.

    python -X utf8 tools/gfx.py check                         compose every label, report fit and pointer counts
    python -X utf8 tools/gfx.py preview OUTDIR [--only ID,..] original | English, zoomed, per label (palette dumps
                                                              from work/gfx/pal/<scene>.pal.bin when present)
Pixels outside a label's `box` may not change (check and tests/test_gfx.py fail otherwise).
"""
import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import le  # noqa: E402
import lz77  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "gfx" / "labels.json"
FONTS = ROOT / "font"
ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
CODECS = {"le": le, "lz": lz77}


def load_font(name):
    """{char: (advance, rows of '#'/'.')} from font/<name>.txt."""
    out, cur = {}, None
    for line in (FONTS / f"{name}.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("#") and not set(line.strip()) <= set("#."):
            continue
        if not line.strip():
            continue
        if line.startswith("@"):
            parts = line[1:].split()
            ch = " " if parts[0] == "space" else parts[0]
            cur = [int(parts[1]) if len(parts) > 1 else None, []]
            out[ch] = cur
        else:
            cur[1].append(line.strip())
    for ch, g in out.items():
        if g[0] is None:
            g[0] = max((len(r.rstrip(".")) for r in g[1]), default=0) + 1
    return out


def text_mask(text, font, spacing=0):
    """Set of (x, y) ink pixels of `text`, x from 0, y from 0 (the font's top row); `spacing` px added per glyph."""
    ink, x = set(), 0
    for ch in text:
        if ch not in font:
            raise ValueError(f"font has no glyph for {ch!r} (in {text!r})")
        adv, rows = font[ch]
        for y, r in enumerate(rows):
            for dx, c in enumerate(r):
                if c == "#":
                    ink.add((x + dx, y))
        x += adv + spacing
    return ink


def text_width(text, font, spacing=0):
    return max((x for x, _ in text_mask(text, font, spacing)), default=-1) + 1


def dilate(px):
    return {(x + dx, y + dy) for x, y in px for dx in (-1, 0, 1) for dy in (-1, 0, 1)}


def to_grid(raw, cols):
    n = len(raw) // 32
    rows = -(-n // cols)
    g = [[0] * (cols * 8) for _ in range(rows * 8)]
    for t in range(n):
        tx, ty = t % cols, t // cols
        for y in range(8):
            for x in range(8):
                b = raw[t * 32 + y * 4 + x // 2]
                g[ty * 8 + y][tx * 8 + x] = (b >> 4) if x & 1 else (b & 15)
    return g


def from_grid(g, cols, ntiles):
    out = bytearray()
    for t in range(ntiles):
        tx, ty = t % cols, t // cols
        for y in range(8):
            row = g[ty * 8 + y]
            for x in range(0, 8, 2):
                out.append(row[tx * 8 + x] | row[tx * 8 + x + 1] << 4)
    return bytes(out)


def load_spec(path=SPEC):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compose(rom, label, styles):
    """(original raw, new raw) for one label entry."""
    mod = CODECS[label["codec"]]
    off = int(label["off"], 16)
    raw, _ = mod.decompress(rom, off)
    cols = label["cols"]
    g = to_grid(raw, cols)
    h, w = len(g), len(g[0])
    for e in label.get("erase", []):
        x0, y0, ew, eh = e["rect"]
        for y in range(y0, y0 + eh):
            for x in range(x0, x0 + ew):
                g[y][x] = g[y][e["copy_col"]] if "copy_col" in e else e["index"]
    bx, by, bw, bh = label["box"]
    for item in label["text"]:
        st = styles[item.get("style", label.get("style"))]
        font = load_font(st["font"])
        sp = item.get("spacing", st.get("spacing", 0))
        x0 = item["x"]
        if x0 == "center":
            x0 = bx + (bw - text_width(item["s"], font, sp)) // 2
        y0 = item.get("y", st.get("top", 0))
        fill = {(x + x0, y + y0) for x, y in text_mask(item["s"], font, sp)}
        outline = dilate(fill) - fill if "outline" in st else set()
        halo = dilate(fill | outline) - fill - outline if "halo" in st else set()
        for x, y in fill | outline | halo:
            if not (bx <= x < bx + bw and by <= y < by + bh):
                raise ValueError(f"{label['id']}: {item['s']!r} runs out of its box at ({x},{y})")
        for x, y in halo:
            if g[y][x] in st.get("halo_on", [0]):
                g[y][x] = st["halo"]
        for x, y in outline:
            g[y][x] = st["outline"]
        for x, y in fill:
            idx = st["fill"]
            if isinstance(idx, list):  # [[first row offset, index], ..] from the text's top row down
                idx = [i for r, i in idx if y - y0 >= r][-1]
            g[y][x] = idx
    new = bytearray(from_grid(g, cols, len(raw) // 32))
    if label.get("names_tiles"):  # {"tile index": "names-charset code"}: copy that 8x8 English glyph (tools/font.py)
        import font
        tiles = font.names_tiles()
        for t, code in label["names_tiles"].items():
            new[int(t) * 32:int(t) * 32 + 32] = tiles[int(code, 16)]
    return raw, bytes(new) + raw[len(new):]


def outside_box_changes(orig, new, label):
    cols = label["cols"]
    a, b = to_grid(orig, cols), to_grid(new, cols)
    bx, by, bw, bh = label["box"]
    return [(x, y) for y in range(len(a)) for x in range(len(a[0]))
            if a[y][x] != b[y][x] and not (bx <= x < bx + bw and by <= y < by + bh)]


def refs(data, off):
    want = struct.pack("<I", 0x08000000 + off)
    return [p for p in range(0, min(len(data), 0x800000) - 3, 4) if data[p:p + 4] == want]


def gfx_stage(rom, free, spec=None):
    """Write every label of gfx/labels.json past `free` and repoint it. Returns the new end."""
    spec = load_spec() if spec is None else spec
    for label in spec["labels"]:
        _, new = compose(rom.orig, label, spec["styles"])
        mod = CODECS[label["codec"]]
        off = int(label["off"], 16)
        ptrs = refs(rom.orig, off)
        if len(ptrs) != label["ptrs"]:
            raise ValueError(f"{label['id']}: {len(ptrs)} pointers to {off:06X}, spec says {label['ptrs']}")
        packed = mod.compress(new)
        free = (free + 3) & ~3
        rom.write(free, packed, f"gfx {label['id']}")
        for p in ptrs:
            rom.write(p, struct.pack("<I", 0x08000000 + free), f"gfx ptr {label['id']} {p:06X}")
        free += len(packed)
    return free


def check(spec=None, rom=None):
    """List of problems (empty = fine)."""
    spec = load_spec() if spec is None else spec
    rom = ROM.read_bytes() if rom is None else rom
    problems = []
    for label in spec["labels"]:
        try:
            orig, new = compose(rom, label, spec["styles"])
        except ValueError as e:
            problems.append(str(e))
            continue
        bad = outside_box_changes(orig, new, label)
        if bad:
            problems.append(f"{label['id']}: {len(bad)} pixels changed outside the box, first {bad[0]}")
        mod = CODECS[label["codec"]]
        if mod.decompress(mod.compress(new), 0)[0] != new:
            problems.append(f"{label['id']}: compress roundtrip differs")
        n = len(refs(rom, int(label["off"], 16)))
        if n != label["ptrs"]:
            problems.append(f"{label['id']}: {n} pointers, spec says {label['ptrs']}")
    return problems


def preview(outdir, only=None, zoom=4):
    from PIL import Image
    spec, rom = load_spec(), ROM.read_bytes()
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    for label in spec["labels"]:
        if only and label["id"] not in only:
            continue
        orig, new = compose(rom, label, spec["styles"])
        pal = [(i * 17, i * 17, i * 17) for i in range(16)]
        pfile = ROOT / "work" / "gfx" / "pal" / f"{label.get('scene', '')}.pal.bin"
        if pfile.exists():
            pd = pfile.read_bytes()
            base = label.get("pal", 0) * 32
            pal = []
            for i in range(16):
                c = struct.unpack_from("<H", pd, base + 2 * i)[0]
                pal.append(((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8))
        imgs = []
        for raw in (orig, new):
            g = to_grid(raw, label["cols"])
            im = Image.new("RGB", (len(g[0]), len(g)))
            im.putdata([pal[v] for row in g for v in row])
            imgs.append(im.resize((im.width * zoom, im.height * zoom), Image.NEAREST))
        sheet = Image.new("RGB", (imgs[0].width, imgs[0].height * 2 + zoom * 2), (255, 0, 255))
        sheet.paste(imgs[0], (0, 0))
        sheet.paste(imgs[1], (0, imgs[0].height + zoom * 2))
        sheet.save(out / f"{label['id']}.png")
        print(out / f"{label['id']}.png")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    p = sub.add_parser("preview")
    p.add_argument("outdir")
    p.add_argument("--only")
    p.add_argument("--zoom", type=int, default=4)
    a = ap.parse_args(argv)
    if a.cmd == "check":
        probs = check()
        for pr in probs:
            print(pr)
        print(f"{len(load_spec()['labels'])} labels, {len(probs)} problems")
        return 1 if probs else 0
    preview(a.outdir, a.only.split(",") if a.only else None, a.zoom)
    return 0


if __name__ == "__main__":
    sys.exit(main())
