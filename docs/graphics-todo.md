# Graphics text still Japanese (phase 8 redraw list)

From the visual-QA pass of 2026-11-17 (codex reviewer over `work/qa/tour/sheet*.png`, verdicts in
`work/qa/verdicts/chunk_000.tsv`). Every item below is graphics: `tools/findtext.py` finds none of them as text
(hits it prints are other dialogue), and `tools/textmap.py` explains every byte of the text region. Match each to
its block with `vramfind.py` over the scene shot (`work/qa/scenes_en/shots/<scene>.png`, states from
`prove.py`), redraw, and re-shoot the scene zoomed from a cold boot.

| Scene(s) | Japanese left |
|---|---|
| title, newgame_menu | logo 真型 メダロット: kept as the original logo (D14), つづきから (not seen yet: needs a save; probably elsewhere in lz_72AC64). **Done:** はじめから -> NEW GAME, オプション -> OPTIONS (screen labels on tiles lz_72AC64 + map lz_72BF8C+10) |
| options (same screen, BG0 rows 11-17 of map lz_72BF8C+10) | **Done** (session 5): ROBATTLE TIME, LONG / NORMAL / SHORT, ROBATTLE TEXT, ON / OFF (label6); つづきから -> CONTINUE (same map, rows 1-2) |
| save_corrupt | **Done** (session 4): message in the dialogue font (lz_72DA44 / lz_72E878+10) |
| sound_test (test mode) | **Done**: TEST MODE, MUSIC, SOUND FX, BACK (lz_72C710 / lz_72D4B8+10) |
| name_entry | **Done** (session 8): NAME ENTRY, prompt "Enter a name, / up to 10 letters.", buttons SPACE (すすむ types a blank and advances) / BACK (deletes) / OK, tabs ABC / abc / 123, three letter grids (screen mode over tiles lz_72F06C, `fixed_tiles`: VRAM after the block is in use; page 1 on BG1 map lz_73163C, pages 2-3 on BG0 map lz_7313EC rows 7-15 / 21-29; text items with `cells`). Input codes: `tools/nameentry.py` rewrites the grid table 0x0C1414 (3 pages x 5 rows x 24 bytes, FF gap, FB-FD tabs, FE row end) and the default name ガンマ (0x50C620 via 0x50C624) -> Gamma. Verified in the emulator: typing, page switching, SPACE/BACK/OK, gap rows |
| field_menu | **Done** (pilot): MEDAWATCH / ITEMS / HELP / SAVE (Le 54C27C/54C420/54C5A0/54C72C), money 円 -> ¥ (Le 56C920 tile 0; names charset C5 too). Other screens with a money box may load their own 円 copy: check |
| items, items_owned | **Done**: ITEMS, Use item, Sort (lz_7281F8 is a `fixed_tiles` block: the page digits sit right after it with hard-coded tile numbers) |
| field_help (encyclopedia) | **Done**: the heading is the field-menu HELP block le_54C5A0 (pilot) |
| medawatch | **Done** (session 5): MEDABOTS / MEDALS / PARTS, Choose with cursor, OK, Back (le_56D154 tiles + le_578E40+10; `fixed_tiles`: appended tiles ran into le_54C890 at VRAM tile 496 and showed garbage) |
| medal_list, party_medals | **Done**: MEDALS, Choose a medal, Details, Lv.UP IN (block le_57134C, `layout`) |
| medarot_list, party_setup | **Done**: MEDABOTS, Assemble, Sort (le_56F328, `layout`) |
| parts_list, party_parts, parts_owned | **Done**: PARTS, Details, NAME / ×OWNED / (EQ) / M/F (le_575BE4, `layout`), tabs HEAD / R.ARM / L.ARM / LEGS (le_54EC30, cols 10) |
| parts_*_detail | **Done** (session 6): PARTS + -HELP (le_576784, `layout`; HELP is BG1 pal 6), 11 stat labels ARMOR / SUCCESS / POWER / USES / CHARGE / COOLDOWN / PROPULSION / MOBILITY / DEFENSE / MELEE / RANGED (le_54F1B8, 12 cols, one label per 8-px row). robattle_detail not checked (its scene shot is the battle field, not the detail screen) |
| parts_shop* | **Done**: headers, Buy/Sell parts/Exit, HEAD/R.ARM/L.ARM/LEGS, Select/OK, list hints and column headers (lz_733100 + maps 734590/734790; list screens lz_734D90 + maps 735630/7357EC, loaded at tile 355). **Left:** confirm はい / いいえ (below) |
| save, parts_shop_confirm (yes/no window) | **Done**: SAVE, MEDALS, PARTS, PLAY TIME, WINS/TOTAL; **YES / NO** (session 7: glyph block le_51126C grown to 9 tiles with `grow`, VRAM tiles 0x13E-0x13F were empty in both screens; inner layout le_511A20 rows 2-3 patched with `patch` so NO gets its own tiles 5-8). Old notes: 7 tiles le_51126C (BG0 tiles 311-317: 137 blank, 138/13A は top/bottom, 139/13B い, 13C/13D え); the window map is copied by 0x08042E50 from a template at VRAM 0x06002D40 (6 rows x 8), itself written by the generic copier at 0x08000F1A (source r2 = 0x02030024, EWRAM) at f2719: find who fills 0x02030024 (the ROM table of the window layout). い's tiles appear in both words (row 1: 137 138 139 137, row 2: 137 139 139 13C), so YES/NO needs either that layout table changed or 8-px-wide words |
| parts_trade | **Done**: PARTS TRADE |
| robattle_intro, robattle_prep | **Done** (session 6): ROBATTLE INFO + BATTLEFIELD tab (le_570D84, 3 ptrs; the header sits half above the screen top, as in the JP), prep header MEDABOTS (le_57D37C). Box contents (session 9): text, already English: field name + opponent name in the dialogue font ("Grassland", "Boyoyo"), seen whole on the story path (`warp.lua SCENE='robattle_prep'`, frame ~4260, `work/qa/rp_en/introz.png`); the `robattle_intro` scene (random encounter, no party) only catches them mid-slide, JP alike |
| road_race | **Done** (session 6): MEDAROAD RACE (lz_748608 tiles 1-30, `layout`, style race_title) |
| baseball | **Done** (session 7): counters BALLS 10 / 0 PTS (`tools/minifont.py`: glyph lists 0x50EB4C / 0x50EC08 in the text region pick 8x16 glyphs from a raw font at 0x087C49CC + code*64, literals 0x77BE8 / 0x788E0; the font is copied past 8 MiB with two-letter 3x7 cells), PLAY BALL! (OBJ le_7C26E8, 3 pieces, piece 0 sits 4 px over piece 1), SWING (le_78CA88). Old notes: counters are BG1 (char base 0x4000, screen 0xC800) built at run time from 8x16 glyph pairs: tile 2/3 の, 4/5 こ, 6/7 り, 14/15 て, 16/17 ん, 18/19 き, 20/21 ゅ, 22/23 う, 34/35 0, 36/37 1 (no whole block in VRAM: find the glyph source with vramwho.lua at 0x06004040). Redraw the kana cells (e.g. のこり -> LEFT, きゅう -> BALL, てん -> PTS in a narrow font) unless the map writer can be changed. プレイボール / バットをふる: sprites or BG2 (le_78CA88 tile 98, 7 tiles at BG2 row 18 = バットをふる) |
| car_game | **Done** (session 7): TIME 60 / 0 PTS (minifont), MEDAKART RACE / START!! (OBJ le_7C3C68, 5 pieces, `layout` with nulls). Old notes: Same 0x4000 glyph set as baseball (BG0/BG1); BG2 map le_789E58+10, BG3 le_78A780+10 on tiles le_78059C |
| corps_game | **Done** (session 7): BOMBS, LIFE, CONTROLS (was プレイ ナビゲーター; screen mode, erase `copy_off` [0,-8] over the 8-px checker), banner DEFEND / SELECT HQ!! (OBJ lz_73F8A0 tiles 549-596). Old notes: Screen mode fits: tiles lz_74949C, maps lz_74AAE4+0 (BG1), lz_74AC50+0 (BG2), lz_74AD20+0 (BG3), 32 wide |
| town_map | **Done**: TOWN MAP |

Not graphics, also found in that pass (text/engine):
- **credits role lines cut: fixed (session 9).** Each credit line is one 8x8 sprite per glyph in OAM records
  given by a hard-coded first slot per line, sized for the Japanese, so English lines ran into the next line's
  records. `tools/credits.py` (build stage) re-allocates the 45 slot immediates from the English byte counts in two
  banks of 64 (even/odd pages); test `tests/test_credits.py`. Verified whole on the English build from a cold-boot
  warp, all 15 pages (`work/qa/cr10/band*.png`). Was: `work/qa/credits_t/sheet.png`.
- money digits in the field-menu box look squeezed against each other compared with the original's spaced digits
  (`work/qa/zoom/fm.png`): check the 8x8 digit overrides in `font/en_names_8x8.txt` / the advance used there.
- item list: "Rubberobo Medal" ends against the "x" column (`work/qa/zoom/io.png`); 86 px may be 2-4 px too wide.
- terminology: one encyclopedia topic says Speed, its text says Propulsion (sheet_4): check glossary.
- "Cervoアアアアア": the debug tool's A-mash through Medabot naming appends ア (as ガンマアアア for the player);
  not a translation bug, but the name entry grid needs English letters.
