# Shingata Medarot: Kuwagata Version English translation

Unofficial English fan translation of **Shingata Medarot: Kuwagata Version** (真型メダロット クワガタバージョン, Game Boy
Advance, Imagineer, 2004), and of its twin **Kabuto Version** (カブトバージョン): the source text and tools that build
both patches.

**Just want to play?** Download the patch for your version from [Releases](../../releases) and follow its README. Each
patch only fits its own version. This repository holds no game data you can play; you need your own dump of the
Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue and story (both the Shingata story and the retained Ikki story), signs and books | Translated |
| Menus, items, parts, Medals, skills, battle messages, tutorials, system messages | Translated |
| Graphics with text (menu tabs, headers, shop options, minigame banners, money symbol) | Translated |
| Title logo 真型 メダロット | Redrawn in English (SHIN GATA MEDAROT) in the original's style |
| Name entry | Translated: English letter grid (ABC / abc / 123) |
| Staff credits | Translated |

Known issues: none known; see [Issues](../../issues). Two encyclopedia topic titles are shortened to fit an 18-byte
row ("Speed & Mobility", "MedalPart Affinity").

## Base ROM

| | |
|---|---|
| No-Intro name | Shingata Medarot - Kuwagata Version (Japan) |
| Size | 8,388,608 bytes (8 MiB) |
| CRC32 | 0FD35628 |
| MD5 | d1415b84b039a978bdb920f917959779 |
| SHA-1 | 573e980dffdee50d53b6f2a79d1db2d650731558 |
| Patched | 9,437,184 bytes (the English text lives in an added 1 MiB), CRC32 0807CCF7 |

Kabuto Version patch:

| | |
|---|---|
| No-Intro name | Shingata Medarot - Kabuto Version (Japan) |
| Size | 8,388,608 bytes (8 MiB) |
| CRC32 | 54AF534D |
| MD5 | 7ab12db7382122998aaf2756dcbac498 |
| SHA-1 | c14e7612698342ccd495e4aef764d4083c5a4765 |
| Patched | 9,437,184 bytes, CRC32 B6FA4B96 |

Tested in MesenCE 2.2.1 with the official GBA BIOS. Start from a cold boot: emulator savestates made on the Japanese game
carry its old text and font code and will show garbled text.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `script_kabuto/` | The Kabuto Version's string tables, linked to `script/`, and its own lines. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, QA, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/shingata-medarot-kuwagata-version-en
cd shingata-medarot-kuwagata-version-en
# copy your dump to: rom/Shingata Medarot - Kuwagata Version (Japan).gba
#   (8388608 bytes, SHA-1 573e980dffdee50d53b6f2a79d1db2d650731558; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/medarot_kuwagata_en.gba
python -X utf8 tools/check.py                          # tests + text lint
# Kabuto Version: copy your dump to rom/Shingata Medarot - Kabuto Version (Japan).gba (SHA-1 in rom_kabuto.sha1)
python -X utf8 build.py --version kabuto               # -> build/medarot_kabuto_en.gba
```

The Kabuto build uses the same sources: `script_kabuto/` lists the Kabuto ROM's strings, each linked to the identical
Kuwagata string in `script/` (so one fix reaches both), plus the 11 lines only the Kabuto Version has.

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Imagineer's and is included only so
the translation can be checked against it. Shingata Medarot is (c) Imagineer (original concept (c) Imagineer and
Natsume); this project is not affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic, and OpenAI Codex). Corrections are very
welcome.
