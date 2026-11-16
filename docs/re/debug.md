# Debug tool: RAM map, scene switches, warps (phase 2)

All addresses **verified** on the original ROM with Mesen probes unless marked guess.

## Globals
| Address | Size | Meaning (evidence) |
|---|---|---|
| 0x0300177C | u32 | **main mode**: index into handler table 0x0845C06C (main loop 0x0800043A). 0 = robattle, 1 = field, 2 = menus / new-game menu / name entry, 3 = ?, 4 = logos / title, 5, 6 = ? (see §Modes) |
| 0x03001D6C | u32 | submode for the mode handler |
| 0x03001364 | u32 | step inside the submode |
| 0x030048B0 | struct | field state base. +0x516 (0x03004DC6) u8 current map id; vars start at +0 (nibbles, see below) |
| 0x030043E1 | u8 | field substate: 1 = map entry, 2 = idle (player control), 3 = walking/fade, 4 = run door warp |
| 0x0300521A/C | u16 | player x / y in pixels (0x03005218 / 0x0300521C as 16.16 fixed point); +0x96A/+0x96C of the base |
| 0x0300521E/F | u8 | player tile x / y (+0x96E/+0x96F) |
| 0x030048A8 | u32 | pointer to the nibble variable array (= 0x030048B0); read by 0x08058260 (var n: byte n>>1, odd n low 3 bits, even n bits 4-6) |

## Modes (shots from `tools/debug/explore_modes.py`: write mode/sub/step from the idle field)
| Mode | Handler | Subs seen (sub: screen) |
|---|---|---|
| 0 | 0x0800259D | 1 field Start menu, 2 Medawatch, 3 Medabot setup, 4 medals, 5 parts, 6 robattle (0x030051F5 = 1 story / 0 random); 7+ back to field |
| 1 | 0x08048DC1 | field (sub 1) |
| 2 | 0x08060111 | 3 new game/continue, 4 items, 5 save, 6/18 name entry (0x0300066C = whose name), 7 test mode (BGM/SE), 8 game over, 9 save corrupt, 10/23 town map, 11 parts shop, 16 parts trade, 25 shop buy list, 31 options; 12, 24 garbage; 0-2, 13-15, 19, 22, 26, 27, 29 nothing |
| 3 | 0x0806BBAD | 0-2 logo (reset), 3 medal-finding cutscene, 4 Medaroad Race, 5 "select corps" board game, 6 Medarot Weekly studio |
| 4 | 0x08076179 | 0 logo, 1 opening, 2 title, 3 baseball, 4 car game, 5 encyclopedia, 6 staff credits |
| 5, 6 | 0x08080139, 0x08000259 | nothing visible from the field |

Field idle (safe to warp) = mode 1, field substate 2 and 0x03004268 = 1 (set by the field input routine
0x08056C38; 0 during events and dialogue). The intro hands over control briefly at ~f2300 of a cold boot.

## Random encounters
0x08044F8C (called from 0x08056C52): returns 1 for a robattle when +0x945 = 0, +0x977 = 0, **+0x941 != 0**
(encounters on), +0x944 bit 0 = 0, and the step counter +0x943 passes 0x10 and a random roll. Pin 0x030051F1
(+0x941) to 0 for no encounters. Then the field calls scene switch case 0x21 (mode 0 sub 6).

## Door warps
- Table 0x084B6248: one u32 pointer per map id to 8-byte entries, 0xFF-terminated:
  `[tile x, tile y, dest map, dir (low 3 bits), ?, ?, dest tile x, dest tile y]`.
- 0x08057E14 (called from the field state machine at 0x08056238 when substate = 4) finds the entry under the player
  and loads the destination (0x08057894 map load, 0x08057D98 facing, 0x08057A38).
- The door graph from home 2F (map 2) reaches 133 maps; map 0 is the town.
- `warp.lua` `MAP=` sets substate 4 and rewrites registers at 0x08057E50/5A (force the match), 0x08057E64 (map),
  0x08057E6E (dir), 0x08057E78/8A (dest tile), so the game's own loader runs.

## Scene switch 0x0804908C (r0 = case, r1 = arg)
Jump table 0x080490A4, 69 cases (`tools/re_scene_cases.py` decodes them). Cases with code:
| Case | Writes |
|---|---|
| 0, 1, 2 | 0x0300066C = 0/1/2, mode 2 sub 0x12 |
| 3 | 0x03001D3C = arg, mode 2 sub 0x0B |
| 4 | mode 2 sub 0x15 |
| 5 | 0x03000670 = 0, mode 2 sub 0x14 |
| 6 | mode 2 sub 0x17 |
| 8 | mode 4 sub 6 |
| 16, 17 | mode 4 sub 3 / sub 4 |
| 18, 19 | mode 3 sub 3 / ? |
| 32, 33 | 0x030051F5 = 1/0, mode 0 sub 6 step 0 (robattle; 33 is the field's button path at 0x08056C64) |
| 64 | mode 0 sub 1 step 0x10 |
| 65, 66, 67 | mode 1 sub 1 step 0x18 / 0x1C / 0x28 |
| 68 | mode 4 sub 17 step 0 |
Callers: 0x080545DE, 0x08055B50 (event command 0x20), 0x08056C64, 0x0805C2BE, 0x0805C306, 0x0805C770, 0x0805C790.
Every constant store to the mode variable: `python -X utf8 tools/re_stores.py ROM 0300177C`.
