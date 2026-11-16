# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool (phase 1 done). Last build: none yet.
- **Done:**
  - Step 0: MesenCE 2.2.1 in `tools/mesen/` (+ GBA BIOS), guard hook proven (canary blocked), pre-commit runs
    `tools/check.py` and rejects a failing test, `rom.sha1` pinned, boot route reaches the title menu.
  - Phase 1 recon: prior work (`docs/re/prior-work.md`), header/map/compression/free space (`docs/re/rom.md`), text
    encoding verified for every code 01-CF, control-code argument counts verified from the dispatcher at 0x080411AC,
    7311 FF-terminated strings + 1129 FE-terminated names (parts, medals, Medabots, characters, items, staff
    credits) in 17 more tables, and the game's own VWF (width table 0x4645B8, word wrap at 208 px, D0-EF free glyph
    slots) in `docs/re/text.md`. "Le" and LZ77 codecs tested. Graphics survey G1-G33 (`docs/re/graphics.md`): tour +
    static sweep with per-block widths (`tools/gfx_sweep.py`), reviewed by codex (`tools/sweep_review.py`); gba8 has
    no Japanese.
- **Next (phase 2, `references/emulator-qa.md` §Debug tool):**
  1. Find the scene/map id and story-flag variables in RAM (`ramsearch.py`, `watch.lua`) from the existing states.
  2. Write `tools/debug/warp.lua` + `tools/debug/scenes.txt` (field menu, Medawatch/parts/medal screens, robattle,
     shop, save, password screen, game over, ending, credits, area banners) and prove each from a cold boot with a shot.
  3. Use the tour to read the "?" rows of the graphics survey (G18, G19, G24, G28-G30) and match G1-G11 to blocks.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
- **Notes for later phases:** phase 4 extractor must take both string kinds (FF xx and FE). Phase 5: try the existing
  VWF (redraw glyphs, lowercase in D0-EF, new widths) before writing one; the main dialogue font address is not pinned
  yet (0x54FEA0 is an alternate italic Latin font). Two menu kana fonts are graphics (G16 0x5518A0, G30 0x72F06C).
- **States:** `work/states/name_entry.mss`, `room_before_dialogue.mss`, `field_home_2f.mss` (made from mash runs on the
  original ROM; regenerate from the debug tool in phase 2). Mesen timing varies run to run: wait on screens, not frames.
