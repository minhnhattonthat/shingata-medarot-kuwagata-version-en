# Shingata Medarot: Kuwagata Version (GBA) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/medarot_kuwagata_en.gba (checks the dump against `rom.sha1` first; written in phase 3)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this; hooks path: `git config core.hooksPath tools/hooks`)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/medarot_kuwagata_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/medarot_kuwagata_en.gba --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 900 --sheet` (scenes: `tools/debug/scenes.txt`, RAM map `docs/re/debug.md`; never ask the user to play to a scene)
- Prove/regen states: `python -X utf8 tools/debug/prove.py --jobs 2` (every scene from a cold boot -> `work/states/<scene>.mss`, sheet `work/qa/scenes/sheet.png`; ~560 MB per job). Ad hoc: `--var MAP=n`, `--var EVENT=0x1D2` (any story event), `--var RAWMODE=n --var RAWSUB=n`
- Map tour: `python -X utf8 tools/debug/maptour.py --jobs 2` (one shot per map id 0-140 -> `work/qa/maps/sheet*.png`)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Shingata Medarot - Kuwagata Version (Japan).gba` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own MesenCE in `tools/mesen/` (release 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored; needs `tools/mesen/Firmware/gba_bios.bin`, SHA-1 300c20df...). Savestates: `work/states/`.
- Text: `script/`. Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- The ROM file name has spaces: quote it. From Git Bash give Python `C:/...` paths, never `/c/...`.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
