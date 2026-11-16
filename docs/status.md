# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- Review fix pass (b017-b019): expanded Select Corps Headquarters in 4BD9ED and 4BDCCB;
  both Important findings accepted, Minor findings untouched. `batches.py check b017 b018 b019`: all OK.

- **Phase:** 6. Translate: in progress (2026-11-17, session 1 of phase 6). Pipeline: `tools/batches.py split`
  made b001-b084 (`work/tl/bNNN.tsv`, identical JP+box batched once, merge copies to duplicates); translators and
  reviewers run through `codex exec` (`tools/codex_tl.py`, `tools/tl_pipeline.py "b014 b015 b016" ...` =
  translate -> pairs -> independent review `work/tl/review/<first>.review.md` -> fix pass -> check; status file
  `work/tl/review/<first>.status` says READY to merge). The controller merges (`batches.py merge bNNN.. --overwrite`)
  so lanes never write `script/` at once. **Merged (4109 of 8038 strings in `en`, check 0 problems, lint 0, build
  smoke ok sha1 5a387ba0):** b001-b007 (names, unreviewed), fix01 (ていし -> Halt), b014-b025 (translated,
  reviewed, fixed), and **merged but NOT yet reviewed:** b008 b009 b011 b012 b070-b081 b083 (run
  `tl_pipeline.py` on them: it skips translation, reviews, fixes; then merge --overwrite).
  **Not done:** b010 b013 b026-b028 b030-b069 b084 (no output yet); b029 (partial, 16 check problems) and b082
  (1 problem): re-run tl_pipeline on their groups. Suggested groups: "b008 b009 b010" "b011 b012 b013"
  "b026 b027 b028" "b029 b030 b031" ... "b068 b069" "b070 b071 b072" ... "b082 b083 b084".
  **Memory:** on 2026-11-17 seven parallel lanes (7 codex sessions + Claude Code) got all background jobs killed
  for low system memory. Run at most 2-3 lanes at once. Docs: `docs/translator-brief.md`, `docs/reviewer-brief.md`, `docs/synopsis.md` (two casts: Shingata's
  Gamma story in 50A9D8/4B50CC/46D598/46E0F0/510124; retained Medarot 2 Core Ikki story in the 4F tables).
  Last build: 2026-11-17
  `build/medarot_kuwagata_en.gba` from `script/`, sha1 573e980d... = the original (identity), smoke ok.
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
- **Next (phase 6, `references/translation.md`):**
  1. Fill `glossary.md` (characters from 46E60C, Medabot names 468308, medals 465B8C, parts 468A00, places,
     skill types / actions) using the official Medabots English names (D2), then dispatch translator agents in
     batches by table (`script/<table>.json`, field `en`), budgets from `data/windows.json` and `tools/lint.py`.
     Orca workers can't nest agents: translate in this session (or `codex exec`) and do the reviewer pass as a
     fresh read-only pass. Battle pieces sharing a line (action + weapon kind) keep to ~70 px each.
  2. Japanese left, all graphics (phase 8): parts-shop options (パーツを かう / うる / もどる), name-entry grid,
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
