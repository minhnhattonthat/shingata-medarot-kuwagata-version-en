# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: in progress (graphics redraws: sessions 4-5 done 17 screens; rest of `docs/graphics-todo.md` next).
- **Phase 8 session 5 (2026-11-17): graphics redraws, batch 2.**
  - **Done, verified English in cold-boot `prove.py --no-states` shots** (`work/qa/gfx6`, medawatch `work/qa/gfx7`;
    build sha1 1457ebc2...): options (ROBATTLE TIME, LONG/NORMAL/SHORT, ROBATTLE TEXT, ON/OFF) + title CONTINUE,
    medawatch, medal_list/party_medals, medarot_list/party_setup, parts_list/party_parts/parts_owned (+ tabs),
    field_help heading (was already the HELP block). 55 labels, `gfx.py check` 0, `tools/check.py` exit 0.
  - **`gfx.py` block `layout`**: rows of block tile numbers (null = don't touch) for blocks whose map the code
    builds (no LZ map to find): the label is drawn on that virtual image and written back per tile; a tile used
    twice must come out identical. One label per block (each composes from the original; `check` now fails
    duplicates). **`tools/blockcells.py SCENE TILE0 COUNT`** prints which map cells show a block's tiles (after
    `screenfind.py SCENE`), i.e. the layout to copy. New styles `msg_outline` (dialogue font + outline 1),
    `lv_green`; `(` `)` added to `font/en_label_6.txt`.
  - **Gotcha:** screen mode appends new tiles to the block; on medawatch that ran past the block's VRAM room into
    le_54C890 (tile 496) and showed garbage in-game while `gfx.py check` passed. Fix: list the block in
    `fixed_tiles` (with every map using it). Check every screen-mode redraw in a shot, not only the preview.
  - **Next:** parts_*_detail (パーツ, ヘルプ, stat labels; robattle_detail too), yes/no window (findings in
    graphics-todo.md), name_entry, robattle_intro/prep (le_570D84 at BG1 tile 512), minigames (road_race, baseball,
    car_game, corps_game), title logo ruling (non-blocking). Then pair sheets + verdicts for all redrawn scenes,
    credits role buffer bug, textcover gaps, inkbox on choice/centred boxes.
