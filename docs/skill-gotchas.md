# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

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
