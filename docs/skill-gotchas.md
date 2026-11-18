# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/emulator-qa.md: a debug Lua's relative path (warp.lua's `../debug/scenes.txt`) resolves against the emulator's working dir, which moves with emu.py's `--out` depth: a tour under work/qa/kabuto/... failed every scene with "unknown SCENE". Pass data files to Lua as absolute paths through `--var`.
- references/pipeline.md (second version of a game): two regional/paired versions (Medarot Kabuto/Kuwagata) share 93% of bytes at small shifts; align them (16-byte unique anchors -> segments, tools/romalign.py), route every hard-coded offset through one map function, and link the second script to the first by identical bytes: only 11 of 8029 strings needed new text.

- references/graphics.md §Survey: a fixed 32-column sheet scrambles row-major images; pick each block's width by the
  seam between tile i and i+w, but narrow widths score better on any data, so require a clear margin (25%) over 32.
- references/graphics.md §Survey: `codex exec -s read-only -i sheet.png ... -o out.tsv` reviews ~10 sheets in ~75 s and
  is a workable independent reviewer when no subagent can be started (repo tool: `tools/sweep_review.py`).
- references/pipeline.md §Recon: a pointer sweep that only accepts targets after `FF xx` missed every name list; this
  game ends names with a 1-byte FE, so also sweep for targets preceded by any terminator byte.
- references/emulator-qa.md §Debug tool: Mesen GBA Lua `emu.setState({["cpu.r3"]=v})` from an `L.on_exec` hook sets
  the register before that instruction runs; rewriting the loads of the game's own door-warp routine gave a warp to
  any map with no ROM patch. Writing the main-mode globals from the idle field reached every menu/minigame screen.
- references/emulator-qa.md §Debug tool: "field idle" needs a player-control flag, not just the field substate: the
  intro left the substate idle while dialogue ran, and a warp there skipped half the intro.
- references/platform-gba.md: Mesen 2.2.1 Lua write callbacks on 0x040000D4-DF (DMA3) never fired while a GBA game saved to EEPROM; find the saved RAM instead with a read trace of the save step (BIOS CpuSet pc 0xB8E read the whole block).
- references/emulator-qa.md §Debug tool: a robattle started by writing the main mode crashed in RAM code the field's encounter path installs; trigger battles through the game's own encounter check (pin the step counter and walk) rather than the mode switch.
  CORRECTED session 4: the crash was a missing opponent team on that map (garbage count byte, a sprite loop overran
  into the RAM code); with a valid team id the mode switch works. Before blaming the emulator, check every table
  the battle setup reads is valid for the map you warped to.
- references/emulator-qa.md §Debug tool: running the game's own story events from Lua (write the event index/pc
  and "running" flag the tile trigger writes, let the interpreter dispatch) gave the party and inventory with
  correct formats, where poking guessed bytes and "fill with 1" tests showed nothing. Find the give-item/part/
  medal commands in the event handler tables and start an event at the offset after its condition.
- references/emulator-qa.md §Debug tool: a "list is empty" screen that reads none of the save block can still
  read an inventory elsewhere: trace the writer of the first displayed string (name buffer) back with a write
  hook logging lr, then read the caller; that found the medal list in two runs.
- references/emulator-qa.md §Debug tool: deep battle screens arrive at varying frames; a scene key that waits on
  the game's mode/sub/step (warp.lua `wait=`) proves them reliably where a fixed hold did not.
- references/emulator-qa.md §Debug tool: a value shown on screen (money) was found fastest by write-hooking the
  screen's text buffer, reading the number-to-text routine's caller, then the ldr just before the call; full-RAM
  read traces of the menu showed only the already-formatted string.
- references/pipeline.md §Identity: for an in-place-read script (GBA, no compression), a byte-identical build is
  trivial; a "relocate every string + overwrite the old copies with one visible glyph" stress build, toured with the
  debug tool, proved the pointer writer and found a code literal pointer the table sweep missed (parts shop clerk).
- references/emulator-qa.md: comparing warp-scene shots of two builds pixel by pixel over-reports: half the scenes
  differed only in animated backgrounds / fades (arrival frame shifts), so diffs need a zoomed look, not a threshold.
- references/emulator-qa.md: a project prove/tour driver should copy each scene's shot into shots/ as soon as it arrives, not at the end; a run reaped for low memory otherwise leaves shots/ (and the shotdiff) missing every scene it did finish.
- references/graphics.md: redrawing a label by appending new tiles to a BG tile block can run past the VRAM room the game gives that block (next block loaded right after it): offline previews look fine, the game shows garbage. Reuse tiles only the old label used, and always confirm with an in-game shot.
- references/emulator-qa.md: qa_gate verdicts with `codex exec -s read-only`: the reviewer cannot write its verdict file; ask it to end its answer with the id<TAB>verdict<TAB>note lines, capture with -o, and save those lines as the chunk tsv.
- references/graphics.md: an erase that copies a column of the original (`copy_col`) must name a column of clean fill for the whole rect height; one column inside a Japanese glyph smeared the glyph's white/red pixels across the box as stripes in-game (offline it looked like a styling difference). Print the box with `screenfind.py --grid` and pick the column from it.
- references/emulator-qa.md: textcover gaps for dialogue tables can be closed with a sweep probe instead of playing to every NPC: hook the game's "start dialogue(ptr)" routine and swap r0 for the next unshown string (sticky per original pointer: some screens restart the same string every frame), while the event tour runs; name-list strings (no box-closing terminator) can't go through the runner.
- references/emulator-qa.md: textcover logs are build addresses, so any text edit that changes a string's length shifts every later string and scrambles coverage (6901 shown became 6923 shown / 7 failing). Keep the strings.tsv of the build the sweep ran on and map old address -> id -> new address (`tools/coverremap.py`) instead of re-sweeping after text-only edits.
- scripts/jp_left.py: `--slots` reaches from each target to the next NUL; games that end strings with FE/FF (Medarot GBA) reach into old Japanese after in-place strings. Pass "SLOT TARGET" lines from the build's strings list and list those runs in `--known`; an option for the terminator byte(s) would make this exact. English that reuses kana codes needs a jp_left .tbl without those codes.
- references/translation.md: batch lint "honorific" rule matched じーさん / かーちゃん (katakana-class ー before さん/ちゃん): kinship words, not names; exclude hiragana+ー before the honorific.
- references/pipeline.md: a per-row tile budget can be per byte, not per px: a 21-byte, 104 px encyclopedia title (row measured to 148 px) spilled its tail into the row above. Measure a longer string's bytes in-game before raising a byte cap even when px fit.
