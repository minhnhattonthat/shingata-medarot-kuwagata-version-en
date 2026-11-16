"""romcheck.py: phase 7 ROM-level checks on a built ROM and its write log.

    python -X utf8 tools/romcheck.py [build/medarot_kuwagata_en.gba]

1. romdiff.check with the write log and no free ranges: every changed byte has a logged write, each write's
   original bytes are what the clean ROM holds, nothing overwrote or overlapped a write.
2. Every write lies inside data/allowed_ranges.txt, or is a 4-byte pointer word (old and new 0x08xxxxxx) at one
   of the known slots (pointer_slots: font and names-charset literals, script string slots).
3. Every pointer slot of a string with English points at that string's encoded bytes (no table skipped).
Exit 0 when all hold. tests/test_build.py runs the same checks on a fresh in-memory build.
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
import romdiff  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"


def allowed_ranges():
    out = []
    for line in (ROOT / "data/allowed_ranges.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            lo, hi = line.split()[0].split("-")
            out.append((int(lo, 16), int(hi, 16)))
    return out


def pointer_slots(orig):
    """The only pointer words the build may rewrite outside the ranges: the font's 9 literals, the names charset's
    literals, every string slot of script/ (the code literals among them), and the literals of every graphics block
    gfx/labels.json redraws."""
    import gfx
    slots = set(font.FONT_REFS) | set(font.names_refs(orig))
    for label in gfx.load_spec()["labels"]:
        slots.update(gfx.refs(orig, int(label["off"], 16)))
    for path in (ROOT / "script").glob("*.json"):
        for e in json.loads(path.read_text(encoding="utf-8"))["strings"]:
            slots.update(int(s, 16) for s in e["slots"])
    return slots


def problems(orig, data, writes):
    """writes: [(offset, orig bytes, new bytes, writer)]. Returns a list of error lines."""
    errs, _ = romdiff.check(orig, data, set(), writes)
    ranges = allowed_ranges()
    slots = None
    for off, old, new, by in writes:
        end = off + len(new) - 1
        if any(lo <= off and end <= hi for lo, hi in ranges):
            continue
        if slots is None:
            slots = pointer_slots(orig)
        is_ptr = len(new) == 4 and off in slots and old[3] == 0x08 and new[3] == 0x08
        if not is_ptr:
            errs.append(f"0x{off:06X}: {by} writes {len(new)} bytes outside the allowed ranges")
    return errs


def slot_problems(data, report_strings):
    """report_strings: {slot: encoded bytes} for every slot whose string has English."""
    errs = []
    for slot, want in report_strings.items():
        p = struct.unpack_from("<I", data, slot)[0] - 0x08000000
        if data[p:p + len(want)] != want:
            errs.append(f"slot 0x{slot:06X} does not reach its English string")
    return errs


def main(argv):
    built = Path(argv[0]) if argv else ROOT / "build/medarot_kuwagata_en.gba"
    writes = romdiff.load_writes(str(built.with_suffix(".writes.txt")))
    errs = problems(ROM.read_bytes(), built.read_bytes(), writes)
    for e in errs[:50]:
        print(e)
    print(f"{built.name}: {len(writes)} writes, {len(errs)} problems")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
