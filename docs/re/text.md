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

## Control codes (argument counts **verified** from the dispatcher; meanings partly guessed)

Dialogue runner state is at IWRAM 0x03000520 (+8 = string base pointer, +0xC = u16 read offset, +0x14 = pen x in
px, +0x19/+0x1A = box state). The step routine at 0x08041180 reads the byte at base+offset; **any byte <= F7 is a glyph**
and F7-FF jump through the 9-entry table at 0x080411AC. Argument count = how far each handler moves +0xC (read from
the `adds r0,#n; strh r0,[rX,#0xc]` in each handler):

| Code | Args | Handler | Meaning (evidence) |
|---|---|---|---|
| F7 n | 1 | 0x0804121C -> 0x08041BFC (+2) | unknown; not seen in the script so far |
| F8 | 0 | 0x08041290 (+1) | unknown, reads state+0x27 (the alt-width-table flag) |
| F9 n | 1 | 0x080411D0 -> 0x0804170C, jump table on n (0-4) | insert variable: F9 00 = player name (verified in-game), F9 01 = item/medal/number |
| FA n | 1 | 0x08041208 -> 0x08041B64 (+2) | battle messages (`メダフォースを ためた！ FA 50`): wait n frames (guess) |
| FB a b c | 3 | 0x08041234 -> 0x08041310 (+4, reads p+1..p+3) | speaker / portrait: `FB 01 00 00` = player side, `FB 00 0B 00` = mother |
| FC | 0 | 0x0804123A (+1) | new page (wait for A, clear box) |
| FD | 0 | 0x08041254 (+1) | newline (2-line box) |
| FE | 0 | 0x0804128A -> 0x08041300 (+1) | **end of a list entry**: terminates all name strings (see §Name lists); in the dialogue runner it only advances (guess: no visible effect) |
| FF xx | 1 | 0x080412AC -> 0x08041C78, jump table on xx (0-4) | end of string; xx is 00 (5695x), 04 (554x), 02 (251x), FF (270x). 04 seems "close box and continue the event" |

D0-EF are **glyph codes, not control codes**: they fall through the glyph path with width 1 (see §Width table), which is
why the probe shots showed them as narrow garbage that "ate" the bytes after them. They are 32 free glyph slots.

## Width table and line wrap (verified by disassembly; phase 5 must measure in-game)

The game already has a **variable-width font**. For each glyph the step routine adds `width[code]` to the pen x
(+0x14). Widths are a 2-byte-per-code table at **0x4645B8** (an identical alternate at 0x4647B8, picked when state
+0x27 is set); byte 0 is the advance in px: space (00) = 4, most kana and A-Z = 8, small kana and some letters = 7,
・ = 5, 」 = 4, ！ = 5, ？ = 6 (codes BD/C1/C3/C4 as tabled), D0-F7 = 1. Before drawing a word it sums widths up to the
next space (00) or control code (> F7) and, if pen x + word > **0xD0 (208 px)**, wraps first (0x080414BA-0x08041538):
**automatic word wrap at 208 px per line**. Glyph bitmaps: the alternate path (state+0x27 set) reads 64 bytes per
code at **0x0854FEA0** (`lsls r0,code,#6`), 8x16 4bpp; rendered, codes 01-10 there are an italic Latin A-P, so that is
a second font (not the kana dialogue font). The main font's address is still to be pinned (phase 5). Phase 5: English can use the existing VWF by redrawing glyphs,
adding lowercase in D0-EF and rewriting the width table, instead of writing a new VWF.

## Name lists (verified: pointer tables found)

Every name the menus use is a **FE-terminated string** in the same encoding, in lists with a u32 pointer table right
after the list (one pointer per entry). The FF-only pointer sweep below missed them. A sweep for pointer runs into
0x464000-0x512000 whose targets follow an FE byte finds **1129 entries in 17 tables**:

| Table | Entries | Contents (first entries) |
|---|---|---|
| 0x465B8C | 30 | medal names: クワガタ, カブト, トータス, クラゲ ... |
| 0x465C84 | 27 | skill types: かくとう, しゃげき, こうがく, かやく ... |
| 0x466374 | 8 | actions: なぐる, がむしゃら, うつ, ねらいうち ... |
| 0x466688 | 52 | attack names: いっせん, よこいっせん, いっせいしゃげき ... |
| 0x468308 | 60 | Medabot names: ストランジェロ, デアベイル, ロッソナリッツ ... |
| 0x468A00 | 240 | part names: バギュー, ドロイテ, アイラガーチ ... |
| 0x469450 | 240 | part model codes: ANGー01, ANGー02 ... (letters, digits, ー) |
| 0x46A508 | 60 | weapon kinds: ソード, ハンマー, ライフル ... |
| 0x46A6F0 | 7 | leg types: ひこう, ふゆう, たきゃく ... |
| 0x46A744 | 11 | terrain: こうや, さばく, いわば ... |
| 0x46E60C | 121 | character names: ガンマ, ダミー, アイリス ... |
| 0x46EDA0 | 6 | battle menu: パーツ, メダフォース, しょうさい, ターゲット ... |
| 0x46F0BC | 128 | battle status messages: こわれている, つかえない, かいすうゼロ ... |
| 0x470B08 | 4 | small list |
| 0x50C998 | 39 | items: ロボロボメダル, ふくびきけん, わたるくんルアー ... |
| 0x50EF18 | 24 | tutorial topics: 「メダフォース」について ... |
| 0x510C28 | 72 | **staff credits**: エグゼクティブプロデューサー ... and staff names (あきら, KIT ...) |

So the credits are text, not graphics. Part, Medabot and medal names are all here. The 0x4B6478/0x4B6658 tables
point at fixed 13-byte records (`00` + up to 12 bytes, FF-padded: `00 0C 0A 0B FF..`, `00 02 09 08 0C 1C 1D 10 19 65 25
FF FF`): values look like small indices, not words (guess: shop or event lists, not text). Check one in-game in phase 5
before excluding them. Phase 4's extractor must take both string kinds (FF xx and FE).

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

- ~~Robot model, part and medal names~~: found, see §Name lists (FE-terminated). ヘッドシザース/メタルビートル are the
  anime's names and simply aren't in this game (its parts have their own names).
- Name-entry keyboard: kana grid looks font-drawn (check in phase 5).
