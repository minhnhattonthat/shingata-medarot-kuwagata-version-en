"""logo.py: the English title logo (D15): MEDAROT in the original's model-kit lettering, SHIN / GATA in the stamp boxes.

The title loads one shared Le tile block (TILES, all four BGs) and a Le map per BG (30x20 entries after a 16-byte
header); the logo is BG0 (letters, palettes 1-4) over BG1 (sprue frame, plate, stamp boxes, palettes 5-8) in map rows
0-9. Palettes are unchanged: every new pixel is a colour the original palettes already hold.

    python -X utf8 tools/logo.py gen        draw gfx/logo/bg0.png, bg1.png (8-bit, pixel = palette*16 + index;
                                            needs numpy); rerun after changing the design below
    python -X utf8 tools/logo.py preview    work/logo/: original | English, 4x, raw palette colours

Build (rombuild -> stage): the tiles only the logo uses are freed, the PNG cells are cut into tiles (deduplicated)
and written into those slots, the two maps are pointed at them, and the three blocks are recompressed past the free
offset and repointed. Nothing outside map rows 0-9 of BG0/BG1 changes (tests/test_logo.py).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import le  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
OUT = ROOT / "gfx" / "logo"
TILES, MAP0, MAP1 = 0x786FC4, 0x789B28, 0x789C28
OTHER_MAPS = (0x78A244, 0x78B418)  # BG2 (characters), BG3 (swirl): their tiles stay untouched
PALS = 0x78BF70  # the title's 16 BG palettes, raw
HDR, MW, MH = 16, 30, 20
ROWS = 10  # logo = map rows 0-9
W, H = MW * 8, ROWS * 8


def entry(mp, cx, cy):
    return struct.unpack_from("<H", mp, HDR + 2 * (cy * MW + cx))[0]


def tile_px(tiles, t, hf=0, vf=0):
    px = []
    for y in range(8):
        yy = 7 - y if vf else y
        row = []
        for x in range(8):
            xx = 7 - x if hf else x
            row.append((tiles[t * 32 + yy * 4 + xx // 2] >> (4 * (xx & 1))) & 15)
        px.append(row)
    return px


def render(tiles, mp):
    """Map rows 0-9 as [[palette*16 + index]] (index 0 = transparent, kept as 0)."""
    g = [[0] * W for _ in range(H)]
    for cy in range(ROWS):
        for cx in range(MW):
            e = entry(mp, cx, cy)
            px = tile_px(tiles, e & 1023, e >> 10 & 1, e >> 11 & 1)
            for y in range(8):
                for x in range(8):
                    v = px[y][x]
                    g[cy * 8 + y][cx * 8 + x] = (e >> 12) * 16 + v if v else 0
    return g


def originals(rom):
    tiles, _ = le.decompress(rom, TILES)
    m0, _ = le.decompress(rom, MAP0)
    m1, _ = le.decompress(rom, MAP1)
    return bytes(tiles), bytes(m0), bytes(m1)


def palette_rgb(rom):
    return [((v & 31), (v >> 5 & 31), (v >> 10 & 31))
            for v in struct.unpack_from("<256H", rom, PALS)]


# ---------------------------------------------------------------- build stage
def load_layers():
    from PIL import Image
    out = []
    for name in ("bg0", "bg1"):
        im = Image.open(OUT / f"{name}.png")
        if im.mode != "P" or im.size != (W, H):
            raise ValueError(f"gfx/logo/{name}.png: want an 8-bit {W}x{H} image")
        px = im.tobytes()
        out.append([px[y * W:(y + 1) * W] for y in range(H)])
    return out


def make(rom, layers=None):
    """New (tiles, map0, map1) raw blocks with the English logo."""
    tiles, m0, m1 = originals(rom)
    layers = load_layers() if layers is None else layers
    keep = set()  # tiles used outside the logo
    for off in OTHER_MAPS:
        mp, _ = le.decompress(rom, off)
        keep |= {entry(mp, cx, cy) & 1023 for cy in range(MH) for cx in range(MW)}
    keep |= {entry(m1, cx, cy) & 1023 for cy in range(ROWS, MH) for cx in range(MW)}
    keep |= {entry(m0, cx, cy) & 1023 for cy in range(ROWS, MH) for cx in range(MW)}
    keep.add(0)
    logo = {entry(mp, cx, cy) & 1023 for mp in (m0, m1) for cy in range(ROWS) for cx in range(MW)}
    pool = sorted(logo - keep)
    tiles = bytearray(tiles)
    have = {bytes(tiles[t * 32:t * 32 + 32]): t for t in sorted(keep, reverse=True)}
    maps = []
    for mp, g in zip((m0, m1), layers):
        mp = bytearray(mp)
        for cy in range(ROWS):
            for cx in range(MW):
                cell = [g[cy * 8 + y][cx * 8:cx * 8 + 8] for y in range(8)]
                pals = {v >> 4 for row in cell for v in row if v & 15}
                if len(pals) > 1:
                    raise ValueError(f"logo cell {cx},{cy}: more than one palette {sorted(pals)}")
                if any(v and not v & 15 for row in cell for v in row):
                    raise ValueError(f"logo cell {cx},{cy}: a pixel with index 0 but a palette")
                old = entry(mp, cx, cy)
                pal = pals.pop() if pals else old >> 12
                tb = bytearray(32)
                for y in range(8):
                    for x in range(8):
                        tb[y * 4 + x // 2] |= (cell[y][x] & 15) << (4 * (x & 1))
                tb = bytes(tb)
                t = have.get(tb)
                if t is None:
                    if not pool:
                        raise ValueError("logo: no free tile left in the title tile block")
                    t = pool.pop(0)
                    tiles[t * 32:t * 32 + 32] = tb
                    have[tb] = t
                struct.pack_into("<H", mp, HDR + 2 * (cy * MW + cx), pal << 12 | t)
        maps.append(bytes(mp))
    return bytes(tiles), maps[0], maps[1], len(pool)


def refs(data, off):
    want = struct.pack("<I", 0x08000000 + off)
    return [p for p in range(0, min(len(data), 0x800000) - 3, 4) if data[p:p + 4] == want]


def block_offsets():
    return (TILES, MAP0, MAP1)


def stage(rom, free):
    """Write the three blocks past `free`, repoint each (one literal each). Returns the new end."""
    new = make(rom.orig)[:3]
    for off, raw in zip(block_offsets(), new):
        found = refs(rom.orig, off)
        if len(found) != 1:
            raise ValueError(f"logo: {len(found)} pointers to {off:06X}, want 1")
        packed = le.compress(raw)
        free = (free + 3) & ~3
        rom.write(free, packed, f"logo {off:06X}")
        rom.write(found[0], struct.pack("<I", 0x08000000 + free), f"logo ptr {off:06X}")
        free += len(packed)
    return free


# ---------------------------------------------------------------- design (gen; numpy)
CAP, TOP = 33, 24  # cap height, top row of the letters
LETTERS = {  # polygon rings (even-odd), local px; width
    'M': (23, [[(0, 0), (8, 0), (11.5, 8), (15, 0), (23, 0), (23, 33), (16, 33), (16, 15), (13, 22), (10, 22),
                (7, 15), (7, 33), (0, 33)]]),
    'E': (16, [[(0, 0), (16, 0), (16, 7), (7, 7), (7, 13), (15, 13), (15, 20), (7, 20), (7, 26), (16, 26),
                (16, 33), (0, 33)]]),
    'D': (19, [[(0, 0), (13, 0), (19, 6), (19, 27), (13, 33), (0, 33)],
               [(7, 7), (10, 7), (12, 9), (12, 24), (10, 26), (7, 26)]]),
    'A': (20, [[(0, 6), (6, 0), (14, 0), (20, 6), (20, 33), (13, 33), (13, 23), (7, 23), (7, 33), (0, 33)],
               [(7, 9), (9, 7), (11, 7), (13, 9), (13, 16), (7, 16)]]),
    'R': (19, [[(0, 0), (13, 0), (19, 6), (19, 13), (16, 17), (19, 20), (19, 33), (12, 33), (12, 24), (10, 22),
                (7, 22), (7, 33), (0, 33)],
               [(7, 7), (10, 7), (12, 9), (12, 13), (10, 15), (7, 15)]]),
    'T': (20, [[(0, 0), (20, 0), (20, 7), (13.5, 7), (13.5, 33), (6.5, 33), (6.5, 7), (0, 7)]]),
}
# the O is the original ロ with its medal eye, moved by whole tiles so its palettes stay as drawn
RO_X, RO_Y, RO_W, RO_H = 128, 27, 29, 30
LAYOUT = [('M', 52), ('E', 77), ('D', 95), ('A', 116), ('R', 138), ('O', 160), ('T', 191)]
GATE = ['#....#', '#....#', '######']  # the sprue-gate notch at stroke ends
BOTTOM_GATES = {'M': [20], 'A': [17], 'R': [4], 'T': [10]}
HL = [[.85, 1, 1, .85], [.95, 1, 1, .95], [.8, 1, 1, .9], [.75, .95, .95, .85]]  # highlight: blend to white
PANEL = (45, 15, 218, 65)  # white sprue panel x0, y0, x1, y1 inclusive
G8 = {
    'S': ['.######.', '##....##', '##......', '.######.', '......##', '......##', '##....##', '.######.'],
    'H': ['##....##', '##....##', '##....##', '########', '########', '##....##', '##....##', '##....##'],
    'I': ['.######.', '...##...', '...##...', '...##...', '...##...', '...##...', '...##...', '.######.'],
    'N': ['##....##', '###...##', '####..##', '##.##.##', '##..####', '##...###', '##....##', '##....##'],
    'G': ['.######.', '##....##', '##......', '##......', '##..####', '##....##', '##....##', '.######.'],
    'A': ['..####..', '.##..##.', '##....##', '##....##', '########', '##....##', '##....##', '##....##'],
    'T': ['########', '########', '...##...', '...##...', '...##...', '...##...', '...##...', '...##...'],
}
STAMPS = [('SHIN', 21, 17, 8 * 16 + 12), ('GATA', 21, 46, 8 * 16 + 4)]  # text, x, y, box colour (pal*16+idx)


def gen():
    import numpy as np
    rom = ROM.read_bytes()
    PAL = np.array(palette_rgb(rom), float)
    tiles, m0, m1 = originals(rom)
    I0 = np.array(render(tiles, m0)); I1 = np.array(render(tiles, m1))
    A0 = (I0 & 15) > 0
    RGB0 = PAL[I0]; RGB1 = PAL[I1]

    def poly_mask(rings, w, h):
        m = np.zeros((h, w), bool)
        ys, xs = np.mgrid[0:h, 0:w] + 0.5
        for ring in rings:
            inside = np.zeros((h, w), bool)
            for i in range(len(ring)):
                (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % len(ring)]
                if y1 != y2:
                    cond = (ys >= min(y1, y2)) & (ys < max(y1, y2))
                    inside ^= cond & (xs < x1 + (ys - y1) * (x2 - x1) / (y2 - y1))
            m ^= inside
        return m

    def dilate(m, r):
        o = m.copy()
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if abs(dx) + abs(dy) <= r + 1:
                    o |= np.roll(np.roll(m, dy, 0), dx, 1)
        return o

    def erode(m, r):
        return ~dilate(~m, r)

    # base gradient per row: the commonest letter colour on that row of the original
    fill = {}
    for y in range(H):
        cols = [tuple(RGB0[y, x]) for x in range(W) if A0[y, x]]
        if cols:
            fill[y] = np.array(max(set(cols), key=cols.count))
    for y in range(H):
        if y not in fill:
            fill[y] = fill[min(fill, key=lambda k: abs(k - y))]

    # ---- BG0 letters
    M = np.zeros((H, W), bool); new0 = np.zeros((H, W, 3)); a0 = np.zeros((H, W), bool)
    for ch, x0 in LAYOUT:
        if ch == 'O':
            sl = (slice(RO_Y, RO_Y + RO_H), slice(RO_X, RO_X + RO_W))
            dst = (slice(RO_Y, RO_Y + RO_H), slice(x0, x0 + RO_W))
            assert (x0 - RO_X) % 8 == 0
            M[dst] |= A0[sl]; a0[dst] |= A0[sl]
            new0[dst] = np.where(A0[sl][..., None], RGB0[sl], new0[dst])
            continue
        w, rings = LETTERS[ch]
        m = poly_mask(rings, w, CAP)
        M[TOP:TOP + CAP, x0:x0 + w] |= m
        for y in range(CAP):
            for x in range(w):
                if not m[y, x]:
                    continue
                L = x == 0 or not m[y, x - 1]
                R = x == w - 1 or not m[y, x + 1]
                T = y == 0 or not m[y - 1, x]
                B = y == CAP - 1 or not m[y + 1, x]
                B2 = not B and (y + 2 >= CAP or not m[y + 2, x])
                f = (0.8 if L else 1) * (0.62 if R else 1) * (0.8 if T else 1) * (0.62 if B else 0.85 if B2 else 1)
                if (T and L) or (B and R):
                    f = 0.42
                new0[TOP + y, x0 + x] = fill[TOP + y] * f
                a0[TOP + y, x0 + x] = True
        runs, x = [], 0
        while x < w:
            if m[0, x]:
                s = x
                while x + 1 < w and m[0, x + 1]:
                    x += 1
                runs.append((s, x))
            x += 1
        notches = [((sx + ex + 1) // 2, TOP + 2, GATE, TOP + 5) for sx, ex in runs]
        notches += [(cx, TOP + CAP - 7, GATE[::-1], TOP + CAP - 8) for cx in BOTTOM_GATES.get(ch, ())]
        for cx, gy, pat, lit in notches:
            gx0 = x0 + cx - 3
            for r, row in enumerate(pat):
                for c, k in enumerate(row):
                    if k == '#':
                        new0[gy + r, gx0 + c] = fill[gy + r] * 0.45
            for c in range(1, 5):
                new0[lit, gx0 + c] = np.minimum(fill[lit] * 1.12, 31)
        sx = runs[0][0]
        hx, hy = x0 + sx + (1 if sx else 0), TOP + 8
        for r in range(4):
            for c in range(4):
                new0[hy + r, hx + c] = new0[hy + r, hx + c] * (1 - HL[r][c]) + 31 * HL[r][c]

    # ---- BG1: panel, plate, runners, stamp boxes
    def c7(i):
        return PAL[7 * 16 + i]
    bg1 = RGB1.copy()
    px0, py0, px1, py1 = PANEL
    bg1[py0:py1 + 1, px0:px1 + 1] = c7(15)
    plate = dilate(M, 4)
    for k in range(1, 4):
        plate |= np.roll(dilate(M, 4), k, 0)
    plate = erode(dilate(plate, 2), 2)
    clip = np.zeros_like(plate); clip[py0 + 2:py1 - 1, px0 + 1:px1] = True
    plate &= clip
    bg1[plate] = c7(1)
    bg1[erode(plate, 0) & ~erode(plate, 1)] = c7(12)
    bg1[erode(plate, 1) & ~erode(plate, 2)] = c7(5)
    for x, top in ((62, 1), (108, 1), (158, 1), (202, 1), (74, 0), (130, 0), (188, 0)):
        for y in (range(py0, py1 + 1) if top else range(py1, py0 - 1, -1)):
            if plate[y, x + 1]:
                break
            bg1[y, x:x + 3] = [c7(1), c7(14), c7(1)]
    for y, left in ((51, 1), (41, 0)):
        for x in (range(px0, px1 + 1) if left else range(px1, px0 - 1, -1)):
            if plate[y + 1, x]:
                break
            bg1[y:y + 3, x] = [c7(1), c7(13), c7(1)]
    nub, bnub = RGB1[15:19, 72:77].copy(), RGB1[64:66, 140:145].copy()
    for x in (66, 151):
        bg1[15:19, x:x + 5] = nub
    for x in (98, 176):
        bg1[64:66, x:x + 5] = bnub
    for text, bx, by, bg in STAMPS:
        bg1[by - 1:by + 20, bx - 1:bx + 20] = PAL[bg]
        m = np.zeros((19, 19), bool)
        for i, ch in enumerate(text):
            ox, oy = 1 + (i % 2) * 9, 1 + (i // 2) * 9
            for r, row in enumerate(G8[ch]):
                for c, k in enumerate(row):
                    m[oy + r, ox + c] |= k == '#'
        edge = np.zeros_like(m)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                edge |= np.roll(np.roll(m, dy, 0), dx, 1)
        edge &= ~m
        for y in range(19):
            for x in range(19):
                if edge[y, x]:
                    bg1[by + y, bx + x] = PAL[8 * 16 + 1]
                elif m[y, x]:
                    bg1[by + y, bx + x] = PAL[8 * 16 + (11 if y % 9 >= 7 else 14)]

    def quantise(img, alpha, pals):
        out = np.zeros((H, W), int)
        for ty in range(H // 8):
            for tx in range(W // 8):
                sl = (slice(ty * 8, ty * 8 + 8), slice(tx * 8, tx * 8 + 8))
                blk = img[sl].reshape(-1, 3); al = alpha[sl].reshape(-1)
                if not al.any():
                    continue
                best = None
                for p in pals:
                    d = ((blk[:, None, :] - PAL[p * 16 + 1:p * 16 + 16][None]) ** 2).sum(-1)
                    k = d.argmin(1)
                    err = d[np.arange(64), k][al].sum()
                    if best is None or err < best[0]:
                        best = (err, p, k)
                _, p, k = best
                out[sl] = np.where(al, p * 16 + k + 1, 0).reshape(8, 8)
        return out

    q0 = quantise(new0, a0, range(1, 5))
    q1 = quantise(bg1, (I1 & 15) > 0, range(5, 9))
    from PIL import Image
    OUT.mkdir(parents=True, exist_ok=True)
    flat = [int(min(255, c * 255 // 31)) for rgb in palette_rgb(rom) for c in rgb]
    for name, q in (("bg0", q0), ("bg1", q1)):
        im = Image.fromarray(q.astype(np.uint8), "P")
        im.putpalette(flat)
        im.save(OUT / f"{name}.png")
    print("wrote", OUT / "bg0.png", OUT / "bg1.png")


def preview(outdir=ROOT / "work" / "logo"):
    from PIL import Image
    rom = ROM.read_bytes()
    pal = palette_rgb(rom)
    t0, a, b = originals(rom)
    t1, n0, n1, left = make(rom)
    outdir.mkdir(parents=True, exist_ok=True)
    shots = []
    for tiles, m0, m1 in ((t0, a, b), (t1, n0, n1)):
        g0, g1 = render(tiles, m0), render(tiles, m1)
        im = Image.new("RGB", (W, H), "white")
        for y in range(H):
            for x in range(W):
                v = g0[y][x] or g1[y][x]
                if v:
                    im.putpixel((x, y), tuple(c * 255 // 31 for c in pal[v]))
        shots.append(im.resize((W * 4, H * 4), Image.NEAREST))
    sheet = Image.new("RGB", (W * 4, H * 8 + 8), "black")
    sheet.paste(shots[0], (0, 0)); sheet.paste(shots[1], (0, H * 4 + 8))
    sheet.save(outdir / "logo_compare.png")
    print(f"{outdir / 'logo_compare.png'} ({left} freed tiles unused)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "gen":
        gen()
    elif cmd == "preview":
        preview()
    else:
        print(__doc__)
        sys.exit(1)
