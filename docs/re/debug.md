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

## Inventory and party (session 4, verified)
| Address | Layout (evidence) |
|---|---|
| 0x03000BE0 | **medals**: 30 records of 0x40 bytes; byte 0 = medal index \| 0x80 when owned \| 0x40 when set in a Medabot, byte 1 = name index (0x080097D8 reads +0 bit 7, names via 0x08465B8C[+1]). The Kuwagata medal is record 0 |
| 0x03001790 | **Medabots**: 9 records of 8 bytes: status (0 none, 1 new, 3 built), gender, medal (0x1F none), head / right arm / left arm / legs part ids (0x3C+gender = none), slot. Created by 0x080437DC; event 0x1D2 leaves `03 00 00 15 15 15 15 00` |
| 0x03001D80 | **items**: 40 records of 2 bytes, [0x80 \| id, count] (0x0804381C finds, 0x0804385C adds) |
| 0x03003DF0 | **parts**: + type*0x78 + id*2, 4 types x 60 parts; byte 0 = count owned (the list shows it mod 100), byte 1 = the "(n)" figure. Poking counts makes them show in the parts list (0x080436B8 reads, 0x080436E0 adds, 0x08043714 removes) |
Event commands that give things (per-frame table 0x0847B618): `10 id n type` part, `11 n` medal (0x08043300), `13 id n`
item (0x080438BC), `14 ..` take part, `35 g` new Medabot (gender g). Event 0x1CB pc 2 (`11 00`) gives the first
medal, event 0x1D2 pc 8 (after its condition `1D 03 07 55`) builds the first Medabot and gives parts 0x15 of all
4 types. `warp.lua` runs both through the game's own interpreter (scene key `events`, below).
The old "task slots at 0x03000BE0" guess was wrong: that is the medal list.

## Money, shops, ending (session 5, verified)
- **Money:** u32 at **0x03001D50** (the Start menu reads it at 0x08002A38 and prints it with 0x0804270C(dst, value),
  5 digits + 円 0xC5 + FE into 0x030005C6). Poking 12345 shows "12345円" in the Start menu and the shops.
  0x03001D64/66 (capped at 9999 by 0x08011554) are something else.
- **Parts shop with stock:** scene switch case 3 (mode 2 sub 11, shop id 0x03001D3C = 1 or 2): clerk menu
  buy/sell/leave -> A, A -> part type picker -> list (shops 1 and 2 stock different heads). In the list: right
  = quantity +1, A = cart total and yes/no (default いいえ), up+A buys (12345 -> 11545 for an 800円 head), Start = part
  detail screen (skill text). Sell lists spare parts only (counts at 0x03003DF0 + type*0x78 + id*2).
- **Items:** 0x03001D80 [0x80|id, count]; item 1 is named "ダミー" (dummy), 2-4 ロボロボメダル, ふくびきけん, わたるくんルアー.
- **Help (Start menu, 3rd row) = the encyclopedia (mode 4 sub 5):** 12 topics on 3 pages, shown as "????????"
  until unlocked by bits at **0x03004260-0x03004267** (saved; read at 0x0807A1FA/0x0807A95C/0x0807AA60). All 0xFF
  unlocks every topic; A opens a lesson (teacher + Medabot frame). Topic 12 is "「テストモード」について".
- **Ending:** event 0x26F (`04 23`, `20 02 1d`, `20 02 1e`, `75 0a`, `6E`, `78 63`, ...) plays cutscene 10, then
  the staff credits (mode 4 sub 6: steps 3-5 per page, 6 the closing group picture, 7-9 fade) and returns to the
  field in Ikki's room (mode 1) at ~f4800 from its start. `warp.lua` key `run={ev,pc}` starts an event without
  waiting for its end (pair with `wait=`); `EVENT=n` plays any event ad hoc.
- **Story robattles** start from NPC talk: the talk-action dispatcher around 0x08055B44 calls the scene switch with
  case 0x20 for action 0x20 (team id already in +0x942; +0x942 = 0x22 has a special line). Who writes +0x942 for
  each NPC is not traced yet; the scenes set it directly (any of the 169 team ids works).
- **Random encounters:** with +0x945 = 0 the setup rolls a team from 0x0846AC18 + map*4 using the map id at
  0x03004DC6, so poking map 30 before the switch gives a real beach encounter while the player stays home.
- **Three Medabots:** medal records 1-2 can be copies of record 0 with byte 0 = 0xC1/0xC2; Medabot records
  `03 g medal head rarm larm legs n` at 0x03001790 + n*8; the robattle then fields all three.
- **Map tour:** `tools/debug/maptour.py` warps to every map id (arrival tile = the first door into it) and shoots
  each (`work/qa/maps/shots/mNNN.png`, sheets `work/qa/maps/sheet*.png`).

## Robattle teams (session 4, verified)
- Setup 0x08012854: if +0x945 (0x030051F5) != 0 (story) the team id is +0x942 (0x030051F2); else a weighted roll
  picks one of 4 ids at 0x0846AC18 + map*4 (0xFF = no random battles: maps 0-29 and most towns; maps 30-33, 36-38,
  44, 48-52, 61-63, 71, 76-91, 95-97, 102-106, 110-114, 117, 128, 131 have teams). The team record (0x28 bytes,
  byte 2 = Medabot count) is copied from pointer table 0x0846C8B4 (169 teams) to 0x030017E0.
- **Why robattles hung before:** on a map with no team (town, home) the "team" is 0x28 bytes of whatever follows
  the table entry (0x0134 words), so the count byte is 0x34; the sprite loop at 0x08012B10 (0x08044968 per entry,
  objects at 0x03001DE0 + n*0x40) runs past the object table into the link state 0x03004140 and the link
  routine copied to 0x03004220 at boot (from 0x08000218). Step 33 then calls that routine (0x08002390) and the
  CPU dies with VBlank masked. It is not an emulator bug. A story robattle (+0x945 = 1, team id set) runs.

## Save block and inventory hunt (2026-11-17, superseded by the section above)
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
- **Superseded (session 4):** the crash at step 33 after a raw write or a town encounter was the missing team (see
  §Robattle teams): no team on that map, the sprite loop overruns into the link routine at 0x03004220.
- **Working path:** party from events 0x1CB/0x1D2, then mode 0 sub 6 with 0x030051F5 = 1 (story) and 0x030051F2 =
  team id. Subs: 6 intro (steps 0-13, 32-34), 3 pre-battle Medabot check, 7 command phase (step 70 waits for input),
  8 action, 9 attack close-up, 6 step 48 result (win: steps 51, 52, 112 "ロボトルインフォメーション" spoils;
  loss: then mode 2 sub 8 game over). With A mashed, our lone Medabot loses to team 1 at ~f9800 of a cold boot.
- **Battle records:** ours at 0x03000680 (medal copy at +0, part ids at +0x37, armor max at +0x8F, current at
  +0x95..+0x99; all 0 head = loss), the enemy's around 0x03000900 (part ids 0x31 at 0x0300092F). God mode for the
  first Medabot = pin 0x03000715-19 to 2D 1C 22 20 18 (`robattle_win`).

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
