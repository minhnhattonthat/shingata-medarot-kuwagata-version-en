# Graphics text survey (phase 1, `references/graphics.md` §Survey)

Every tile-drawn Japanese element seen so far. Source guesses come from the ROM map (docs/re/rom.md); confirm each with
`ppudump.lua` + `vramfind.py` before editing. "Font?" = may be font-drawn at runtime (then it's text work, not graphics).

## Tour list (cold boot -> title -> options -> new game -> name entry -> intro)
| # | Screen | Element | Kind | First guess at source | Shot |
|---|---|---|---|---|---|
| G1 | Title | 「真型 メダロット」 logo | BG | "Le" or LZ77 block | work/qa/smoke_orig f000960 |
| G2 | Title | "Kuwagata Version" subtitle | BG | already English | same |
| G3 | Title | 「PRESS START」-style line under the logo (small, Japanese/English unclear) | BG/OBJ | | same |
| G4 | Title menu | はじめから, オプション (red/green outlined lettering) | BG | compressed tiles | work/qa/smoke_orig final |
| G5 | Options | ロボトル じかん: ながい / ふつう / みじかい; ロボトル メッセージ: あり / なし | BG | compressed tiles (coloured, outlined: not the dialogue font) | same |
| G6 | Title BG | "MEDAROT" pattern in the background | BG | English already; it says MEDAROT, decide with the logo | same |
| G7 | Name entry | header 「ネームエントリー」 | BG | compressed tiles | work/qa/reads1 f001900 |
| G8 | Name entry | prompt 「なまえを 10もじ いないで にゅうりょくしてください」 | BG | font? (yellow outlined, likely pre-drawn) | same |
| G9 | Name entry | kana keyboard grid, カタカナ / ひらがな / えいすうじ tabs | BG | font? keyboard cells; tabs likely tiles | same |
| G10 | Name entry | buttons すすむ / もどる / けってい | BG | compressed tiles | same |
| G11 | Intro | dialogue box | BG | font-drawn: text work | work/qa/run4 |

## Static sweep (done; reviewed)
`python -X utf8 tools/gfx_sweep.py work/sweep/gba4` (and `--fmt gba8 work/sweep/gba8`) decompresses all 3021
pointed-to blocks (1457 LZ77 + 1564 Le), renders 2640 with a per-block tile width (2158 at 32, 417 at 8, 105 at 2, 75
at 4; narrow ones folded into bands) on 167 gba4 / 102 gba8 sheets, `index.tsv` maps sheet+row to block offset, and
`skipped.tsv` lists the 381 skipped with reasons (270 tilemap-like, 89 tiny, 22 palettes). Reviewed by an independent
read-only pass (`tools/sweep_review.py`: one `codex exec` per 10 sheets); answers in `work/sweep/*/review/chunk_*.tsv`,
merged per block in `work/sweep/gba4/review/japanese.tsv` (208 items). **gba8: no Japanese** on any sheet, so the game
is 4bpp throughout. "?" = Japanese seen but not legible in the grey render: still to be confirmed in the tour.

| # | Block(s) | Codec | What (reviewer's reading) | Kind |
|---|---|---|---|---|
| G12 | 0x54C27C-0x54C890 | Le | battle labels ダメージ, メダフォース, チャージ + 2 unread | label |
| G13 | 0x54E59C, 0x54EC30 | Le | にする, うで, こうげき | label |
| G14 | 0x54F1B8 | Le | part stat labels: いりょく せいこう じゅうてん はんのう れいきゃく すいしん そうこう きゃくぶ ぼうぎょ | label |
| G15 | 0x5513C8 | Le | チャージ, メダフォース (second copy) | label |
| G16 | 0x5518A0 | Le | **a whole kana font as tiles** (ア-ホ, ム-ゼ, ダ-お, た-ん, じ-ざ): a menu/HUD font separate from the dialogue VWF | font |
| G17 | 0x552F40, 0x553694, 0x553E10 | Le | ロボトル, そうび, メダル/メダルをつかって/チャージ, ?をきりひらけ！ | label |
| G18 | 0x5554F0-0x5574EC (14 blocks) | Le | unread Japanese; 0x556570 reads かいぞく / かぞくゲーム | label |
| G19 | 0x55C0D4 | Le | unread | label |
| G20 | 0x561FD0, 0x5624FC | Le | medal skill labels: こうげき じゅうりょく まもる おうえん ねらいうち ぼうがい いんぺい ... | label |
| G21 | 0x56A05C | Le | かいひ, さいそく, すいしん + 2 unread | label |
| G22 | 0x56D154 | Le | シンガタ メダロット | logo |
| G23 | 0x56F328-0x574A44 (8 blocks) | Le | Medawatch menu: もちものへ, メダロット, アニメーション, カーソルで メダルせんたく, パーツ, メダリア, メダル, メダロッチ | label |
| G24 | 0x575BE4-0x577B98 | Le | パーツ, つうしん + unread | label |
| G25 | 0x57D37C | Le | メダリア | label |
| G26 | 0x5AAC38 | Le | 真型メダロット | logo |
| G27 | 0x650D9C, 0x6A5CB0, 0x6ABABC | LZ77 | メダロット / メダロ.. lettering on pictures | logo |
| G28 | 0x6CAA50-0x6DB050 (11 blocks) | LZ77 | おもちゃ, はな repeated (shop/sign art? check in tour: may be a misread) | other |
| G29 | 0x721988 | Le | 動 + unread (kanji: unusual in this kana-only game) | label |
| G30 | 0x725778-0x74AFFC (19 blocks) | LZ77 | field menu screens: メダロッチ, アイテム, アイテムをつかう, セッティング, ロボトル, パーツ, セーブデータが.., はなしを.., ヒダリウデ, アタマ, こうせいがめん, a kana font (0x72F06C) | label/font |
| G31 | 0x77EB98, 0x77EE84, 0x78059C, 0x786FC4 | LZ77/Le | 真型 / メダロット title logo parts | logo |
| G32 | 0x78CA88 | Le | パスワードを.. (password screen) | label |
| G33 | 0x7C26E8-0x7C42C0 | Le | メダロット.. logo variants | logo |

The credits are **text**, not graphics (FE list at 0x510C28, docs/re/text.md §Name lists), as are part, medal and
Medabot names. G1-G11 from the tour are some of these blocks seen in place (title logo = G26/G31, title menu and
options = G18/G30 likely); match them with `ppudump.lua` + `vramfind.py` in phase 8.

## Still to survey (tour from the phase 2 debug tool)
- Mid-game screens the tour can't see yet: field menu (Start/Select did not open one in the 2F bedroom state), parts
  and Medabot screens, medal screen, robattle HUD and command menus, shop, save screen, game over, ending, credits,
  chapter/area banners, minigames. Reach them with the debug tool (phase 2).
