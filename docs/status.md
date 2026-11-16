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
  - Session 3 (`docs/re/debug.md` §Events, §Story walk, §Save block): event script format decoded (688 events,
    `tools/debug/evdump.py`), map event lists 0x0847DF80, `tools/debug/story.py` (play + mash + dialogue text log),
    `tools/debug/ramdiff.py`, `tools/lua/{evtrace,mash_idle,blockdiff,dumpblock}.lua`. The story was walked to the
    first medal (event 0x1CB, park map 3); the next step (deliver it to the M-PK) is not found yet. Parts shop works
    with a shop id (0x03001D3C = 1 or 2) but money is 0 and lives outside the save block.
  - Session 4 (`docs/re/debug.md` §Inventory and party, §Robattle teams, §Robattle): medals 0x03000BE0, Medabots
    0x03001790, items 0x03001D80, parts 0x03003DF0; event give-commands (10 part, 11 medal, 13 item, 35 Medabot).
    `warp.lua` runs story events through the game's interpreter (`events=`), waits on mode/sub/step (`wait=`) and
    asserts RAM on arrival (`expect=`, NOTARRIVED fails prove.py). The robattle "crash" was a missing team on
    town maps, not the emulator: story path (+0x945=1, team id +0x942) works. New scenes: party_setup/medals/parts,
    robattle_prep, robattle, robattle_attack, robattle_win (armor pinned), robattle_loss, cutscene_01..10 (all 11
    story comic cutscenes via 0x03005B29). Probe `tools/lua/writes.lua` (write hook with lr).
    Proof state: the old 32 scenes + party_*, robattle_prep, robattle, cutscene_01..10 ARRIVED from cold boots;
    robattle_win ARRIVED in a single run (f12813, spoils screen). A full `prove.py --jobs 4` was killed for low
    memory (each Mesen ~560 MB; the robattle scenes run ~13000 frames): **first thing next session, run
    `prove.py --jobs 2`** and fix robattle_attack / robattle_loss if their `wait=` doesn't hold.
- **Next (phase 2, `references/emulator-qa.md` §Debug tool):**
  1. **Money and shops with stock:** money is still unknown (shops show 0円). Trace reads in the Start menu
     (mode 0 sub 1, which shows money) with `reads_in_mode.lua`, or find the event command that pays (grep
     handlers in 0x0847B618 for adds to a u32). Then `parts_shop_buy` with ids 1/2, sell list and a purchase.
  2. **Story flags / chapters:** nibble array 0x030048B0 (reader 0x08058260; `1F hh ll` sets flag hhll). Map
     event groups in 0x0847DF80 pick by flags (code near 0x08056370). Chapter entries: list the story events
     that start story robattles (cmd `20`, 94 uses) and the cutscene events (75 xx: 0x1CD, 0x17E, 0x192, 0x146,
     0x19C, 0x1DE, 0x228, 0x26F), run them with `events=` after setting their preceding flags. Pre-credits
     ending: event 0x26F (cutscene 10, then commands 6E/78/36/39) is the candidate; credits alone are 4/6.
  3. **More battle types:** story robattle with a full 3-Medabot party (give parts/medals with `events=` or
     pokes, team ids from 0x0846AC18), Medaforce/special attacks per family, a random encounter on a map with
     teams (maps 30+), link battle screens if any.
  4. **Map tour:** one shot per map id 0-~140 (`MAP=n`) for area banners and the "?" rows of the graphics
     survey (G18, G19, G24, G28-G30). 5. Submenus by `press=` (Start menu help "せつめい", shop sell, save yes/no).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
- **Notes for later phases:** phase 4 extractor must take both string kinds (FF xx and FE). Phase 5: try the existing
  VWF (redraw glyphs, lowercase in D0-EF, new widths) before writing one; the main dialogue font address is not pinned
  yet (0x54FEA0 is an alternate italic Latin font). Two menu kana fonts are graphics (G16 0x5518A0, G30 0x72F06C).
- **States:** `work/states/<scene>.mss` from `prove.py` (regenerate after engine/font/graphics changes); older
  `name_entry.mss`, `room_before_dialogue.mss`, `field_home_2f.mss` came from mash runs. Mesen timing varies run to
  run: wait on RAM flags (warp.lua does), not frames.
