# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (Step 0 done). Last build: none yet.
- **Done:**
  - Step 0: MesenCE 2.2.1 in `tools/mesen/` (+ GBA BIOS), guard hook proven (canary blocked), pre-commit runs
    `tools/check.py` and rejects a failing test, `rom.sha1` pinned, boot route reaches the title menu.
  - Recon: prior work (`docs/re/prior-work.md`), header/map/compression (`docs/re/rom.md`), text encoding verified
    in-game for every code 01-CF, 7311 pointed strings in 0x464000-0x511000 (`docs/re/text.md`, `tbl/jp.tbl`),
    graphics-text tour of boot/title/options/name entry (`docs/re/graphics.md`).
  - "Le" codec reversed and verified (`tools/le.py`, all 1564 blocks decode; `tests/test_codecs.py`).
  - Static sweep tool `tools/gfx_sweep.py` renders all blocks with an index (167 sheets in `work/sweep/gba4`).
- **Next (to finish phase 1):**
  1. Fix the sweep's sheet widths (full-screen images are 30 tiles wide; see `docs/re/graphics.md`), add gba8/linear.
  2. Review the sweep sheets in a fresh read-only pass (`codex exec`, chunks of ~10 sheets) and list every Japanese
     cell in `docs/re/graphics.md`.
  3. Locate robot/part/medal name storage (not in the dialogue encoding outside the script; see text.md §Not found).
  4. Pin the control-code argument counts (FA, FB, FE, D0-D3) against the draw routine.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
- **States:** `work/states/name_entry.mss`, `room_before_dialogue.mss`, `field_home_2f.mss` (made from mash runs on the
  original ROM; regenerate from the debug tool in phase 2). Mesen timing varies run to run: wait on screens, not frames.
