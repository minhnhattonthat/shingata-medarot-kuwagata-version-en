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
            if len(parts[0]) == 2 and len(parts) > 1 and not parts[1].isdigit():
                parts = parts[1:]  # dialogue font (font/en_glyphs.txt): `@XX c [advance]`, XX = the code
            ch = " " if parts[0] == "space" else parts[0]
            cur = [int(parts[1]) if len(parts) > 1 else None, []]
            out[ch] = cur
        else:
            cur[1].append(line.strip())
    for ch, g in out.items():
        if g[0] is None:
            g[0] = max((len(r.rstrip(".")) for r in g[1]), default=0) + 1
    out.setdefault(" ", [3, []])
    return out


def text_mask(text, font, spacing=0, ink_char="#"):
    """Set of (x, y) ink pixels of `text`, x from 0, y from 0 (the font's top row); `spacing` px added per glyph.
    ink_char "+" gives the half-ink pixels of the dialogue font instead."""
    ink, x = set(), 0
    for ch in text:
        if ch not in font:
            raise ValueError(f"font has no glyph for {ch!r} (in {text!r})")
        adv, rows = font[ch]
        for y, r in enumerate(rows):
            for dx, c in enumerate(r):
                if c == ink_char:
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


def paint(g, label, styles):
    """Erase and draw one label's text into the index grid g (absolute pixel coordinates)."""
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
        if "half" in st:  # half-ink pixels ("+" in font/en_glyphs.txt), drawn under the fill
            for x, y in {(x + x0, y + y0) for x, y in text_mask(item["s"], font, sp, "+")}:
                g[y][x] = st["half"]
        for x, y in fill:
            idx = st["fill"]
            if isinstance(idx, list):  # [[first row offset, index], ..] from the text's top row down
                idx = [i for r, i in idx if y - y0 >= r][-1]
            g[y][x] = idx


def compose(rom, label, styles):
    """(original raw, new raw) for a block label (the block is the image, `cols` tiles wide)."""
    mod = CODECS[label["codec"]]
    raw, _ = mod.decompress(rom, int(label["off"], 16))
    cols = label["cols"]
    g = to_grid(raw, cols)
    paint(g, label, styles)
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


def _src(s):
    """"lz:72BF8C+10" -> (codec, block offset, byte offset inside the block)."""
    codec, rest = s.split(":")
    off, _, at = rest.partition("+")
    return codec, int(off, 16), int(at or "0", 16)


def map_width(mp, at):
    """Entries per map row: the block's 16-byte header (u32 width, u32 height, ..) when the map starts after one
    (at >= 16, e.g. 30 for a 240-px map), else 32."""
    if at >= 16:
        w, h = struct.unpack_from("<II", mp, at - 16)
        if 1 <= w <= 32 and 1 <= h <= 32 and at + 2 * w * h <= len(mp):
            return w
    return 32


