"""credits.py: OAM slots for the English staff credits (phase 8, credits role lines cut).

The staff credits (mode 4 sub 6) are a ticker. Page b (0-14) is drawn by the switch at 0x0807FAE0 (jump table
0x0807FB08), which calls 0x08042218(str, slot, x, y, [box w, pal, 1, 0]) once per line. That routine puts one 8x8
sprite per glyph (spaces take none) into the sprite records at 0x03001DE0 (64 bytes each, 128 of them) starting at
record `slot`, set by a `movs r1, #slot` before each call. Every frame 0x0808007C moves all 128 records 1 px left and
frees one once x <= -16; the next page comes timing[b] frames later (u16 table 0x08510DD0: 250 each, page 9 330,
page 11 0, so pages 11 and 12 start together).

The JP gave each line exactly its Japanese glyph count, so a longer English line ran into the next line's records
and was overwritten ("Executive Produc", "Chief Produce", "Character De"; names cut when the next page drew).
A sprite lives at most ~490 frames (names start at x = 37*8 or 49*8), under two page gaps, so two banks are
enough: even pages take records 0-63, odd pages 64-127 (pages 11 and 12 share bank 1, 13 -> 0, 14 -> 1), each
line its English byte count (spaces included: a little spare). The stage fails if a bank overflows; a write past
record 127 would run into RAM after the array (the parts list at 0x03003DF0).
"""
import struct

# (page, string id, address of the `movs r1, #slot` before the call), in drawing order. From the disassembly of
# 0x0807FAE0 (tables 0x08510C28 roles, 0x08510C88 sub-roles, 0x08510CE8 names).
LINES = [
    (0, 0x510AEC, 0x7FB58), (0, 0x510B9C, 0x7FB72),
    (1, 0x510AFB, 0x7FB94), (1, 0x510BA6, 0x7FBAE),
    (2, 0x510B06, 0x7FBD0), (2, 0x510BB0, 0x7FBEA),
    (3, 0x510B11, 0x7FC0C), (3, 0x510B7E, 0x7FC26), (3, 0x510BB9, 0x7FC3E),
    (4, 0x510B19, 0x7FC64), (4, 0x510B7F, 0x7FC7E), (4, 0x510BBD, 0x7FC96),
    (5, 0x510B24, 0x7FCC0), (5, 0x510BC3, 0x7FCDE), (5, 0x510BCD, 0x7FCF6), (5, 0x510BD4, 0x7FD0E),
    (6, 0x510B32, 0x7FD30), (6, 0x510B83, 0x7FD48), (6, 0x510BDB, 0x7FD62),
    (7, 0x510B3F, 0x7FD88), (7, 0x510B84, 0x7FDA0), (7, 0x510BE0, 0x7FDBA),
    (8, 0x510B45, 0x7FDE0), (8, 0x510B85, 0x7FDFA), (8, 0x510BE4, 0x7FE14),
    (9, 0x510B54, 0x7FE36), (9, 0x510B86, 0x7FE4E), (9, 0x510BE8, 0x7FE6C), (9, 0x510BEF, 0x7FE84),
    (9, 0x510BF4, 0x7FE9C), (9, 0x510BFA, 0x7FEB4), (9, 0x510BFE, 0x7FECC), (9, 0x510C01, 0x7FEE4),
    (10, 0x510B60, 0x7FF0C), (10, 0x510B8C, 0x7FF24), (10, 0x510C04, 0x7FF3E),
    (11, 0x510B65, 0x7FF64), (11, 0x510B8D, 0x7FF7C),
    (12, 0x510B66, 0x7FFA8), (12, 0x510C0B, 0x7FFC6), (12, 0x510C10, 0x7FFDE), (12, 0x510C1A, 0x7FFF6),
    (13, 0x510B72, 0x80020), (13, 0x510C1E, 0x80038),
    (14, 0x510B92, 0x80060),
]
# Original slots, checked against the ROM before patching.
ORIG_SLOTS = [0, 16, 27, 40, 51, 63, 74, 86, 97, 108, 0, 11, 22, 36, 47, 58, 69, 85, 91, 102, 110, 117, 0, 16,
              26, 37, 50, 61, 72, 83, 94, 105, 116, 0, 16, 30, 40, 52, 70, 82, 93, 104, 0, 10, 20]
BANK = {11: 1, 12: 1, 13: 0, 14: 1}  # pages 11 and 12 start in the same frame; the rest alternate
BANK_SIZE = 64


def bank_of(page):
    return BANK.get(page, page % 2)


def slots(sizes):
    """sizes: one sprite count per LINES entry. Returns the first record of each line; raises on a bank overflow."""
    out, used, last_page = [], {}, None
    for (page, sid, _), n in zip(LINES, sizes):
        b = bank_of(page)
        if page != last_page:
            used[b] = 0
            last_page = page
        out.append(b * BANK_SIZE + used[b])
        used[b] += max(1, n)
        if used[b] > BANK_SIZE:
            raise ValueError(f"credits: page {page} needs more than {BANK_SIZE} sprites (line {sid:06X})")
    return out


def stage(rom, entries, table, strings=None):
    """Patch the slot immediates for the English text. entries: rombuild.load_script() list; table: en table;
    strings: the build's {offset: encoded bytes} overrides (marker builds)."""
    text = {off: t for off, _, t in entries}
    strings = strings or {}
    sizes = []
    for page, sid, at in LINES:
        if sid in strings:
            sizes.append(len(strings[sid]))
        elif sid in text:
            sizes.append(len(table.encode(text[sid])))  # with the FE terminator: one spare
        else:
            raise ValueError(f"credits: string {sid:06X} not in script/")
    try:
        new_slots = slots(sizes)
    except ValueError as err:
        if not strings:
            raise
        print(f"{err}: marker/stress text, credit slots left as the original")
        return
    for (page, sid, at), old, new in zip(LINES, ORIG_SLOTS, new_slots):
        if rom.orig[at:at + 2] != bytes([old, 0x21]):
            raise ValueError(f"credits: no movs r1, #{old} at {at:06X}")
        rom.write(at, bytes([new]), "credits slot")
