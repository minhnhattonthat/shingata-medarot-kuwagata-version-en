"""lz77.py: GBA BIOS LZ77 (type 0x10) decompress / compress, plus a block scanner.

    python -X utf8 tools/lz77.py scan ROM            # list pointed-to LZ77 blocks (offset, packed, unpacked size)
    python -X utf8 tools/lz77.py dump ROM OFF OUT    # decompress one block to a file
"""
import struct
import sys


def decompress(data, off=0, limit=1 << 22):
    """Return (bytes, end_offset). Raises ValueError on a malformed block."""
    if data[off] != 0x10:
        raise ValueError("not LZ77 0x10")
    size = data[off + 1] | data[off + 2] << 8 | data[off + 3] << 16
    if size == 0 or size > limit:
        raise ValueError("bad size")
    out = bytearray()
    p = off + 4
    n = len(data)
    while len(out) < size:
        if p >= n:
            raise ValueError("ran off the end")
        flags = data[p]
        p += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                if p + 1 >= n:
                    raise ValueError("ran off the end")
                b1, b2 = data[p], data[p + 1]
                p += 2
                length = (b1 >> 4) + 3
                disp = ((b1 & 0xF) << 8 | b2) + 1
                if disp > len(out):
                    raise ValueError("back-reference before start")
                for _ in range(length):
                    out.append(out[-disp])
            else:
                if p >= n:
                    raise ValueError("ran off the end")
                out.append(data[p])
                p += 1
    return bytes(out[:size]), p


def compress(raw):
    """Greedy LZ77 type 0x10 (VRAM-safe: displacement >= 2)."""
    out = bytearray([0x10, len(raw) & 0xFF, len(raw) >> 8 & 0xFF, len(raw) >> 16 & 0xFF])
    i = 0
    n = len(raw)
    while i < n:
        flag_pos = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if i >= n:
                break
            best_len, best_disp = 0, 0
            lo = max(0, i - 0x1000)
            maxlen = min(18, n - i)
            for j in range(i - 2, lo - 1, -1):
                k = 0
                while k < maxlen and raw[j + k] == raw[i + k]:
                    k += 1
                if k > best_len:
                    best_len, best_disp = k, i - j
                    if k == maxlen:
                        break
            if best_len >= 3:
                flags |= 0x80 >> bit
                d = best_disp - 1
                out += bytes([(best_len - 3) << 4 | d >> 8, d & 0xFF])
                i += best_len
            else:
                out.append(raw[i])
                i += 1
        out[flag_pos] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def scan(data):
    """Blocks reached by an aligned ROM pointer whose target decompresses cleanly."""
    seen = {}
    for p in range(0, len(data) - 3, 4):
        v = struct.unpack_from("<I", data, p)[0]
        if not 0x08000000 <= v < 0x08000000 + len(data) - 4:
            continue
        off = v - 0x08000000
        if off in seen or data[off] != 0x10:
            continue
        try:
            raw, end = decompress(data, off)
        except ValueError:
            seen[off] = None
            continue
        seen[off] = (end - off, len(raw), p)
    return {k: v for k, v in sorted(seen.items()) if v}


if __name__ == "__main__":
    cmd = sys.argv[1]
    rom = open(sys.argv[2], "rb").read()
    if cmd == "scan":
        for off, (packed, size, ref) in scan(rom).items():
            print(f"{off:07X} packed={packed:6d} size={size:6d} ref={ref:07X}")
    elif cmd == "dump":
        raw, _ = decompress(rom, int(sys.argv[3], 16))
        open(sys.argv[4], "wb").write(raw)
