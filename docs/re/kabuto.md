# Kabuto Version port

`build.py --version kabuto` builds the Kabuto patch from the same sources as the Kuwagata one.

## The two ROMs

| | Kuwagata | Kabuto |
|---|---|---|
| Header | `SHINMEDA-KWG` `BKUJ` | `SHINMEDA-KBT` `BKVJ` (warp.lua tells them apart by byte 0x0AE) |
| SHA-1 | `rom.sha1` | `rom_kabuto.sha1` |

Both are 8 MiB and hold the same code and data. From 0x0000AA on, almost every block sits a few bytes away (code
-0x4 to -0x48, text region -0x44/-0x40, graphics -0x40 or +0xA84). `tools/romalign.py` aligns the two
(`data/kabuto_map.tsv`: 4009 segments of identical bytes, 93.2% of the ROM). Gaps between two segments with the
same delta are the same layout with a few changed bytes (BL offsets, address literals); gaps between different
deltas are content that differs or moved.

RAM is identical: all 533 distinct IWRAM/EWRAM literals in the code (0x0000-0xC5000) occur in both, with the same
counts, so `docs/re/debug.md` holds for both. The warp hooks on the door-warp routine (0x08057E14) sit 4 bytes earlier
in Kabuto.

## How the build follows

Every hard-coded offset in `tools/` and `gfx/labels.json` is a Kuwagata offset and goes through
`version.at()`: identity for Kuwagata; for Kabuto the segment map, plus `version.OVERRIDES` where the map has no
single answer. Each stage still checks the bytes it expects there (literals hold the mapped base, `movs` slot
immediates, FE terminators), so a wrong mapping stops the build.

| Overrides (Kuwagata -> Kabuto) | Found from |
|---|---|
| 786FC4 -> 78789C, title tile block | literal 077518 (Kabuto 0774FC) |
| 789B28 -> 78A59C, title BG0 map | literal 077524 (Kabuto 077508) |
| 50EB4C -> 50EB0C, 50EC08 -> 50EBC8, minigame glyph lists | literals 077BE4 / 0788DC (Kabuto 077BC4 / 0788BC) |
| 50E8F4 -> 50E8B4, starter-parts tutorial table | Kabuto's table scan |

Checked (scratch analysis, then tests/test_kabuto.py):
- All 53 graphics blocks of `gfx/labels.json` decompress to the same bytes and have the same pointer counts, so
  the labels apply unchanged.
- Title screen: palettes 1-8 (the logo's) are identical, 12-13 (the Medabot's) differ; every cell of BG0/BG1
  rows 0-19 is the same tile pixels with the same palette and flips. Only the tile numbering and the Medabot art
  (BG2, Metabee-style, Kabuto's own) differ. The "Kabuto Version" subtitle is English in the original, so
  `gfx/logo/*.png` (D15) goes on unchanged; `logo.make()` allocates the free tiles of Kabuto's own block, which
  compresses 332 bytes larger than Kuwagata's.
- Minigame font: the glyphs (codes 52-CF) are the same; the copy runs to code FF, and codes D0-EC there are other,
  version-specific data at the end of the ROM (copied as Kabuto has it).

## Script overlay

`tools/kabuto_script.py` writes `script_kabuto/<Kabuto table>.json` (extract.py's format, Kabuto ids and slots).
Of the Kabuto tables' 8029 strings, 7593 are byte-identical to the Kuwagata string at the mapped offset and 425
to one elsewhere (moved by a version-specific string before them; none of the 425 has two Kuwagata copies with
different English). Those get `"src": "<Kuwagata id>"` and take their English from `script/` at build time
(`rombuild.load_script`). The 11 Kabuto-only strings carry their own `en` (`"like"` = the Kuwagata string at their
place):

| Kabuto | Kuwagata | What |
|---|---|---|
| 4FEB94 | 4FEBD8 | Rubberobo grunt: the Kabuto Medal (Kuwagata Medal) |
| 5022AD, 5022C1 | (5022F2, 502307) | "Devil" / "Ninja" Medal sightings, in place of Kuwagata's "Dragon" / "Angel" |
| 505028 | 505070 | M-PK hands over the park Medal: same text, the Medal's face 006500 (006400) |
| 509869, 50C88A, 50CB25 | 5098B1, 50C8D2, 50CB6D | rhino beetle (stag beetle): message, item name, description |
| 50E7B4-50E817 | 50E7FC-50E858 | Weekly Medabot parts tutorial: Missile / Revolver / Submachine Gun / Ochitsukar |

`python -X utf8 tools/kabuto_script.py` reruns it (own `en` kept by id); `tests/test_kabuto.py` fails when
`script_kabuto/` is stale. `tools/lint.py` lints the own strings against their Kuwagata table's window.

## QA

- `tests/test_kabuto.py`: overlay up to date; romcheck (writes logged, in the mapped `data/allowed_ranges.txt`
  or pointer words); every Kabuto slot reaches its English; the font, widths, names charset, graphics labels,
  credit slots and name entry write the same bytes as the Kuwagata build; the logo cells match it pixel for pixel.
- `tools/romcheck.py --version kabuto`, `tools/release.py --game kabuto` (jp_left with
  `docs/jp_left_known.txt` mapped; textcover is carried by the Kuwagata sweep, since the shared strings are byte
  copies).
- Warp tour: `prove.py build/medarot_kabuto_en.gba --no-states --qa work/qa/kabuto/scenes_en` (the Japanese
  Kabuto ROM's in `work/qa/kabuto/scenes_jp`).