- **Phase 8 session 4 (2026-11-17): graphics redraws, batch 1.**
  - **Done, each verified English in a cold-boot `prove.py --no-states` shot on the English build** (`work/qa/gfx2..gfx5`):
    town_map, sound_test, save (labels; not yes/no), parts_trade, save_corrupt (message), items, parts_shop menu,
    type picker, list/sell/confirm headers + hints + column headers. 40 labels in `gfx/labels.json`, `gfx.py check` 0.
  - **`tools/screenfind.py SCENE`**: dumps the original's VRAM from `work/states/SCENE.mss` (once, `work/gfx/s_SCENE/`),
    prints per BG the tile blocks (tile0) and map blocks (`+10`, 30 or 32 wide), sprites; renders `bgN.png` (zoom 2,
    8-px grid) and copies the palette for `gfx.py preview`. `--grid BG X Y W H` prints colour indices (read the
    label's fill/outline rows from it). `--warp --rom build/...` = the same on a cold-boot warp of a build.
    Maps whose entries are relative (tiles loaded at a fixed base, e.g. shop lists at 355) don't match: search a
    row with the base subtracted (done by hand for lz_735630).
  - `gfx.py`: maps with a 16-byte header use its width (30-wide 240-px maps); fonts: `font/en_label_6.txt` (6-px caps
    + `×`, style `label6`: fill 1/2, outline 3), the dialogue font `en_glyphs` (style `msg_white`: fill 15, half 8),
    style `header_yellow` (the 16-px screen headers: fill 2/3/4, outline 15, halo 1; same indices on every header).
    **`fixed_tiles`** {block: [every map using it]}: new tiles go into tiles only the Japanese labels used, the block
    keeps its size. Needed where the game puts tiles with hard-coded numbers right after the block (items page
    digits "1/1" broke when tiles were appended). Elsewhere appending was verified safe (le_7239FC follows the
    decompressed size). Check each screen's digits/cursors in the shot after a redraw.
  - **Next:** yes/no window (findings in graphics-todo.md, save + shop confirm), then options (label6 now exists),
    medawatch / medal_list / medarot_list / parts_list / field_help / parts detail (char base 0, Le blocks: block
    mode like field_menu; screenfind finds no LZ maps there, use vramblocks/declog), name_entry, robattle_intro
    (le_570D84 at BG1 tile 512), minigames, title つづきから. Then pair sheets + verdicts for all redrawn scenes.
- **Phase 8 session 3 (2026-11-17): graphics pipeline + pilot.**
  - **`tools/gfx.py`** + **`gfx/labels.json`**: the build (`rombuild.build` -> `gfx_stage`, after `names_stage`)
    redraws labels, recompresses past 8 MiB and repoints every literal-pool word of the block (`ptrs` /
    `screen_ptrs` = expected count; romcheck accepts those slots via `gfx.block_offsets()`). Two modes:
    *block* (the block is the image: `codec/off/cols`, erase rects with `index` or `copy_col`, text items) and
    *screen* (`tiles`+`map` sources like `lz:72BF8C+10`, box on the 8-px grid: paint on the rendered map, each changed
    cell gets a new/identical tile appended to the tile block and its map entry repointed, palette kept).
    Styles: font, `top`, `spacing`, `fill` gradient `[[row, index]..]`, `outline`, `halo` (+`halo_on`).
    `names_tiles` copies a names-charset glyph into a tile. `gfx.py check` (in tests/test_gfx.py): box fit, no pixel
    changed outside the boxes, codec roundtrip, pointer counts. `gfx.py preview OUT [--only ids]`: JP over EN, zoomed
    (palette from `work/gfx/pal/<scene>.pal.bin`).
  - Font `font/en_label_9.txt`: hand-drawn bold 9-px capitals, digits, `!?.-:'/` (MIT, add to docs/fonts.md next).
    ¥ added to `font/en_names_8x8.txt` as code C5 (円) for money boxes (`font.names_tiles` takes charset-only codes).
  - **Done, verified by cold-boot warp on the English build:** field_menu MEDAWATCH/ITEMS/HELP/SAVE + ¥
    (`work/qa/gfx_fm`), title menu NEW GAME / OPTIONS (`work/qa/gfx_title`). Build sha1 70980946..., romcheck 0.
  - **How to find a screen's source (fast):** `emu.py ORIG --state-in work/states/<scene>.mss --frames 30 --script
    $SKILL/scripts/lua/probes/ppudump.lua`, then `python tools/vramblocks.py <dump>.vram.bin` (blocks whole in VRAM,
    by address), BG registers from the `.io.bin` (BGxCNT at 0x08), map entries -> tile numbers; maps are LZ77 blocks
    with a 0x10 header (search a map row in work/blocks). When a label isn't whole in VRAM:
    `tools/lua/vramwho.lua --var ADDR=0x0600xxxx` (writes with r0-r14: the Le writer's r12/r5 = source) or
    `tools/lua/declog.lua` (Le calls with src/dst). G12 "battle labels" in docs/re/graphics.md were the field menu.
  - **Next:** a 6-px label font for the 8-px rows (options panel, small headers), then the rest of
    `docs/graphics-todo.md` one screen at a time (save, name_entry, medawatch, lists, shops, parts detail, minigames,
    save_corrupt, sound_test); after each batch re-run prove.py for the scenes, rebuild pair sheets, new verdicts.
    Still open from session 2: credits role buffer bug, textcover gaps, inkbox on choice/centred boxes.
- **Phase 8 session 2 (2026-11-17):**
  - English scene proof finished: **77/77 arrive** (`work/qa/scenes_en/shots`, all copied; `prove.py` now copies
    each shot as it arrives). `shotdiff.py work/qa/scenes/shots work/qa/scenes_en/shots`: 7 identical, the rest
    differ by text/timing; the 7 newer scenes (robattle_menu.., parts_owned..) have no original shot yet (run
    `prove.py --no-states --only robattle_menu,robattle_parts,robattle_detail,robattle_menutour,parts_owned,parts_owned_detail,parts_legs_detail`
    on the original ROM; note: without `--no-states` it overwrites `work/states/`).
  - Visual QA: pair sheets EN|JP `work/qa/tour/sheet*.png` (13, `sheet.py ... --compare work/qa/scenes/shots --cols 2
    --max 6 --div 1`), gate `work/qa/manifest.tsv` (build recorded), brief `docs/visual-qa-brief.md`, codex verdicts
    `work/qa/verdicts/chunk_000.tsv`: **2 ok, 11 issue**. Issues = graphics Japanese on almost every menu screen
    plus 4 text/engine findings: all listed in **`docs/graphics-todo.md`** (credits role lines cut at ~13-16 glyphs
    is a real bug; money digits squeezed; item name touching the x column; Speed vs Propulsion topic title).
  - Event tour (new): `tools/debug/eventtour.py` plays every story event 0-687 back to back from cold boots
    (`warp.lua EVENTS=`, EVSTART/EVSTUCK in the log; resumable) with the textcover probe ->
    `work/qa/events_en/run_*`. **Textcover:** scenes 191/8029 strings shown; the event tour (reaped for low
    memory in the background after events 0-0x107, 26 runs, many EVSTUCK) 360/8029. Resume it in the
    **foreground** in slices (`eventtour.py --to 0x180`, then higher; it skips events already started), one
    emulator at a time. 2-8 events per run get stuck (robattle/map change) and cost a cold boot each: if the
    rest stays slow, make EVSTUCK skip the event (reset to field) instead of ending the run.
  - **Next in phase 8:** graphics redraws (`docs/graphics-todo.md`, `references/graphics.md`; pilot one screen,
    e.g. field_menu, then the rest); credits role buffer; textcover gaps (new scenes or `docs/text_unshown.tsv`
    waivers); inkbox on choice/centred boxes (save はい/いいえ, shop confirm, options); after each fix re-run
    `prove.py` for its scenes, rebuild the pair sheets, `qa_gate.py init` + new verdicts (`verdicts/recheck_N.tsv`).
- **Phase 8 session 1 (2026-11-17):**
  - Phase 7 review (`.harness/reviews/...-phase7.md`) fixed, all Important + Minors 1, 2, 4 (c1bca0c):
    `{fa:FF}` info panes draw page 1 only (parts_shop_detail, `work/qa/pg_psd` vs `pg_psd2`), so 37 pane + 2 timed
    battle lines refit to 2 lines; `lint.py page_problem` fails an added `{page}` in panes, timed lines and tables
    whose JP never pages unless `data/windows.json` "page_tables" gives evidence (FC's A-wait is inside the runner,
    0x0804123A -> 0x08041A28). Stub rule now: last line < 6 characters (author `{n}` too) fails; 270 lines
    rebalanced by codex (`batches.py fixset s001-s003` = fix batch seeded with the live English, then
    `merge --overwrite`). romcheck: out-of-range pointer writes only at known slots. FE names keep the JP's
    leading/trailing blanks. Captain Oro -> Leader Oro (glossary Avoid).
  - Open from the review: **Minor 3** (jp_left on the build: needs a jp_left .tbl without codes 52-78/A2-CF and a
    slots file; wire into `tools/release.py` in phase 9); **Minor 5** (alt font flag): `prove.py --probes` now
    watches writes to 0x03000547 (state+0x27) in every scene log (`pc=... addr=03000547 <value>`); so far only
    value 0 seen (home_1f). Check all scene logs: `grep -h 03000547 work/qa/scenes_en/*/log.txt | sort -u`, then
    record the result in docs/re/text.md. Verify page_tables entries 46D598/46E0F0 (robattle face lines) in a
    battle tour.
  - Text coverage wired: `build.py` writes `build/medarot_kuwagata_en.strings.tsv` (id, GBA address in this build);
    `prove.py --probes` adds textcover.lua (ranges from that file) to each scene run. Report:
    `python -X utf8 $SKILL/scripts/textcover.py work/qa/scenes_en build/medarot_kuwagata_en.strings.tsv --mask 0x1FFFFFF`.
  - English proof `prove.py build/medarot_kuwagata_en.gba --no-states --qa work/qa/scenes_en --jobs 1 --probes`
    (build sha1 of c1bca0c + strings.tsv) was **reaped for low memory again after 39 scenes**: rerun only the missing
    ones (`--only a,b,..`: the scenes with no `work/qa/scenes_en/<scene>/arrived.png`), in the foreground, alone.
    All 0x03000547 writes in those 39 logs store 0 (alt font never selected so far).
  - **Next in phase 8:** finish the proof; `shotdiff.py work/qa/scenes/shots work/qa/scenes_en/shots`; qa_gate
    manifest + visual-QA verdicts (fresh read-only pass, or `codex exec` read-only); textcover gaps -> new scenes or
    `docs/text_unshown.tsv` waivers; inkbox on choice/centred boxes; graphics-text redraws (list under "Japanese
    left" below).
- **Phase 7 result (2026-11-17):** build green. `tools/check.py` exit 0: 32 tests, lint 0 errors (now also fails a
  wrapped page ending in a stub line < 24 px, and any reached string with Japanese but no `en`; exceptions go in
  `script/keep_jp.txt`, none needed), batch check 0 problems (control codes matched). `tools/romcheck.py` (and
  `tests/test_build.py`, a fresh in-memory build): romdiff with the write log, 16841 writes, 0 problems; writes only
  in `data/allowed_ranges.txt` (text region, past 8 MiB) or 0x08 pointer words; every translated slot reaches its
  English. 226 stub lines rebalanced by a codex fit pass (`work/tl/stubfit_*.txt`). Build sha1 583ec02b..., smoke
  ok. Scene proof on the English build (`prove.py build/medarot_kuwagata_en.gba --no-states --qa
  work/qa/scenes_en --jobs 1`) was **reaped for low memory after 13/70 scenes** (shots in `work/qa/scenes_en/<scene>/`,
  home_1f dialogue clean); rerun it first in phase 8, alone on the machine, then `shotdiff.py work/qa/scenes/shots
  work/qa/scenes_en/shots`.
- **Phase 6 review fixes (.harness review of 2a392e9, all Important items):** capped part names now the closest
  10-byte form (D11: widening ruled out); メダロットしゃ = Medabot Company (glossary row, 10 lines fixed); Gang Boss
  label, Music Tchr / Sci. Tchr (cap), credits "Events & Battles" (D12); every Minor in `docs/polish.md` (one line
  each, release gate needs them ticked); reviews and fix logs in `docs/reviews/` (`tools/collect_reviews.py`).
  `tools/rereview.py` sent every group's fixed lines to a read-only reviewer: **all 28 groups Approved**
  (`work/tl/review/*.status` = "READY: re-review approved"; b032 needed glossary exception for the 4CDB37 chant).
  `tl_pipeline.py` now ends with rereview; `batches.py merge --overwrite` also updates earlier copies.
- **Phase 6 result:** every batch b001-b084 translated, independently reviewed (codex reviewer, `docs/reviewer-
  brief.md`) and fixed (`work/tl/review/<first>.review.md`; fix logs
  `work/tl/logs/*.fix.last.txt`: ~100 findings applied, 2 rejected: 25 capped part names now in glossary.md
  "Capped part names", and Robo-robo vs the binding Rubberobo). Merged into `script/`: **7976 of 8038 strings in
  `en`**; the 62 without are control-code-only strings plus 9 dead strings in `unused.json`. `batches.py check`
  b001-b084 all OK, `tools/check.py` 0 problems, lint 0 errors/0 warnings. Glossary gained a homograph row
  (なぞのベール, so ベール = veil isn't forced to Behr) and the capped-names table.
  Build 2026-11-17: `build/medarot_kuwagata_en.gba` sha1 3b1bf93e..., 7936 strings moved, smoke ok, warp to
  parts_shop shows English dialogue (`work/qa/warp_p6/final.png`; warp needs `--frames 4000` from a cold boot).
  Pipeline (for re-translation or fixes): `tools/tl_pipeline.py "bNNN ..."` -> `batches.py merge .. --overwrite`.
  **Memory:** run at most 3 codex lanes at once (7 lanes got everything killed); background shells left idle may be
  reaped under memory pressure, so wait in the foreground.
  Docs: `docs/translator-brief.md`, `docs/reviewer-brief.md`, `docs/synopsis.md` (two casts: Shingata's
  Gamma story in 50A9D8/4B50CC/46D598/46E0F0/510124; retained Medarot 2 Core Ikki story in the 4F tables).
  Marker build `build/marker.gba` (`build.py --marker`; `--full` fills dialogue lines to 208 px): boots, 70/70
  scenes arrive (`work/qa/scenes_marker/shots`, `prove.py build/marker.gba --no-states --qa work/qa/scenes_marker`).
- **Done:**
  - Step 0: MesenCE 2.2.1 in `tools/mesen/` (+ GBA BIOS), guard hook proven (canary blocked), pre-commit runs
    `tools/check.py` and rejects a failing test, `rom.sha1` pinned, boot route reaches the title menu.
  - Phase 1 recon: `docs/re/` (prior work, ROM map, text encoding + control codes, 7311 FF strings + 1129 FE names,
    the game's own VWF, graphics survey G1-G33). "Le" and LZ77 codecs tested.
  - Phase 2 debug tool (`docs/re/debug.md`): `tools/debug/warp.lua` boots cold (new game, intro) and reaches any of
    the **70 scenes** in `tools/debug/scenes.txt`; `tools/debug/prove.py --jobs 2` proves them all from cold boots
    and writes `work/states/<scene>.mss` (all 70 ARRIVED on 2026-11-17: 50 in one full run, the 20 added this
    session in `--only` runs; shots `work/qa/scenes/<scene>/arrived.png`). Coverage: field maps, Start menu (money),
    help = encyclopedia (empty, 3 pages unlocked, a lesson, the "test mode" topic), Medawatch, Medabot/medal/parts
    lists (empty, 1 and 3 Medabots), items (empty, owned), save, name entry, options, game over, save-corrupt, sound
    test, town map, parts trade, parts shops 1 and 2 (clerk, type picker, buy lists, detail, cart yes/no, purchase,
    sell list), robattles (intro, prep, command phase, attack, win, loss, random encounter on the beach, full party
    of three), the 11 story comic cutscenes, the ending (event 0x26F: cutscene 10, credits, closing picture, back
    to Ikki's room), credits alone, 4 minigames, Medarot Weekly, logo, opening, title.
    Ad hoc: `MAP=n`, `EVENT=n` (any of the 688 story events, A mashed), `RAWMODE/RAWSUB`. Scene keys added this
    session: `run={ev,pc}` (start an event, arrive by `wait=`), `poke={[addr]="hex bytes"}`.
    `tools/debug/maptour.py --jobs 2`: all 141 map ids warped and shot (`work/qa/maps/sheet*.png`).
    RAM: money u32 0x03001D50, shop id 0x03001D3C, encyclopedia bits 0x03004260-67, medals 0x03000BE0, Medabots
    0x03001790, items 0x03001D80, parts 0x03003DF0, team id +0x942 / story flag +0x945.
  - Phase 3 identity build: `build.py` -> `tools/rombuild.py` (text stage: every string of the 61 text tables +
    4 code literals found by `tools/texttables.py`, 8029 strings / 8990 slots, decoded and re-encoded through
    `tbl/jp.tbl`; unchanged strings stay, changed ones move past 8 MiB and get repointed; graphics blocks kept as the
    original bytes). Default build is byte-identical (`tests/test_identity.py`, in the pre-commit check). Pointer
    writer proven by `build.py --relocate-all --poison` (all strings moved, old copies -> ア): romdiff with the write
    log clean, smoke ok, 70/70 scenes arrive, no ア left after adding the code literals (docs/re/text.md §Tables used
    by the build). LZ77 + Le: every block (1457 + 1564) roundtrips (`pytest -m slow tests/test_codecs.py`).
    `prove.py --qa DIR` keeps another ROM's shots apart; `tools/shotdiff.py` compares two shot dirs.
  - Phase 4 extract: `tools/extract.py` -> `script/<table>.json` (61 tables + `unused.json`; 8038 strings, 8990
    slots; fields id, slots, kind ff/fe, bytes, tail_of, jp, en, status, notes; never clobbers, `--force` keeps
    en/status/notes and lists ids whose jp changed). The build now reads `script/` (`rombuild.load_script(lang)`: `en`,
    or `jp` while empty) and is still byte-identical. `tests/test_script.py`: every `jp` re-encodes to the original
    bytes, files match a fresh dump, slots = `find_tables` slots, and `tools/textmap.py` explains every byte of
    0x464000-0x512000 (28 DATA ranges, 9 unused strings, 0 gaps). Every rejected pointer run was read: all data
    (docs/re/text.md §Coverage; 0x4A2E9C is sprite pieces, not names). Relocate+poison build smoke ok.
  - Phase 5 so far: dialogue font pinned (0x548E7C, a real VWF up to 8 px per glyph, docs/re/text.md §Font).
    English font `font/en_glyphs.txt` (A-Z, a-z, 0-9, punctuation; drawn here, MIT) + `tbl/en.tbl` (on top of jp.tbl;
    a-z and punctuation in D0-F6). `tools/font.py` (render / widths; `font_stage` copies the font past 8 MiB,
    repoints its 9 literals, writes advances to 0x4645B8). `rombuild.build` adds the font automatically once any
    `en` text exists (identity build unchanged). `tools/marker.py` + `build.py --marker [--full]`, `build.py --set
    ID=TEXT --out F` for stress lines. `tests/test_font.py`. Dialogue boxes show `ID: The quick brown fox...` in the
    new font, clean (shot: parts_shop). 0x4789EC is data (§Font).
    **Menu names solved (2026-11-17):** they are 8x8 sprites from Le block 0x5518A0 (codes 01-CF only, no VRAM room
    to grow), so English lowercase/punctuation moved to the hiragana codes 52-78 (D8 in decisions.md; en.tbl,
    en_glyphs.txt). `font.names_stage` redraws that charset (8x8 overrides `font/en_names_8x8.txt`) and repoints its
    29 pointers; the build runs it after `font_stage`; `tests/test_font.py::test_names_stage_writes`. Item list,
    shop list and robattle names show English in the marker build (`work/qa/scenes_marker2`). Glyph torture line
    (all punctuation, double spaces) renders right in party_parts (`work/qa/stress/z.png`).
    Width gate (2026-11-17, session 2): `data/windows.json` now **measured** for dialogue 208 px x 2 lines (zoomed
    `--full` shot, work/qa/enc_full_z.png), battle messages (same box), item list 86 px/18 B, part names 79 px/**10 B**
    (the shop detail screen goes black with 18 bytes), Medabot names 79/10, tutorial topics 148/18, credits 131/18,
    `name_box_10` 79/10 (medals, skill types, actions, terrain, character names). `{var:00}` (player name) = 80 px
    (10-cell buffer). `build.py --marker --full` now turns FE names into rulers (id + W/M, 8 px each, to the
    variant's byte cap: a longer ruler overflows 10-byte name buffers and breaks warps). **`tools/lint.py`** (in
    `tools/check.py`, `tests/test_lint.py`) checks `en` against windows.json: FE px + bytes, FF word wrap simulated
    per page; `--all` lints the marker text as a self-test. `tools/findtext.py WORD..`: a word in table encoding /
    SJIS in the ROM (no hit = graphics).
    Sorted as **graphics** (not in the ROM as text): bottom hint lines (…ならびかえ, …しょうさいがめんへ, …アイテムを
    つかう, メダルを せんたく), shop column headers (パーツめい, ねだん), party_parts column header, parts-detail stat
    labels. The robattle_intro info box squiggle is the name sliding in (same in the original).
    New tools: `tools/unpack_blocks.py OUTDIR` (every LZ77/Le block, for vramfind.py), `tools/debug/namefields.py
    SCENE..` (sprite name fields' x ranges from a savestate).
  **Phase 5 finished (2026-11-17, session 3):**
    - Width gate complete: `names_default` is gone. 46EDA0 = `battle_menu` (68 px/10 B, the bottom-right box of
      the robattle command menu), 46F0BC = `battle_status_box` (80/10, the teal box in the parts picker), 46A6F0 leg
      types = `name_box_10` (parts_legs_detail). 466688 attack names, 469450 model codes, 46A508 weapon kinds and
      470B08 part slots = `var_piece` (19 bytes, 100 px): code strcpy's them into the F9 01-04 piece buffers
      (0x030005C6 + 20*n) for battle lines such as うつこうどう レーザー!. `{var:01}`-`{var:04}` are linted at 100 px.
      `lint.py`: 0 warnings (no guessed variant left). Evidence shots in `work/qa/wg/`.
    - The tile-map renderer 0x08062ABC is link-cable code; the parts-trade name draws in the English charset,
      centred, 10 bytes whole (docs/re/text.md §Font, "Resolved").
    - Marker map tour (`maptour.py build/marker.gba --jobs 1 --qa work/qa/maps_marker`, new `--qa`): 141/141 arrive;
      vs the original (`shotdiff.py work/qa/maps/shots work/qa/maps_marker/shots`) only maps 1, 17, 21 differ by
      text (arrival dialogue shows ids), the rest are animation timing. No Japanese text left on any map.
    - `warp.lua`: player name poked at 0x03001D54 (`PNAME`, default "Ikki"), so {var:00} looks real in QA; scene
      key `wait={..., stopmash=true, press=".."}`; new scenes robattle_menu, robattle_parts, robattle_detail,
      robattle_menutour, parts_owned, parts_owned_detail, parts_legs_detail (not yet in `work/states/`: run
      `prove.py --jobs 1 --only ...` when phase 8 needs their states).
- **Next (phase 8, `references/emulator-qa.md`, `references/graphics.md`):** rerun the English scene proof (above,
  13/70 done) and `shotdiff.py` vs `work/qa/scenes/shots` for overflow / garbled boxes; route tours with sheets and
  visual-QA verdicts (`qa_gate.py`); textcover; graphics redraws. Phase 9 needs `docs/polish.md` ticked (incl. the
  Oro Captain/Leader drift found in phase 7) and `docs/style-reference.md` before the story pass (D13).
  Japanese left, all graphics (phase 8): parts-shop options (パーツを かう / うる / もどる), name-entry grid,
     money "円" glyph, menu tabs and headers (あたま etc. in the parts list), bottom hint lines, column headers.
     `jp_left.py --gba-ptrs` is noise here; the textmap coverage proof is the real check.
  Run **one emulator job at a time** (`--jobs 1`): other projects share this machine's memory.
- **Debug-tool gaps (not blocking; grow the list when phase 8 needs them):**
  1. Story robattles start from NPC talk (dispatcher near 0x08055B44, action 0x20 -> scene switch case 0x20); who
     writes the team id +0x942 per NPC is not traced. Scenes set the team id directly, which gives the same screens.
  2. Medaforce / special attacks per family: the gauge address is not found (battle records 0x03000680 ours,
     ~0x03000900 enemy). Needed for phase 8 battle-text QA.
  3. Story flags (nibble array 0x030048B0, `1F hh ll` sets flag hhll) and the map event-group selection
     (0x08056370) are not mapped; `EVENT=n` plays any event's text directly, which covers the dialogue.
  4. Graphics survey rows G18, G19, G24, G28-G30: match them to screens with `vramfind.py` over the scene and map
     tour shots when the graphics work starts.
  5. Link battle / link trade screens beyond `parts_trade`: not looked at.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
- **Notes for later phases:** Phase 5: try the existing
  VWF (redraw glyphs, lowercase in D0-EF, new widths) before writing one; the main dialogue font address is not pinned
  yet (0x54FEA0 is an alternate italic Latin font). Two menu kana fonts are graphics (G16 0x5518A0, G30 0x72F06C).
  Item 1 is named "ダミー" (a dummy entry in the game).
- **States:** `work/states/<scene>.mss` from `prove.py` (regenerate after engine/font/graphics changes); older
  `name_entry.mss`, `room_before_dialogue.mss`, `field_home_2f.mss` came from mash runs. Mesen timing varies run to
  run: wait on RAM flags (warp.lua does), not frames.
