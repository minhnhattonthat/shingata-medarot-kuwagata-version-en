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

## Still to survey (phase 1 static sweep + tour from the phase 2 debug tool)
- Static sweep: render every LZ77 block (`tools/lz77.py scan`, 1457 blocks) and every "Le" block (1564, needs the
  decoder: docs/re/rom.md) in gba4 and gba8, linear too, into numbered sheets with an offset index, and list every
  Japanese cell. Not done yet.
- Mid-game screens the tour can't see yet: field menu (Start/Select did not open one in the 2F bedroom state), parts
  and Medabot screens, medal screen, robattle HUD and command menus, shop, save screen, game over, ending, credits,
  chapter/area banners, minigames. Reach them with the debug tool (phase 2).
