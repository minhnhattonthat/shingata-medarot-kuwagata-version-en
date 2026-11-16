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
