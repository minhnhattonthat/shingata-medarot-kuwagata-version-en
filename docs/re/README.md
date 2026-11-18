# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| prior-work.md | earlier patches, official English names, related games | done |
| rom.md | header, map, save type, LZ77 and "Le" compression, free space | header verified; map partly guessed; LZ77 and Le codecs verified |
| text.md | encoding, control codes, pointer tables, name lists, VWF width table | encoding and control-code arg counts verified; name lists found |
| kabuto.md | Kabuto Version: offset map to Kuwagata, overrides, script overlay, what was checked | verified (tests/test_kabuto.py, warp tour) |
| graphics.md | graphics-text survey | tour of boot/title/name entry + reviewed static sweep (G1-G33); mid-game screens wait for the debug tool |

Recon helpers: `tools/lua/gba_romreads.lua` (per-PC ROM read ranges in a frame window), `tools/probe_codes.py`
(probe ROMs that show code runs in the intro box), `tools/lz77.py`, `tools/le.py`, `tools/gfx_sweep.py` (static
sheets) + `tools/sweep_review.py` (codex review of the sheets).
