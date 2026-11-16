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

## Save block and inventory hunt (2026-11-17, unfinished)
- **Saved RAM:** the save (mode 2 sub 5, "yes") CpuSets 0x030048B0-0x03005287 (0x9D8 bytes, the field-state block)
  plus 0x03001D80-0x03001DCF and 0x03004260-0x03004267 (BIOS CpuSet pc 0xB8E; `work/qa/rsv3`). EEPROM save
  (`EEPROM_V124`); Mesen Lua write hooks never fire on the DMA3 registers, so `tools/lua/dma_eeprom.lua` logs nothing.
- **Not the inventory (when empty):** the medal list (0/4), Medabot setup (0/3), parts list (0/5) and shop buy list
  (2/25) read no byte of the save block at all (`tools/lua/reads_in_mode.lua --var RLO=0x030048B0 --var RHI=0x03005290`).
  Filling 0x03004A00-A9F, 0x03004AB0-DBF, 0x03004E40-51CF or 0x03000548-650 with 1 before opening them changes
  nothing (`tools/lua/fill.lua`). So either the lists check a count elsewhere first, or the inventory is built
  only when the story gives the first Medabot. Next try: diff RAM across the story event that hands over the first
  Medabot/medal (find it with the event interpreter, below), or the "give part" event command.
- UI objects live at 0x0202E000-0x0202F6FF (0x50/0x210-byte records) and task slots at 0x03000BE0 (0x40 each);
  0x02020000-0x0202007F is a glyph-drawing buffer (0x08041600 ORs it into VRAM 0x06000280). Skip them in traces.
- **Parts shop / money (2026-11-17, session 3):** the shop (mode 2 sub 11) needs a shop id in 0x03001D3C (scene
  switch case 3): id 0 = empty buy list (what `parts_shop_buy` shows), ids 1 and 2 show a clerk and the
  buy/sell/leave menu. Money shows 0円. The shop reads **no byte of the save block either** (`reads_in_mode.lua`
  with RLO/RHI on it), so money and inventory live somewhere else. A full-RAM read trace stops at RMAX in the
  EWRAM glyph buffers 0x02020000-0x02030FFF: rerun with `--var RXLO=0x02020000 --var RXHI=0x0203FFFF` (or a
  higher RMAX) to see the rest. Getting money then buying parts at shop 1 is a candidate route to a first Medabot.

## Events (field event scripts; verified 2026-11-17)
- **Event table** 0x084FC358: one u32 per event index, **688 events**. Fetch 0x08050678: byte =
  `[table[ev] + pc]`, event index u16 at 0x03005256 (+0x9A6), pc u16 at 0x03005252 (+0x9A2), current command at
  0x0300525A (+0x9AA). Argument byte count per command: 0x0847B050[cmd]. Handlers: 0x0847B160 (122 entries, run on
  dispatch, called at 0x0804D63C / 0x080502A6 / 0x08050308) and 0x0847B618 (per-frame continuation, same index).
  `python -X utf8 tools/debug/evdump.py` writes every script to `work/re/events.txt` (`--ev 0x1CB` prints one).
  `tools/lua/evtrace.lua` logs each dispatched command (event, pc, cmd, map; `EVTRACE_BYTES=1` hooks a second
  fetch routine 0x08050650 that the field events don't use).
- **Commands seen:** `02` end. `01 a b` text: bank a>>4, index ((a&0xF)<<8)|b; bank A = the string pointer table
  0x50A9D8 (`01 a2 6e` = index 0x26E = "ここは MーPKたい ベント・デル・マーレ しぶ"; entries 622-1100 of that table
  all point at that one string, i.e. unused slots). `1F hh ll` sets story flag hhll (each event sets its own index
  when done, e.g. `1F 01 cb`). `43 hh ll`, `21 hh ll v`, `20 hh ll`, `5F hh ll v` take a flag number too (guess:
  clear / set-var / test). `52 actor x y dir` places an actor (guess). `75 n` starts a cutscene (event 0x1CB:
  `75 00` = the medal-finding scene, mode 3 sub 3).
- **Map event lists:** pointer table 0x0847DF80 (141 entries = map ids, read at 0x08056370), records of 12 bytes
  with the event index u16 at +6, several FF-terminated groups per map (story phases, guess). Map 18 (town door
  (12,6) -> map 11 -> map 16 -> map 18) holds events 0x222-0x225, the M-PK officer, but at the medal story step the
  room is empty: the group selection (which flags pick a group) is the next thing to read.

## Story walk (first Medabot hunt, session 3)
`tools/debug/story.py FROM NAME "route"` plays a route from a state, mashes A until the player has control and
saves `work/play/s/NAME.mss` + shot, printing every dialogue string shown (decoded with `tbl/jp.tbl`; helper
`tools/lua/mash_idle.lua`). `--warp --var MAP=n --var X= --var Y= --var MASH_FROM=300` warps first.
`tools/debug/ramdiff.py A.mss B.mss` diffs the save block (or `--lo/--hi`) between two states.
Opening, from `work/states/home_2f.mss`: stairs (left, up) to 1F; walk to the door: mother asks Ikki to walk the
dog Kamui; out to the town (map 0) and down/east into the park (map 3, door (29,24)). In the park the dog runs off
(a short camera scene); walk right along y=9 to x=14: the dog stands by a glowing medal at (16,9). Step up, right
2, face down, A: event 0x1CB (medal cutscene, "「クワガタ」メダルを てにいれた", medal name entry 2/18 -> 2/6). Then
the medal list shows the Kuwagata medal; the save block change is only flags (+0xE1 0x80->0x88, +0xE5 0x00->0x88,
+0x1F4-0x206 cleared, +0x5EF/+0x5FE 07->00). Ikki's line: take the medal to the M-PK corps. Not found yet where
that event fires (map 18? map 40 is an empty pink building west of town).

## Robattle (mode 0 sub 6)
- Steps 0..13 (intro, referee, formation), 32, 33 (fade: counter 0x030005AC to 8), 34, ... (`tools/lua/modelog.lua`).
- Opponent table by map: 0x0846A7B0 + map*8, 2 bytes copied to 0x03000616 by 0x08012818.
- **A raw mode write crashes** after the opponent's line: step 33 calls RAM code at 0x03004220 (via `bx r0`
  0x0808B984 from 0x080023A4) that the field's encounter path sets up, and it jumps to 0x0FF336E0.
- **A real encounter works:** on a field map pin 0x030051F1 = 1 (encounters on), 0x030051F3 = 0x20 (step
  counter), 0x030051F5 = 0 and walk (`tools/lua/pin.lua`); mode 0 sub 6 starts by itself and reaches step 34, then
  stays black with the CPU idle (pc 0x24, lr 0x080005DA): presumably no player Medabot. `robattle_intro` in
  scenes.txt is still the raw write (good to the opponent's line only).

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
