# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (Step 0 done). Last build: none yet.
- **Done:**
  - Step 0: MesenCE 2.2.1 in `tools/mesen/` (+ GBA BIOS), guard hook proven (canary blocked), pre-commit runs
    `tools/check.py` and rejects a failing test, `rom.sha1` pinned, boot route reaches the title menu.
  - Recon: prior work (`docs/re/prior-work.md`), header/map/compression (`docs/re/rom.md`), text encoding verified
    in-game for every code 01-CF, 7311 pointed strings in 0x464000-0x511000 (`docs/re/text.md`, `tbl/jp.tbl`),
    graphics-text tour of boot/title/options/name entry (`docs/re/graphics.md`).
- **Next (to finish phase 1):**
  1. Reverse the "Le" decompressor (ROM 0x08000B42-0x08000DDC, header 0x080009E2-0x08000B04) into `tools/le.py`,
     roundtrip-test it.
  2. Static graphics sweep: render all LZ77 + Le blocks (gba4/gba8, linear too) into numbered sheets with an offset
     index; list every Japanese cell in `docs/re/graphics.md` (review sheets in a fresh read-only pass).
  3. Locate robot/part/medal name storage (not in the dialogue encoding outside the script; see text.md §Not found).
  4. Pin the control-code argument counts (FA, FB, FE, D0-D3) against the draw routine.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
- **States:** `work/states/name_entry.mss`, `room_before_dialogue.mss`, `field_home_2f.mss` (made from mash runs on the
  original ROM; regenerate from the debug tool in phase 2). Mesen timing varies run to run: wait on screens, not frames.
