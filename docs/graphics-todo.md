# Graphics text still Japanese (phase 8 redraw list)

From the visual-QA pass of 2026-11-17 (codex reviewer over `work/qa/tour/sheet*.png`, verdicts in
`work/qa/verdicts/chunk_000.tsv`). Every item below is graphics: `tools/findtext.py` finds none of them as text
(hits it prints are other dialogue), and `tools/textmap.py` explains every byte of the text region. Match each to
its block with `vramfind.py` over the scene shot (`work/qa/scenes_en/shots/<scene>.png`, states from
`prove.py`), redraw, and re-shoot the scene zoomed from a cold boot.

| Scene(s) | Japanese left |
|---|---|
| title, newgame_menu | logo 真型 メダロット (keep as logo or add an English subtitle: ruling needed, non-blocking), つづきから (not seen yet: needs a save; probably elsewhere in lz_72AC64). **Done:** はじめから -> NEW GAME, オプション -> OPTIONS (screen labels on tiles lz_72AC64 + map lz_72BF8C+10) |
| options (same screen, BG0 rows 11-17 of map lz_72BF8C+10) | ロボトルじかん, ながい / ふつう / みじかい, ロボトルメッセージ, あり / なし: the rows are 8 px tall (6-px fill + outline 3, fill 1 / 2): needs a 6-px font first |
| save_corrupt | whole box: もうしわけありません / セーブデータが こわれました / もういちど はじめから あそんでくださいね |
| sound_test (test mode) | テストモード, BGMをきく, SEをきく, もどる |
| name_entry | ネームエントリー, なまえを10もじいないで にゅうりょくしてください, カタカナ / ひらがな / えいすうじ, すすむ / もどる / けってい, the kana grid (needs an English letter grid: input codes too) |
| field_menu | **Done** (pilot): MEDAWATCH / ITEMS / HELP / SAVE (Le 54C27C/54C420/54C5A0/54C72C), money 円 -> ¥ (Le 56C920 tile 0; names charset C5 too). Other screens with a money box may load their own 円 copy: check |
| items, items_owned | アイテム header, …アイテムをつかう, …ならびかえ |
| field_help (encyclopedia) | せつめい heading |
| medawatch | メダロット / メダル / パーツ, カーソルでせんたく, けってい, もどる |
| medal_list, party_medals | メダル header, カーソルでメダルせんたく, …しょうさいがめんへ, Lv.UPまで |
| medarot_list, party_setup | メダロット header, くみたてがめんへ, ならびかえ |
| parts_list, party_parts, parts_owned | パーツ header, tabs あたま etc., しょうさい, column headers パーツめい / しょじすう(そうびすう) / せいべつ |
| parts_*_detail | パーツ, ヘルプ, stat labels そうこう / すいしん / きどう / ぼうぎょ / きんせつ / えんかく / せいこう / いりょく / かいすう |
| parts_shop* | パーツショップ header, 円, パーツをかう / うる / もどる, slot picker あたま / みぎうで / ひだりうで / きゃくぶ, えらぶ / けってい, list headers しょうさいがめんへ / ごうけい / パーツめい / しょじすう / ねだん / こすう, confirm はい / いいえ |
| save | セーブ, メダル, パーツ, ゲームじかん, かちすう／トータル, はい / いいえ |
| parts_trade | パーツトレード |
| robattle_intro, robattle_prep | ロボトルインフォメーション, ロボトルフィールド |
| road_race | メダロードレース |
| baseball | のこり10きゅう, 0てん, プレイボール, バットをふる |
| car_game | のこり60びょう, 0てん, メダカートレース, スタート!! |
| corps_game | ばくだん, ライフ, コロシア チビケンジャー, セレクトほんぶを まもれ!! |
| town_map | タウンマップ |

Not graphics, also found in that pass (text/engine):
- **credits role lines cut** (open bug): roles stop after ~13-16 glyphs ("Executive Produc", "Chief Produce",
  "Character De"); staff names draw whole. The role sprite/buffer is smaller than windows.json `credits_line`
  says (the 18-byte ruler test only proved names). Shots: `work/qa/credits_t/sheet.png`. Find the role buffer
  size in the credits code (mode 4 sub 6), then re-measure and refit the 72 credit strings.
- money digits in the field-menu box look squeezed against each other compared with the original's spaced digits
  (`work/qa/zoom/fm.png`): check the 8x8 digit overrides in `font/en_names_8x8.txt` / the advance used there.
- item list: "Rubberobo Medal" ends against the "x" column (`work/qa/zoom/io.png`); 86 px may be 2-4 px too wide.
- terminology: one encyclopedia topic says Speed, its text says Propulsion (sheet_4): check glossary.
- "Cervoアアアアア": the debug tool's A-mash through Medabot naming appends ア (as ガンマアアア for the player);
  not a translation bug, but the name entry grid needs English letters.