def render_screen(tiles, mp, at, tile0):
    """256x256 index grid of a text-BG map (entries at mp[at:], map_width() per row, up to 32 rows) over a tile
    block; tile = entry - tile0."""
    g = [[0] * 256 for _ in range(256)]
    w = map_width(mp, at)
    rows = min(32, (len(mp) - at) // (2 * w))
    for cy in range(rows):
        for cx in range(w):
            e = struct.unpack_from("<H", mp, at + 2 * (cy * w + cx))[0]
            t = (e & 1023) - tile0
            if not 0 <= t < len(tiles) // 32:
                continue
            for y in range(8):
                sy = 7 - y if e & 0x800 else y
                for x in range(8):
                    sx = 7 - x if e & 0x400 else x
                    b = tiles[t * 32 + sy * 4 + sx // 2]
                    g[cy * 8 + y][cx * 8 + x] = (b >> 4) if sx & 1 else (b & 15)
    return g


def screen_blocks(rom, spec):
    """Apply every screen label (one with "map"): {block offset: [codec, original raw, new raw]}. Each changed cell
    of a label's box gets a tile of its own appended to the tile block (or an identical existing one) and its map
    entry is pointed at it, palette kept, flips cleared; tiles other screens use are never edited in place."""
    blocks = {}

    def get(src):
        codec, off, at = _src(src)
        if off not in blocks:
            raw, _ = CODECS[codec].decompress(rom, off)
            blocks[off] = [codec, raw, bytearray(raw)]
        return blocks[off][2], at

    for label in spec["labels"]:
        if "map" not in label:
            continue
        tiles, _ = get(label["tiles"])
        mp, at = get(label["map"])
        tile0 = label.get("tile0", 0)
        g = render_screen(tiles, mp, at, tile0)
        paint(g, label, spec["styles"])
        have = {}
        for t in range(len(tiles) // 32 - 1, -1, -1):
            have[bytes(tiles[t * 32:t * 32 + 32])] = t
        bx, by, bw, bh = label["box"]
        if bx % 8 or by % 8 or bw % 8 or bh % 8:
            raise ValueError(f"{label['id']}: a screen label's box must be on the 8-px cell grid")
        for cy in range(by // 8, (by + bh) // 8):
            for cx in range(bx // 8, (bx + bw) // 8):
                cell = [g[cy * 8 + y][cx * 8:cx * 8 + 8] for y in range(8)]
                tb = from_grid(cell, 1, 1)
                p = at + 2 * (cy * map_width(mp, at) + cx)
                e = struct.unpack_from("<H", mp, p)[0]
                t = have.get(tb)
                if t is None:
                    t = len(tiles) // 32
                    tiles += tb
                    have[tb] = t
                if tile0 + t > 1023:
                    raise ValueError(f"{label['id']}: tile block full (tile {tile0 + t})")
                new_e = (e & 0xF000) | (tile0 + t)
                if (e & 0x3FF) - tile0 == t and not e & 0xC00:
                    new_e = e
                struct.pack_into("<H", mp, p, new_e)
    return blocks


def screen_problems(rom, spec, blocks):
    """Pixels changed outside every box drawn on the same map."""
    out = []
    boxes = {}
    for label in spec["labels"]:
        if "map" in label:
            boxes.setdefault((label["tiles"], label["map"], label.get("tile0", 0)), []).append(label)
    for (tsrc, msrc, tile0), labels in boxes.items():
        _, toff, _ = _src(tsrc)
        _, moff, at = _src(msrc)
        a = render_screen(blocks[toff][1], blocks[moff][1], at, tile0)
        b = render_screen(blocks[toff][2], blocks[moff][2], at, tile0)
        rects = [lb["box"] for lb in labels]
        bad = [(x, y) for y in range(256) for x in range(256) if a[y][x] != b[y][x]
               and not any(bx <= x < bx + bw and by <= y < by + bh for bx, by, bw, bh in rects)]
        if bad:
            out.append(f"{labels[0]['id']}..: {len(bad)} pixels changed outside the boxes, first {bad[0]}")
    return out


def refs(data, off):
    want = struct.pack("<I", 0x08000000 + off)
    return [p for p in range(0, min(len(data), 0x800000) - 3, 4) if data[p:p + 4] == want]


def gfx_stage(rom, free, spec=None):
    """Write every label of gfx/labels.json past `free` and repoint it. Returns the new end."""
    spec = load_spec() if spec is None else spec
    out = []  # (name, codec, block offset, new raw, expected pointer count)
    for label in spec["labels"]:
        if "map" in label:
            continue
        _, new = compose(rom.orig, label, spec["styles"])
        out.append((label["id"], label["codec"], int(label["off"], 16), new, label["ptrs"]))
    ptrs = spec.get("screen_ptrs", {})
    for off, (codec, _, new) in screen_blocks(rom.orig, spec).items():
        out.append((f"screen {off:06X}", codec, off, bytes(new), ptrs.get(f"{off:06X}")))
    for name, codec, off, new, want in out:
        found = refs(rom.orig, off)
        if len(found) != want:
            raise ValueError(f"{name}: {len(found)} pointers to {off:06X}, spec says {want}")
        packed = CODECS[codec].compress(new)
        free = (free + 3) & ~3
        rom.write(free, packed, f"gfx {name}")
        for p in found:
            rom.write(p, struct.pack("<I", 0x08000000 + free), f"gfx ptr {name} {p:06X}")
        free += len(packed)
    return free


def block_offsets(spec=None):
    """Every ROM block gfx/labels.json replaces (for romcheck's pointer slots)."""
    spec = load_spec() if spec is None else spec
    offs = set()
    for label in spec["labels"]:
        if "map" in label:
            offs |= {_src(label["tiles"])[1], _src(label["map"])[1]}
        else:
            offs.add(int(label["off"], 16))
    return offs


def check(spec=None, rom=None):
    """List of problems (empty = fine)."""
    spec = load_spec() if spec is None else spec
    rom = ROM.read_bytes() if rom is None else rom
    problems = []
    try:
        blocks = screen_blocks(rom, spec)
        problems += screen_problems(rom, spec, blocks)
        for off, (codec, _, new) in blocks.items():
            mod = CODECS[codec]
            if mod.decompress(mod.compress(bytes(new)), 0)[0] != new:
                problems.append(f"screen {off:06X}: compress roundtrip differs")
            n, want = len(refs(rom, off)), spec.get("screen_ptrs", {}).get(f"{off:06X}")
            if n != want:
                problems.append(f"screen {off:06X}: {n} pointers, screen_ptrs says {want}")
    except ValueError as e:
        problems.append(str(e))
    for label in spec["labels"]:
        if "map" in label:
            continue
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
    blocks = None
    for label in spec["labels"]:
        if only and label["id"] not in only:
            continue
        if "map" in label:
            if blocks is None:
                blocks = screen_blocks(rom, spec)
            _, toff, _ = _src(label["tiles"])
            _, moff, at = _src(label["map"])
            bx, by, bw, bh = label["box"]
            grids = [[row[bx:bx + bw] for row in render_screen(blocks[toff][i], blocks[moff][i], at,
                                                              label.get("tile0", 0))[by:by + bh]] for i in (1, 2)]
        else:
            orig, new = compose(rom, label, spec["styles"])
            grids = [to_grid(orig, label["cols"]), to_grid(new, label["cols"])]
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
        for g in grids:
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
