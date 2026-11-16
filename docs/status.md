# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (phase 1 done). Last build: none yet.
- **Done:**
  - Step 0: MesenCE 2.2.1 in `tools/mesen/` (+ GBA BIOS), guard hook proven (canary blocked), pre-commit runs
    `tools/check.py` and rejects a failing test, `rom.sha1` pinned, boot route reaches the title menu.
  - Phase 1 recon: `docs/re/` (prior work, ROM map, text encoding + control codes, 7311 FF strings + 1129 FE names,
    the game's own VWF, graphics survey G1-G33). "Le" and LZ77 codecs tested.
  - Phase 2 so far (`docs/re/debug.md`): main mode 0x0300177C / sub 0x03001D6C / step 0x03001364 and what every
    mode+sub shows; map id 0x03004DC6, door-warp table 0x084B6248 (133 maps reachable from home), field idle test,
    random-encounter switch. `tools/debug/warp.lua` boots cold (new game, A through the intro, ~f2340), then warps by
    map (register rewrite inside the game's own door routine) or by mode switch; `tools/debug/scenes.txt` has 32
    scenes, all proven from a cold boot with a correct shot (`work/qa/scenes/sheet*.png`, 2026-11-17) (field maps, Start menu, Medawatch, Medabot/medal/parts lists, items, save, shop, trade, town map, name
    entry, options, game over, save-corrupt, sound test, 4 minigames, Medarot Weekly, medal cutscene, logo, opening,
    title, encyclopedia, credits); `tools/debug/prove.py` proves them all from a cold boot and writes
    `work/states/<scene>.mss`. RE helpers: `tools/re_stores.py`, `tools/re_scene_cases.py`, `tools/debug/explore_modes.py`.
- **Next (phase 2, `references/emulator-qa.md` §Debug tool):**
  1. **Party / inventory:** the player has no Medabot after the intro, so `robattle_intro` (mode 0 sub 6) dims and
     stops, and the Medabot/medal/parts lists are empty. Find the party, medal and parts inventory in RAM (the save
     screen 2/5 shows the counts; the Medabot list 0/3 reads them) and add a `FAST` option that fills them; then a
     working `robattle` scene (random: 0x030051F5 = 0; story: 1 plus the opponent id) through to the attack messages,
     win and loss.
  2. **Story flags:** the nibble array at 0x030048B0 (+0, ~0x500 bytes; reader 0x08058260) and the event command
     interpreter around 0x08055B44 (command 0x20 = story robattle). Needed for chapter entries, the pre-credits
     ending (credits alone are 4/6) and the Start menu, which is locked in the early story (1 opens it anyway).
  3. **Map tour:** one shot per map id 0-~140 (`MAP=n`, entry tile from the door table) to look for area banners
     and to read the "?" rows of the graphics survey (G18, G19, G24, G28-G30); match G1-G11 to blocks.
  4. Submenus by `press=` (help text under the Start menu "せつめい", shop sell list, save yes/no), then the
     done-when: every entry reached from a cold boot with a shot (`prove.py` exit 0).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
- **Notes for later phases:** phase 4 extractor must take both string kinds (FF xx and FE). Phase 5: try the existing
  VWF (redraw glyphs, lowercase in D0-EF, new widths) before writing one; the main dialogue font address is not pinned
  yet (0x54FEA0 is an alternate italic Latin font). Two menu kana fonts are graphics (G16 0x5518A0, G30 0x72F06C).
- **States:** `work/states/<scene>.mss` from `prove.py` (regenerate after engine/font/graphics changes); older
  `name_entry.mss`, `room_before_dialogue.mss`, `field_home_2f.mss` came from mash runs. Mesen timing varies run to
  run: wait on RAM flags (warp.lua does), not frames.
