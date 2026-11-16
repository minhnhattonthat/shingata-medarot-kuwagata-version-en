# ROM header, map, compression, free space

## Header (verified: read from the dump)
- Title `SHINMEDA-KWG`, code `BKUJ`, maker `9C` (Imagineer), 8 MiB (0x800000). Developer: Rocket Company, 2004-12-16.
- Save type: EEPROM (`EEPROM_V124` at 0x45BD10). Expanding the ROM to 16 MiB is safe for EEPROM and stays in BPS/IPS
  range; 32 MiB would change the EEPROM addressing, so **do not go past 16 MiB**.

## Map (from read logs and scans; guess unless noted)
| Range | Contents |
|---|---|
| 0x000000-0x0C4FFF | code (THUMB/ARM), tables |
| 0x0F4000-0x430000 | sound samples (read by the IWRAM mixer at 0x030001E8-0x030003FC; **verified** by read log) |
| 0x44B8D0-0x45B05F | music sequence data (read by 0x0808063A-0x08081732) |
| 0x45BD10 | EEPROM library |
| 0x464000-0x511000 | **script and menu text** (docs/re/text.md) |
| 0x510FA4-0x60FFFF, 0x720000-0x7CFFFF | "Le" compressed graphics/tilemaps (1564 pointed-to blocks) |
| 0x600000-0x7FFFFF | BIOS LZ77 (type 0x10) blocks: 1457 pointed-to blocks (1180 in 0x6xxxxx, 276 in 0x7xxxxx) |

## Compression
- **BIOS LZ77 0x10**: `tools/lz77.py` (decompress, greedy VRAM-safe compress, `scan`). Roundtrip of
  decompress -> compress -> decompress is exact on sampled blocks (**verified** for 0x0ACBD8, 0x60ECC0, 0x60ED58; make
  it a test in phase 3). The BIOS LZ77 routine (PC 0x0B8E/0x0C18) reads 0x511D14-0x551718 during the intro.
- **"Le" format** (game's own; **verified**): `tools/le.py`. Entry 0x080009DC checks `L` `e`, then calls 0x08000A2C
  (byte writes) or 0x08000B34 (destination in VRAM, halfword writes), same format. Header: "Le" + 24-bit LE size +
  1 unused byte; data at +6. Each flag byte = four 2-bit commands, low bits first: 0 = u16 w, copy (w>>12)+3 bytes
  from dst-((w&0xFFF)+5); 1 = u8 b, copy (b>>2)+2 bytes from dst-((b&3)+1); 2 = one literal; 3 = three literals.
  Verified: all 1564 pointed-to Le blocks decode to their header size, 1460 of them end exactly where the next block
  starts (4-byte aligned), and decompress(compress(x)) == x on every 25th block (`tests/test_codecs.py` keeps 3).
  `le.compress` is greedy, not the game's packer: the identity build must keep the original blocks.
  Example: 0x5118CC decompresses to a tilemap (`00 F0 01 F0 02 F0 ...`).

## Free space candidates (unverified)
- 0x7C8504-0x7FFFFF is all 0x00 (~226 KB). A candidate only: trap-fill and tour before use.
- Past 0x800000: everything up to 16 MiB is free once the ROM is expanded. The script (~700 KB Japanese) will be
  relocated there whole; its pointers are plain u32 so repointing is a table rewrite.
