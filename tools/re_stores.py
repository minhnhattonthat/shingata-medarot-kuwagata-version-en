"""List constant stores to a RAM global in the Thumb code of a GBA ROM.

usage: python -X utf8 tools/re_stores.py ROM ADDR [--window 12]

Finds each literal-pool word equal to ADDR, each `ldr rX, [pc, #n]` that loads it, then within the next
--window instructions any `str/strb/strh rY, [rX(, #0)]`, and reports the last `movs rY, #imm` before it.
Phase 2 used it to list every main-mode switch (0x0300177C) the game makes.
"""
import argparse
import struct

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("addr", type=lambda s: int(s, 16))
    ap.add_argument("--window", type=int, default=12)
    a = ap.parse_args()
    d = open(a.rom, "rb").read()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    pools = [i for i in range(0, len(d) - 3, 4) if struct.unpack_from("<I", d, i)[0] == a.addr]
    for p in pools:
        # Thumb ldr literal: 01001 rd imm8, target = (pc & ~3) + 4 + imm8*4; scan 1 KB back
        for off in range(max(0, p - 1020), p, 2):
            h = struct.unpack_from("<H", d, off)[0]
            if h >> 11 != 0b01001:
                continue
            if ((off + 4) & ~3) + (h & 0xFF) * 4 != p:
                continue
            rx = (h >> 8) & 7
            ins = list(md.disasm(d[off:off + 2 * a.window + 2], 0x08000000 + off))
            consts = {}
            for i in ins[1:]:
                ops = i.op_str.replace(" ", "")
                if i.mnemonic in ("movs", "mov") and ",#" in ops:
                    r, v = ops.split(",#")
                    consts[r] = int(v, 0)
                if i.mnemonic in ("str", "strb", "strh") and (ops.endswith(f"[r{rx}]") or ops.endswith(f"[r{rx},#0]")):
                    r = ops.split(",")[0]
                    print(f"{i.address:08X} {i.mnemonic} {r}={consts.get(r, '?')}")
                    break
                if i.mnemonic.startswith("b") or i.mnemonic == "pop":
                    break


if __name__ == "__main__":
    main()
