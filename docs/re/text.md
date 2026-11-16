# Text engine: encoding, control codes, pointer tables

Dump: see `rom.sha1`. Offsets are ROM file offsets (CPU address = 0x08000000 + offset).

## Encoding (verified)

One byte per character, no kanji in the game (kana-only children's RPG). Table: `tbl/jp.tbl`.

- **verified** by probe ROMs (`tools/probe_codes.py`): the intro line 「したにおりていらっしゃい」 at 0x50A0D0 was overwritten
  with runs of 12 consecutive codes and shot in the dialogue box from state `work/qa/run4/s002700.mss` (frame 178,
  A-mash every 60). Every code 01-CF was read off the screen. Also cross-checked by decoding the first intro strings
  (きょうは しゅうぎょうしきが..., なんだ パソコン つきっぱなしだったのか) and the relative-search hit at 0x50A0D0.

| Codes | Characters |
|---|---|
| 00 | space |
| 01-2E | ア-ン, gojuon order incl. ヲ (ア=01, ヤ=24 ユ=25 ヨ=26, ワ=2C ヲ=2D ン=2E) |
| 2F-37 | ァィゥェォッャュョ |
| 38-4B | ガギグゲゴザジズゼゾダヂヅデドバビブベボ |
| 4C-50 | パピプペポ; 51 = ヴ |
| 52-7F | あ-ん (same order as katakana) |
| 80-88 | ぁぃぅぇぉっゃゅょ |
| 89-9C | が-ぼ; 9D-A1 ぱ-ぽ |
| A2-BB | A-Z (capitals only: **the font has no lowercase**) |
| BC-C5 | ー ・ ♥ ／ ？ ！ 〜 「 」 円 (C5 looks like 円 at 4x zoom: **guess** for the exact glyph) |
| C6-CF | 0-9 |
| D0-EF | not glyphs: drawn as garbage tiles (D0, D2-D3 seem to eat following bytes: possible control codes, unproven) |

The dialogue font is a fixed-width 8 px cell font (by eye from the probe shots; width per glyph to be measured in
phase 5). It is not stored as Shift-JIS anywhere: `jp_left.py --sjis` is useless here; use `--tbl tbl/jp.tbl`.

## Control codes (guess: argument counts from the decoded script; phase 4's roundtrip test must confirm)

| Code | Args | Meaning (evidence) |
|---|---|---|
| FF xx | 1 | end of string; xx is 00 (5695x), 04 (554x), 02 (251x), FF (270x), others rare. 04 seems to mean "close box and continue the event"; FF ends name/list entries. Pointers point just past the arg byte. |
| FD | 0 | newline (2-line box) |
| FC | 0 | new page (wait for A, clear box) |
| FB a b c | 3 | speaker / portrait: `FB 01 00 00` = player side, `FB 00 0B 00` = mother... (face id) |
| F9 n | 1 | insert variable: F9 00 = player name (verified: shows the entered name), F9 01 = item/medal/number in system messages |
| FA n | 1 | seen in battle messages (`メダフォースを ためた！ FA 50`): wait or sound, unproven |
| FE | ? | 318 hits, mostly inside non-text data at 0x464A00-0x465FFF; rare in dialogue |

## Pointer tables (verified for 0x50C284)

Plain GBA pointers (u32 LE, 0x08000000 | offset), one table per block, stored **after** the strings it points to.
Example: table 0x50C284 (53 entries) -> strings 0x509FC8-0x50A9C9 (the intro at home; entry 0x50C2A0 -> 0x50A0C9
= `FB 00 0B 00 F9 00 FD したにおりていらっしゃい FF 00`).

A whole-ROM sweep for u32 pointers into 0x464000-0x511000 whose target follows an `FF xx` found **7311 string starts in
177 tables of >= 3 entries** (683 runs in all; the short runs need checking in phase 4). 7256 decode with no unknown
byte; the rest start in non-text data at 0x464A00-0x465FFF (structured records, FE-heavy) and must be excluded.

Code that reads it: the text reader reads the script by byte at runtime from ROM (no compression, no RAM copy):
`gba_romreads.lua` over the intro shows 0x08041190 / 0x08041360-0x08041548 reading 0x50A042-0x50A0B5 while the box
types (**verified** as reads; the exact draw routine entry is still to be pinned in phase 5).

### Text ranges (from the sweep; to be finalised in phase 4)

| Range | Contents (sampled) |
|---|---|
| 0x464A00-0x465FFF | mixed: structured non-text records with a few string tables |
| 0x466000-0x4702FF | battle messages (0x4702F4 table: メダフォースを ためた！, しょうしゃ...), robattle taunts (0x46D59C, 0x46E124) |
| 0x478300-0x479000 | small tables |
| 0x4AD5F0-0x4B7A6A | signs and books (0x4B50D0, 0x4B54F8), system messages (0x4B76B4: 「F9」メダルを てにいれた), two odd tables 0x4B6478/0x4B6658 that decode as short katakana noise (maybe name indices or another encoding: **open**) |
| 0x4B7A6A-0x4F3C88 | NPC and event dialogue, master tables 0x4F3C88-0x4F86BC |
| 0x4FC000-0x510208 | more scene dialogue (tables 0x50A9DC-0x50C274: intro, town), tutorials (0x510128: ティンペット, パーツ) |

The menu words みぎうで, セーブ, アイテム, メダロッチ appear only inside this region, so menus probably share the table.

### Not found yet (phase 2/4 must locate)

- Robot model, part and medal **names**: メタビー/ロクショウ appear only 3-4 times, all in dialogue; ヘッドシザース and
  メタルビートル do not occur in this encoding. They may be in a second table (the 0x4B6478/0x4B6658 tables?), drawn as
  graphics, or in another encoding. Find them by hooking the menu draw once the debug tool reaches the parts screen.
- Name-entry keyboard: kana grid looks font-drawn (check in phase 5).
