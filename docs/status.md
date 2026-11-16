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
- **Next (phase 2, `references/emulator-qa.md` §Debug tool):**
  0. Rebuild the medal state first (`work/play/` is not in git): follow §Story walk with `story.py` from
     `work/states/home_2f.mss`, then turn it into a scene (`medal_found`) that `warp.lua` can reach (pokes of the
     flags it lists, or the walk as a route).
  1. **Party / inventory** (read `docs/re/debug.md` §Save block and §Robattle first: 2026-11-17 ruled out a lot).
     Two leads from session 3: (a) find which flags pick a map's event group in 0x0847DF80 (code near 0x08056370),
     then follow the story's own events (grep `work/re/events.txt` for the event that sets the flag after 0x1CB)
     to the first Medabot; (b) find money (shop read trace skipping EWRAM 0x02020000-0x0203FFFF), set it, buy
     parts at shop 1, and build a Medabot in the setup screen.
     The saved RAM is 0x030048B0-0x03005287, but the empty list screens read none of it and filling its zero
     ranges changes nothing. Robattles must start from a real encounter (pin 0x030051F1=1, 0x030051F3=0x20, walk:
     the raw mode write crashes in RAM code 0x03004220); that path reaches step 34 and goes black with no party.
     Next: play the opening story with `play.py` (mash A + walk out of the house) until the game hands over the first
     Medabot, saving a state just before; diff `ramdump.lua` dumps across that event (`ramsearch.py`), or trace the
     event interpreter (0x08055B44 area) for the give-Medabot/part command. Then a `FAST` option that fills the
     party, and a `robattle` scene from a real encounter through attacks, win and loss.
     Probes made this session: `tools/lua/reads_in_mode.lua` (reads by mode/sub/step, pc/addr filters),
     `fill.lua`, `pin.lua`, `modelog.lua` (mode changes, PCEVERY for hangs), `dma_eeprom.lua` (doesn't fire).
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
