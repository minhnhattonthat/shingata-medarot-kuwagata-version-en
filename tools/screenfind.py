"""screenfind.py: where a scene's on-screen graphics come from (phase 8 label redraws).

    python -X utf8 tools/screenfind.py SCENE [--rom ROM] [--redump] [--frames 30]

Dumps VRAM/palette/OAM/IO from work/states/SCENE.mss on the original ROM (once, into work/gfx/s_<SCENE>/, with
$SKILL/scripts/lua/probes/ppudump.lua), then prints for each enabled text BG: char base, screen base, scroll, the
decompressed blocks (work/blocks, tools/unpack_blocks.py) sitting whole in its tile area with their tile0, and the
blocks that hold its map (rows matched, byte offset of map row 0 = the "+NN" of a gfx/labels.json "map" source).
Also lists the visible sprites (tile, palette, blocks under them). Renders work/gfx/s_<SCENE>/bg<N>.png (map
coordinates, zoom 2, 8-px grid) and copies the palette to work/gfx/pal/<SCENE>.pal.bin for `gfx.py preview`.
"""
import argparse
import glob
import struct
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"


def warp(scene, rom, state):
    """Cold boot `rom`, warp to `scene` and save a state at arrival (the English build's own VRAM)."""
    out = state.parent / f"warp_{scene}"
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           "--frames", "15000", "--timeout", "600", "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--var", f"SCENE='{scene}'", "--var", "STOP=1", "--var", f"SAVE='{state.as_posix()}'"]
    subprocess.run(cmd, check=True)
    if not state.exists():
        sys.exit(f"{scene}: no arrival (see {out / 'log.txt'})")


def dump(scene, rom, out, frames, state):
    out.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           "--state-in", str(state), "--frames", str(frames),
           "--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "ppudump.lua")]
    subprocess.run(cmd, check=True)


