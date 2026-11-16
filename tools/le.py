"""le.py: the game's own "Le" compression (decoder at ROM 0x08000A2C; VRAM variant 0x08000B34).

Format (from the THUMB code, docs/re/rom.md):
  "Le" + 24-bit LE decompressed size + 1 unused byte; data from +6.
  Each flag byte holds four 2-bit commands, low bits first:
    0: u16 LE w  -> copy (w >> 12) + 3 bytes from dst - ((w & 0xFFF) + 5)
    1: u8 b      -> copy (b >> 2) + 2 bytes from dst - ((b & 3) + 1)
    2: 1 literal byte
    3: 3 literal bytes
  Decoding stops when the output size is reached (checked after each flag group's command).

    python -X utf8 tools/le.py scan ROM          # pointed-to Le blocks: offset, packed size, unpacked size
    python -X utf8 tools/le.py dump ROM OFF OUT  # decompress one block
"""
import struct
import sys


def decompress(data, off=0, limit=1 << 20):
    """Return (bytes, end_offset). Raises ValueError on a malformed block."""
    if data[off:off + 2] != b"Le":
        raise ValueError("not an Le block")
    size = data[off + 2] | data[off + 3] << 8 | data[off + 4] << 16
    if size == 0 or size > limit:
        raise ValueError("bad size")
    out = bytearray()
    p = off + 6
    try:
        while len(out) < size:
            flags = data[p]
            p += 1
            for _ in range(4):
                if len(out) >= size:
                    break
                cmd = flags & 3
                flags >>= 2
                if cmd == 0:
                    w = data[p] | data[p + 1] << 8
                    p += 2
                    disp, n = (w & 0xFFF) + 5, (w >> 12) + 3
                elif cmd == 1:
                    b = data[p]
                    p += 1
                    disp, n = (b & 3) + 1, (b >> 2) + 2
                elif cmd == 2:
                    out.append(data[p])
                    p += 1
                    continue
                else:
                    out += data[p:p + 3]
                    p += 3
                    continue
                if disp > len(out):
                    raise ValueError("back-reference before start")
                for _ in range(n):
                    out.append(out[-disp])
    except IndexError:
        raise ValueError("ran off the end") from None
    if len(out) != size:
        raise ValueError(f"size mismatch {len(out)} != {size}")
    return bytes(out), p


def compress(raw):
    """Greedy encoder; decompress(compress(x)) == x. Not byte-identical to the game's own packer."""
    n = len(raw)
    cmds = []  # (cmd, payload bytes)
    i = 0
    lits = bytearray()

    def flush_lits():
        while len(lits) >= 3:
            cmds.append((3, bytes(lits[:3])))
            del lits[:3]
        for b in lits:
            cmds.append((2, bytes([b])))
        lits.clear()

    while i < n:
        best_n, best_d = 0, 0
        # short form: disp 1-4, len 2-65
        for disp in range(1, 5):
            if disp > i:
                break
            k = 0
            while k < 65 and i + k < n and raw[i + k] == raw[i + k - disp]:
                k += 1
            if k > best_n:
                best_n, best_d = k, disp
        short_n, short_d = best_n, best_d
        # long form: disp 5-4100, len 3-18
        long_n, long_d = 0, 0
        lo = max(0, i - 4100)
        for j in range(i - 5, lo - 1, -1):
            if raw[j] != raw[i]:
                continue
            k = 0
            while k < 18 and i + k < n and raw[j + k] == raw[i + k]:
                k += 1
            if k > long_n:
                long_n, long_d = k, i - j
                if k == 18:
                    break
        if short_n >= 2 and short_n >= long_n:
            flush_lits()
            cmds.append((1, bytes([(short_n - 2) << 2 | (short_d - 1)])))
            i += short_n
        elif long_n >= 3:
            flush_lits()
            w = (long_n - 3) << 12 | (long_d - 5)
            cmds.append((0, bytes([w & 0xFF, w >> 8])))
            i += long_n
        else:
            lits.append(raw[i])
            i += 1
    flush_lits()
    out = bytearray(b"Le" + bytes([n & 0xFF, n >> 8 & 0xFF, n >> 16 & 0xFF, 0]))
    for g in range(0, len(cmds), 4):
        group = cmds[g:g + 4]
        flags = 0
        for k, (c, _) in enumerate(group):
            flags |= c << (2 * k)
        out.append(flags)
        for _, payload in group:
            out += payload
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def scan(data):
    """Blocks reached by an aligned ROM pointer that decompress cleanly: {off: (packed, size, ref)}."""
    found = {}
    for p in range(0, len(data) - 3, 4):
        v = struct.unpack_from("<I", data, p)[0]
        if not 0x08000000 <= v < 0x08000000 + len(data) - 6:
            continue
        off = v - 0x08000000
        if off in found or data[off:off + 2] != b"Le":
            continue
        try:
            raw, end = decompress(data, off)
        except ValueError:
            continue
        found[off] = (end - off, len(raw), p)
    return dict(sorted(found.items()))


if __name__ == "__main__":
    cmd = sys.argv[1]
    rom = open(sys.argv[2], "rb").read()
    if cmd == "scan":
        for off, (packed, size, ref) in scan(rom).items():
            print(f"{off:07X} packed={packed:6d} size={size:6d} ref={ref:07X}")
    elif cmd == "dump":
        raw, _ = decompress(rom, int(sys.argv[3], 16))
        open(sys.argv[4], "wb").write(raw)
