# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (phases 1-4 done). Last build: 2026-11-17
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
- **Next (phase 5, `references/pipeline.md` §Marker, `references/platform-gba.md`):**
  1. **Tile-map name renderer** (docs/re/text.md §Font, "Second renderer"): list/menu names are drawn as fixed 8 px
     tiles from a charset in VRAM (0x08062ABC, code-1 split by 26). Pin the charset's source (vramfind.py on a VRAM
     dump of `items_owned` / `medal_list`; candidates G16 0x5518A0, data at 0x54CCBC), add English cells for D0-F6
     (the charset must grow past code 0xCF), rebuild, recheck `items_owned` (marker shows garbage tiles over the
     list there now) and `party_parts`, `parts_shop_list1`, `robattle` name fields. Also check other renderers that
     sum `width[]` (literals of 0x084645B8 at 0x0804228C-0x08042704, 0x08063198, 0x08063B50).
  2. Japanese left in the marker tour, sort into text vs graphics: bottom hint lines (…しょうさいがめんへ, …けってい,
     …アイテムを つかう, カーソルで メダルを せんたく, …ならびかえ), shop column headers (パーツめい, しゅるい, ねだん),
     the parts-shop menu options (パーツを かう / うる / もどる), name-entry grid, money "円" glyph in the menu font,
     menu tabs (graphics G-rows). Run `jp_left.py build/marker.gba --tbl tbl/jp.tbl --gba-ptrs` for text the
     extractor missed. Battle messages concatenate pieces (`robattle_attack` shows several ids on one line): fine.
  3. Width gate: measure each box variant in-game (dialogue with/without face: 208 px wrap seen, the 2-line box;
     list fields in cells; shop; battle messages; credits; encyclopedia pages), record budgets per table in
     `windows.json` (measured / guess + shot), and boot a glyph torture line with `build.py --set`.
  4. Map tour (`maptour.py`) on the marker build for signs / NPC text ids.
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
