"""Decode the field's scene-switch function 0x0804908C (switch on r0, 69 cases, jump table 0x080490A4).

usage: python -X utf8 tools/re_scene_cases.py ROM

For each case prints the constant stores the case makes before branching to the shared tail: main mode
(0x0300177C), submode (0x03001D6C), step (0x03001364) and any byte at 0x030048B0+off.
"""
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm import ARM_OP_IMM, ARM_OP_MEM, ARM_OP_REG, ARM_REG_PC

NAMES = {0x0300177C: "mode", 0x03001D6C: "sub", 0x03001364: "step"}


def main():
    d = open(sys.argv[1], "rb").read()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    table = 0x0490A4
    for case in range(69):
        tgt = struct.unpack_from("<I", d, table + 4 * case)[0]
        off = tgt - 0x08000000
        regs, out = {}, []
        for i in md.disasm(d[off:off + 80], tgt):
            ops = i.operands
            if i.mnemonic == "ldr" and len(ops) == 2 and ops[1].type == ARM_OP_MEM and ops[1].mem.base == ARM_REG_PC:
                lit = ((i.address + 4) & ~3) + ops[1].mem.disp
                regs[ops[0].reg] = struct.unpack_from("<I", d, lit - 0x08000000)[0]
            elif i.mnemonic in ("movs", "mov") and len(ops) == 2 and ops[1].type == ARM_OP_IMM:
                regs[ops[0].reg] = ops[1].imm
            elif i.mnemonic in ("adds", "add") and len(ops) == 3 and ops[2].type == ARM_OP_REG:
                a, b = regs.get(ops[1].reg), regs.get(ops[2].reg)
                regs[ops[0].reg] = a + b if a is not None and b is not None else None
            elif i.mnemonic in ("adds",) and len(ops) == 3 and ops[2].type == ARM_OP_IMM:
                a = regs.get(ops[1].reg)
                regs[ops[0].reg] = a + ops[2].imm if a is not None else None
            elif i.mnemonic.startswith("str") and ops[1].type == ARM_OP_MEM:
                base = regs.get(ops[1].mem.base)
                val = regs.get(ops[0].reg)
                if base is not None:
                    a = base + ops[1].mem.disp
                    name = NAMES.get(a, f"{a:08X}")
                    out.append(f"{name}={val if val is not None else '?'}")
            elif i.mnemonic.startswith("b") or i.mnemonic in ("pop", "bx"):
                if i.mnemonic == "bl":
                    out.append(f"call {i.op_str}")
                    continue
                break
        print(f"case {case:2d} {tgt:08X}  " + " ".join(out))


if __name__ == "__main__":
    main()