def rgb(pal, i):
    c = struct.unpack_from("<H", pal, 2 * i)[0]
    return ((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8)


def blocks():
    out = []
    for p in sorted((ROOT / "work" / "blocks").glob("*.bin")):
        b = p.read_bytes()
        if len(b) >= 64 and any(b):
            out.append((p.stem, b))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene")
    ap.add_argument("--rom", default=str(ROM))
    ap.add_argument("--redump", action="store_true")
    ap.add_argument("--frames", type=int, default=30)
    ap.add_argument("--grid", nargs=5, type=int, metavar=("BG", "X", "Y", "W", "H"),
                    help="print that map rectangle's colour indices (hex, map pixel coordinates) and stop")
    ap.add_argument("--warp", action="store_true",
                    help="cold-boot --rom (e.g. the English build) and warp instead of the original's state; "
                         "output in work/gfx/w_<SCENE>/")
    a = ap.parse_args(argv)
    out = ROOT / "work" / "gfx" / f"{'w' if a.warp else 's'}_{a.scene}"
    if a.redump or not glob.glob(str(out / "ppu_*.vram.bin")):
        state = ROOT / "work" / "states" / f"{a.scene}.mss"
        if a.warp:
            state = out / "arrived.mss"
            out.mkdir(parents=True, exist_ok=True)
            state.unlink(missing_ok=True)
            warp(a.scene, a.rom, state)
        dump(a.scene, a.rom, out, a.frames, state)
    pre = sorted(glob.glob(str(out / "ppu_*.vram.bin")))[-1][:-len(".vram.bin")]
    vram = Path(pre + ".vram.bin").read_bytes()
    pal = Path(pre + ".pal.bin").read_bytes()
    oam = Path(pre + ".oam.bin").read_bytes()
    io = Path(pre + ".io.bin").read_bytes()
    (ROOT / "work" / "gfx" / "pal").mkdir(parents=True, exist_ok=True)
    (ROOT / "work" / "gfx" / "pal" / f"{a.scene}.pal.bin").write_bytes(pal)
    if a.grid:
        n, gx, gy, gw, gh = a.grid
        cnt = struct.unpack_from("<H", io, 8 + 2 * n)[0]
        cb, sb = (cnt >> 2 & 3) * 0x4000, (cnt >> 8 & 31) * 0x800
        for y in range(gy, gy + gh):
            s = ""
            for x in range(gx, gx + gw):
                e = struct.unpack_from("<H", vram, sb + 2 * ((y // 8) * 32 + x // 8))[0]
                sy, sx = (7 - y % 8 if e & 0x800 else y % 8), (7 - x % 8 if e & 0x400 else x % 8)
                b = vram[cb + (e & 1023) * 32 + sy * 4 + sx // 2]
                s += "%X" % (b >> 4 if sx & 1 else b & 15)
            print(f"{y:3} {s}")
        return
    blks = blocks()
    dispcnt = struct.unpack_from("<H", io, 0)[0]
    print(f"DISPCNT {dispcnt:04X} mode {dispcnt & 7}")
    for n in range(4):
        if not dispcnt >> (8 + n) & 1:
            continue
        cnt = struct.unpack_from("<H", io, 8 + 2 * n)[0]
        hofs, vofs = struct.unpack_from("<HH", io, 0x10 + 4 * n)
        cb, sb, size, bpp8 = (cnt >> 2 & 3) * 0x4000, (cnt >> 8 & 31) * 0x800, cnt >> 14, cnt >> 7 & 1
        print(f"\nBG{n}: cnt {cnt:04X} prio {cnt & 3} char {cb:05X} screen {sb:05X} size {size} 8bpp {bpp8} "
              f"scroll {hofs & 511},{vofs & 511}")
        mp = vram[sb:sb + 0x800]
        used = sorted({struct.unpack_from('<H', mp, 2 * i)[0] & 1023 for i in range(1024)})
        print(f"  tiles used {len(used)}: {used[0]}..{used[-1]}")
        for name, b in blks:
            i = vram.find(b, cb, min(len(vram), cb + 0x10000))
            if i >= 0 and (i - cb) // 32 <= used[-1]:
                print(f"  tiles {name:12} at {i:05X} tile0 {(i - cb) // 32} ({len(b) // 32} tiles)")
        rows = [r for r in range(32) if len(set(mp[r * 64:r * 64 + 64])) > 4]
        for name, b in blks:
            hits = {}
            for r in rows:
                seg = mp[r * 64:r * 64 + 60]  # 30 entries: maps are 30 (240 px) or 32 entries wide
                j = b.find(seg)
                while j >= 0:
                    for w in (30, 32):
                        hits.setdefault((w, j - r * 2 * w), set()).add(r)
                    j = b.find(seg, j + 2)
            for (w, at), rs in hits.items():
                if at >= 0 and len(rs) >= max(2, len(rows) // 3):
                    print(f"  map   {name:12} +{at:X} ({w} wide): {len(rs)}/{len(rows)} rows match")
        im = Image.new("RGB", (256, 256))
        px = im.load()
        for cy in range(32):
            for cx in range(32):
                e = struct.unpack_from("<H", mp, 2 * (cy * 32 + cx))[0]
                t, pb = e & 1023, e >> 12
                for y in range(8):
                    sy = 7 - y if e & 0x800 else y
                    for x in range(8):
                        sx = 7 - x if e & 0x400 else x
                        if bpp8:
                            v = vram[cb + t * 64 + sy * 8 + sx]
                            px[cx * 8 + x, cy * 8 + y] = rgb(pal, v)
                        else:
                            v = vram[cb + t * 32 + sy * 4 + sx // 2]
                            v = v >> 4 if sx & 1 else v & 15
                            px[cx * 8 + x, cy * 8 + y] = rgb(pal, pb * 16 + v) if v else (40, 0, 40)
        im = im.resize((512, 512), Image.NEAREST)
        d = ImageDraw.Draw(im)
        for k in range(0, 512, 16):
            col = (90, 90, 90) if k % 64 else (200, 200, 0)
            d.line([(k, 0), (k, 511)], fill=col)
            d.line([(0, k), (511, k)], fill=col)
        im.save(out / f"bg{n}.png")
    print("\nsprites (x, y, w x h, tile, pal):")
    sizes = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
             (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}
    spr_tiles = set()
    for k in range(128):
        a0, a1, a2 = struct.unpack_from("<HHH", oam, 8 * k)
        if a0 >> 8 & 3 == 2:
            continue
        y, x = a0 & 255, a1 & 511
        w, h = sizes.get((a0 >> 14, a1 >> 14), (0, 0))
        if y >= 160 and y + h <= 256 or x >= 240 and x + w <= 512:
            continue
        print(f"  #{k}: {x},{y} {w}x{h} tile {a2 & 1023} pal {a2 >> 12}")
        spr_tiles.add(a2 & 1023)
    for name, b in blks:
        i = vram.find(b, 0x10000)
        if i >= 0:
            t0, t1 = (i - 0x10000) // 32, (i - 0x10000 + len(b)) // 32
            if any(t0 <= t < t1 for t in spr_tiles):
                print(f"  obj tiles {name:12} at {i:05X} tile {t0}..{t1 - 1}")


if __name__ == "__main__":
    main()
