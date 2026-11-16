# Glossary - Shingata Medarot: Kuwagata Version

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables: a JP term (as a whole kana/kanji run) needs its EN form in the line,
and an Avoid spelling fails.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Ikki-kun, Karin-chan, Iris-san). Name order: Western (given name first).
- Romanisation source: official English (Medabots anime/games) where it exists, else an earlier fan patch, else
  Hepburn without macrons. Shingata's own new cast and Medabots have no official English: names below are ours.
- Credits: English.
- Register / flavour: light JP flavour (honorifics kept, -sensei for teachers addressed as せんせい).
- Sound effects: the font has no `* < > ~`, so SFX are plain words with ! (`BAM!`, `Woof! Woof!`) (D9).
- Abbreviations: full names and terms everywhere; name boxes are hard-capped at 10 bytes (measured), so the few
  names that can't fit get the shortest clear form, listed here with "cap" in notes.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・ -> ..., ！？ -> !?, 〜 (long vowel / wavy) -> drop or stretch
  the word ("Hellooo!"), ♪ -> drop (no glyph). Only ASCII the font has: A-Z a-z 0-9 space ! " % & ' ( ) + , - . / : ; ?
- The player is {var:00} (default Ikki). Never glue a suffix onto {var:..}; "{var:00}-kun" is fine (honorific).
- Rubberobo Gang grunts and officers end sentences with ロボ: keep it as "-robo!" / ", robo!" ("Take that, robo!").
- Voices: see docs/synopsis.md "Who is who" for each character's pronoun and quirks; keep every quirk audible.
- Kanji-free kana text is the game's style for kids; the English stays plain and lively, not childish.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| イッキ | Ikki | | Medarot 2 Core hero (4F tables); the player is always {var:00} | |
| ガンマ | Gamma | | Shingata's hero | |
| かいとうレトルト | Phantom Retort | | Henry's masked identity; "Retort" keeps the retort-curry pun (dub: Phantom Renegade) | Phantom Renegade |
| アリカ | Erika | | official | Arika |
| コウジ | Koji | | official | |
| カリン | Karin | | official | |
| ヒカル | Henry | | official dub name | Hikaru |
| キクヒメ | Samantha | | official (the Screws) | Kikuhime |
| イワノイ | Sloan | | official (the Screws) | Iwanoi |
| カガミヤマ | Spyke | | official (the Screws) | Kagamiyama |
| スクリューズ | Screws | | "the Screws" | |
| ナエ | Natalie | | official | |
| ヘベレケ | Meta-Evil | | ヘベレケはかせ = Dr. Meta-Evil (official) | Hebereke |
| サケカース | Seaslug | | Rubberobo officer (official) | Sakekasu |
| スルメ | Shrimplips | | Rubberobo officer (official) | Surume |
| シオカラ | Squidguts | | Rubberobo officer (official) | Shiokara |
| レトルト | Retort | | レトルトレディ = Retort Lady; keeps the "retort curry" pun | |
| メダロットはかせ | Dr. Aki | | official name of the Medabot Professor | |
| アイリス | Iris | | | |
| ガンマ | Gamma | | | |
| ラ・マスカーラ | La Mascara | 10 | | |
| ユマリ | Yumari | | | |
| リューキ | Ryuki | | | |
| シフォン | Chiffon | | | |
| マスキー | Masky | | | |
| ピョロリ | Pyorori | | | |
| ボヨヨ | Boyoyo | | | |
| マンソン | Manson | | | |
| マミーア | Mamia | | | |
| カムイ | Kamui | | | |
| ソンチョー | Chief | | village chief | |
| アマリロ | Amarillo | | | |
| アズル | Azul | | | |
| ロジョ | Rojo | | | |
| オーロ | Oro | | オーロたいちょう = Leader Oro (cap) | |
| マルガリータ | Margarita | | cocktail-named | |
| ウォッカ | Vodka | | | |
| ブルーハワイ | Blue Hawaii | | | |
| プース・カフェ | Pousse Cafe | | | |
| カルア | Kahlua | | | |
| ミルキー | Milky | | | |
| ジュンマイ | Junmai | | | |
| ソルティ | Salty | | | |
| ハチロウ | Hachiro | | | |
| キララ | Kirara | | | |
| ラピ | Rapi | | | |
| ナツコ | Natsuko | | | |
| アワノ | Awano | | | |
| ヤナギ | Yanagi | | | |
| ベティ | Betty | | | |
| ボナパルト | Bonaparte | | | |
| モッキンバード | Mockingbird | | | |
| コーダイン | Kodine | | | |
| ホリウチー | Horiuchi | | | |
| キンタロウ | Kintaro | | | |
| ブリレッツ | Brilletz | | | |
| テラ | Terra | | | |
| ラシオネ | Racione | | | |
| ビオラ | Viola | | | |
| コテツ | Kotetsu | | | |
| モレア | Morea | | | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| メダロポリス | Medalopolis | | | |
| オセアノ・タワー | Oceano Tower | | | |
| ビーチ・デル・ソル | Beach del Sol | | | |
| メダロットカンパニー | Medabot Company | | | Medarot |

## Medabots (468308, 10 bytes)
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ストランジェロ | Strangelo | 10 | | |
| デアベイル | Dearbail | 10 | | |
| ロッソナリッツ | Rossonritz | 10 | cap (Rossonaritz) | |
| アルカオプティ | Arcaopti | 10 | | |
| ジャートフェイジ | Jartphage | 10 | | |
| ペロスカル | Peroskull | 10 | | |
| アルトソニード | Altosonido | 10 | | |
| バロウ | Barrow | 10 | | |
| カポ・パスカ | Capo Pasca | 10 | | |
| マジッシュフロウ | Magishflow | 10 | | |
| ベクフィー | Becfee | 10 | | |
| マウナドラーガ | Maunadraga | 10 | | |
| バスクラータ | Basclata | 10 | | |
| デュオカイザー | Duo Kaiser | 10 | | |
| プレディケイダー | Predicader | 10 | | |
| ラグノー | Ragno | 10 | | |
| ベネノーラ | Venenola | 10 | | |
| マシオコルポ | Maciocorpo | 10 | | |
| バレントレロ | Valentrero | 10 | | |
| プラインフロイ | Plainfroi | 10 | | |
| モーダウォル | Modawall | 10 | | |
| セルヴォ | Cervo | 10 | also a medal | |
| ビート | Beat | 10 | also a medal | |
| ペレドメ | Peredome | 10 | | |
| ケンプメイド | Kempmaid | 10 | | |
| スカルタクス | Skultacus | 10 | | |
| ルナコニー | Lunacony | 10 | | |
| ハークノット | Harknot | 10 | | |
| チェインブル | Chainbull | 10 | | |
| ヒエロトラバス | Hierotrabs | 10 | cap (Hierotrabas) | |
| メディエスピオ | Mediespio | 10 | | |
| モントラビー | Montrabee | 10 | | |
| メイリンローブ | Meilinrobe | 10 | | |
| バオリキシー | Baorikishi | 10 | | |
| リギングラ | Rigingla | 10 | | |
| ユナフィ | Yunafi | 10 | | |
| ファミーレ | Famire | 10 | | |
| リネル | Rinel | 10 | | |
| クラッツクリニア | Kratclinia | 10 | cap | |
| ディオーザ | Diosa | 10 | | |
| マテューラ | Matura | 10 | | |
| トデス | Todes | 10 | | |
| ピコラブル | Picolable | 10 | | |
| ソラテス | Solates | 10 | | |
| マーバス | Marbus | 10 | | |
| アドソルダ | Adsolda | 10 | | |
| アグラダブル | Agradable | 10 | | |
| デューケン | Duken | 10 | | |
| プロドラド | Prodorado | 10 | | |
| ベイザハート | Beizaheart | 10 | | |
| ネザドロイ | Nezadroy | 10 | | |
| グラレッチ | Grallech | 10 | | |
| ボーデンドラン | Bodendran | 10 | | |
| ダクシュー | Dakshu | 10 | | |
| フィビオス | Phibios | 10 | | |
| ペレグレサー | Peregreser | 10 | cap | |
| アリファセット | Alifacet | 10 | | |
| パフレック | Puffrec | 10 | | |
| メイレーニュ | Meiregne | 10 | | |
| ラズー | Razoo | 10 | | |

## Medals (465B8C, 10 bytes)
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| クワガタ | Kuwagata | 10 | official; クワガタメダル = Kuwagata Medal | |
| カブト | Kabuto | 10 | official | |
| トータス | Tortoise | 10 | | |
| クラゲ | Jellyfish | 10 | | |
| クマ | Bear | 10 | | |
| クモ | Spider | 10 | | |
| へ・ビー | He-Bee | 10 | snake (hebi) + bee pun | |
| クイーン | Queen | 10 | | |
| クラーケン | Kraken | 10 | | |
| フェニックス | Phoenix | 10 | | |
| ユニコーン | Unicorn | 10 | | |
| ゴースト | Ghost | 10 | | |
| ナイト | Knight | 10 | | |
| マーメイド | Mermaid | 10 | | |
| ペンギン | Penguin | 10 | | |
| コウモリ | Bat | 10 | | |
| カッパ | Kappa | 10 | | |
| ネズミ | Mouse | 10 | | |
| カメレオン | Chameleon | 10 | | |
| ウサギ | Rabbit | 10 | | |
| サル | Monkey | 10 | | |
| デビル | Devil | 10 | | |
| エンジェル | Angel | 10 | | |
| ドラゴン | Dragon | 10 | | |
| しのび | Ninja | 10 | | |
| エイリアン | Alien | 10 | | |
| ネコ | Cat | 10 | | |
| オオカミ | Wolf | 10 | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| メダロット | Medabot | | official; plural Medabots | Medarot |
| メダロッター | Medafighter | | official | Medarotter |
| メダロッターズ | Medafighters | | | |
| メダロッチ | Medawatch | | official | Medarotch |
| ロボトル | Robattle | | official; ロボトルファイト = "Robattle, fight!" (referee call) | Robottle |
| ロボロボ | Rubberobo | | ロボロボだん = Rubberobo Gang (official) | Roborobo |
| ティンペット | Tinpet | | official | |
| メダフォース | Medaforce | 10 | official | |
| メダル | Medal | | | |
| パーツ | part / parts | | | |
| ほねぐみ | frame | | the Tinpet is a Medabot's "frame" | |
| フユーン | Fuyun | | フユーンストーン = Fuyun Stone | |
| ゴッドエンペラー | God Emperor | | | |
| セレクト | Select | | セレクトたい = Select Corps; セレクトスリー = Select Three | |
| パーツンラリー | Parts'n Rally | | | |
| メダリンク | Medalink | | | |
| メダロードレース | Medaroad Race | | | |
| エレメンタルシリーズ | Elemental Series | | | |
| ヘベレケスペシャル | Meta-Evil Special | | | |
| かくとう | Melee | 10 | skill type | |
| しゃげき | Shooting | 10 | skill type | |
| こうがく | Beam | 10 | skill type (optical) | |
| かやく | Explosive | 10 | skill type | |
| じゅうりょく | Gravity | 10 | skill type | |
| せっち | Trap | 10 | skill type (placed); かくとうトラップ = Melee Trap | |
| へんどう | Shift | 10 | skill type (stat fluctuation) | |
| ていし | Halt | 10 | skill type (stops a part); not "Freeze" = フリーズ, a weapon kind | |
| そくばく | Bind | 10 | skill type | |
| けいぞく | Sustained | 10 | skill type | |
| かいじょ | Dispel | 10 | skill type | |
| むこう | Nullify | 10 | skill type | |
| ぼうぎょ | Defense | 10 | skill type | |
| かいふく | Recover | 10 | skill type | |
| ふっかつ | Revive | 10 | skill type | |
| たいくう | Anti-Air | 10 | skill type | |
| たいすい | Anti-Water | 10 | skill type | |
| さくてき | Scout | 10 | skill type | |
| いんぺい | Stealth | 10 | skill type | |
| ぼうがい | Jamming | 10 | skill type and action | |
| はかい | Destroy | 10 | skill type | |
| さいせい | Regenerate | 10 | skill type | |
| れんけい | Teamwork | 10 | skill type | |
| はんげき | Counter | 10 | skill type | |
| なぐる | Strike | 10 | action | |
| がむしゃら | Berserk | 10 | action | |
| うつ | Shoot | 10 | action | |
| ねらいうち | Snipe | 10 | action | |
| まもる | Protect | 10 | action | |
| なおす | Repair | 10 | action | |
| おうえん | Support | 10 | action | |
| こうや | Wilderness | 10 | terrain | |
| さばく | Desert | 10 | terrain | |
| いわば | Rockland | 10 | terrain | |
| けいこく | Canyon | 10 | terrain | |
| そうげん | Grassland | 10 | terrain | |
| しんりん | Forest | 10 | terrain | |
| まちなか | City | 10 | terrain | |
| しつない | Indoors | 10 | terrain | |
| かいがん | Coast | 10 | terrain | |
| すいちゅう | Underwater | 10 | terrain | |
| サイバー | Cyber | 10 | terrain | |
| ひこう | Flight | 10 | leg type | |
| ふゆう | Hover | 10 | leg type | |
| たきゃく | Multi-Leg | 10 | leg type | |
| にきゃく | Bipedal | 10 | leg type | |
| しゃりょう | Wheeled | 10 | leg type | |
| せんしゃ | Tank | 10 | leg type | |
| せんすい | Aquatic | 10 | leg type | |
| ローテーション | Rotation | 10 | battle menu | |
| ターゲット | Target | 10 | battle menu | |
| きゃくぶ | Legs | 10 | part slot (あたま Head, みぎうで Right Arm, ひだりうで Left Arm) | |
| せいこう | Success | | part stat (hit chance) | |
| じゅくれんど | Mastery | | medal skill level | |
| あいしょう | affinity | | medal/part compatibility | |

<!-- GENERATED by tools/glossary_names.py -->
## Game names (generated from the translated name tables; edit the tables, then re-run)
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| MーPKメダル | M-PK Medal | | item | |
| おぼえていない | Not Known | | status | |
| かいすうドレイン | Use Drain | | weapon kind | |
| かいひふのう | Disable Evasion | | weapon kind | |
| かくとうトラップ | Melee Trap | | weapon kind | |
| かぜのつばさ | Wind Wings | | item | |
| かやくか | Explosive Shift | | attack | |
| かやくむこう | Nullify Explosive | | weapon kind | |
| かんぜんぼうぎょ | Perfect Defense | | weapon kind | |
| きゃくぶパーツと「ちけい」について | Legs Parts/Terrain | | tutorial topic | |
| きゅうそくチャージ | Rapid Charge | | weapon kind | |
| きょうか | Enhance | | weapon kind | |
| くわがたむし | Stag Beetle | | item | |
| けいぞくかいふく | Sustained Recover | | weapon kind | |
| けいたいでんわ | Cell Phone | | item | |
| こうがくか | Beam Shift | | attack | |
| こうがくむこう | Nullify Beam | | weapon kind | |
| こうげきクリア | Attack Clear | | weapon kind | |
| こうげきトラップ | Attack Trap | | attack | |
| こわれている | Broken | | status | |
| こんらん | Confusion | | weapon kind | |
| しのびチケット | Ninja Ticket | | item | |
| しゃげきトラップ | Shooting Trap | | weapon kind | |
| しょうじょうクリア | Status Clear | | weapon kind | |
| しようふのう | Disable | | weapon kind | |
| じゅうりょくか | Gravity Shift | | attack | |
| じゅうりょくむこう | Nullify Gravity | | weapon kind | |
| じょうじチャージ | Constant Charge | | weapon kind | |
| せっちいりょくアップ | Trap Power Up | | attack | |
| せんぼうきょう | Periscope | | item | |
| そせい | Resurrect | | weapon kind | |
| つかえない | Unusable | | status | |
| てんとう | Knockdown | | weapon kind | |
| へんか | Change | | weapon kind | |
| へんか／かいふく | Change/Recover | | weapon kind | |
| へんか／こうげき | Change/Attack | | weapon kind | |
| へんか／ぼうがい | Change/Jamming | | weapon kind | |
| へんか／ぼうぎょ | Change/Defense | | weapon kind | |
| ほしのかけら | Star Fragment | | item | |
| ほじょチャージ | Charge Support | | weapon kind | |
| ぼうぎょふのう | Disable Defense | | weapon kind | |
| みまんぼうぎょ | Threshold Defense | | weapon kind | |
| アンチエア | Anti-Air | | weapon kind | |
| アンチシー | Anti-Water | | weapon kind | |
| ウィルス | Virus | | weapon kind | |
| ウェーブ | Wave | | weapon kind | |
| ガトリング | Gatling | | weapon kind | |
| クロスセット | Cross Set | | weapon kind | |
| クロスファイア | Crossfire | | weapon kind | |
| サクリファイス | Sacrifice | | weapon kind | |
| サンダー | Thunder | | weapon kind | |
| ソード | Sword | | weapon kind | |
| タウンマップ | Town Map | | item | |
| ダメロット | Meda-dud | | item | |
| チャージドレイン | Charge Drain | | weapon kind | |
| ツビーベル | Zwiebel | | part | |
| デストロイ | Destroy | | weapon kind | |
| トラップむこう | Nullify Trap | | attack | |
| トラップクリア | Trap Clear | | weapon kind | |
| ナパーム | Napalm | | weapon kind | |
| ハンマー | Hammer | | weapon kind | |
| パーツの「せいこう」について | Part Success | | tutorial topic | |
| ビーム | Beam | | weapon kind | |
| ファイヤー | Fire | | weapon kind | |
| フォースせいぎょ | Force Control | | weapon kind | |
| フォースドレイン | Force Drain | | weapon kind | |
| フリーズ | Freeze | | weapon kind | |
| ブレイク | Break | | weapon kind | |
| プレス | Press | | weapon kind | |
| ベール | Behr | | part | |
| ホールド | Hold | | weapon kind | |
| マッターシェン | Mattaschen | | part | |
| ミサイル | Missile | | weapon kind | |
| ミニハンドル | Mini Wheel | | item | |
| メダルの「じゅくれんど」について | Medal Mastery | | tutorial topic | |
| メダルもどき | Fake Medal | | item | |
| メダロットってなに？ | What's a Medabot? | | tutorial topic | |
| メルト | Melt | | weapon kind | |
| ライフル | Rifle | | weapon kind | |
| レーザー | Laser | | weapon kind | |
| ロボロボカード | Rubberobo Card | | item | |
| ロボロボメダル | Rubberobo Medal | | item | |
| ロボロボメダルについて | Rubberobo Medals | | tutorial topic | |
<!-- END GENERATED -->
## Decisions from earlier batches
- ベール is also the plain word "veil": なぞのベール (veil of mystery, 50D015) is not the part Behr. The row below
  masks it so the check doesn't demand "Behr".

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| なぞのベール | mystery | | idiom "shrouded in a veil of mystery", not the part Behr | |

## Capped part names (10-byte name buffer; full form in notes)
The b001 review asked for the full names; they don't fit the measured 10-byte cap, so these short forms stand.

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| フォイデノンモル | Foinonmor | 10 | cap; full Foidenonmor | |
| グラフュノンモル | Grafnonmor | 10 | cap; full Grafyunonmor | |
| タテコントラリ | Tatecontra | 10 | cap; full Tatecontrali | |
| ディレクシッケル | Direcsichl | 10 | cap; full Direcsichel | |
| アビディマリーナ | Abimarina | 10 | cap; full Abidimarina | |
| アンガベコレト | Angabecol | 10 | cap; full Angabecoleto | |
| アンガデコレト | Angadecol | 10 | cap; full Angadecoleto | |
| モデロリスタット | Modelstat | 10 | cap; full Modeloristatt | |
| レットティグレ | Rettigre | 10 | cap; full Retto Tigre | |
| ニストロティグレ | Nistigre | 10 | cap; full Nistro Tigre | |
| ジャメットベーノ | Jambeno | 10 | cap; full Jametto Beno | |
| ペテロケミセルト | Petrocerto | 10 | cap; full Petrokemicerto | |
| ペテロケミエスク | Petroesq | 10 | cap; full Petrokemiesque | |
| デセントベスタ | Desentbes | 10 | cap; full Desento Besta | |
| リンハデバシロ | Linhbacil | 10 | cap; full Linha de Bacilo | |
| アルマエスピーノ | Armespino | 10 | cap; full Arma Espino | |
| ソンプロフェット | Sonprofet | 10 | cap; full Sonprofetto | |
| ソンプロビッサ | Sonprovis | 10 | cap; full Sonprovissa | |
| カンバナデスコ | Cambandes | 10 | cap; full Cambana Desco | |
| ラビダラルガ | Vidalarga | 10 | cap; full La Vida Larga | |
| ラマノデグラ | Manodegra | 10 | cap; full La Mano Degra | |
| ラマノイグラン | Manoigran | 10 | cap; full La Mano Igran | |
| ラコララルガ | Colalarga | 10 | cap; full La Cola Larga | |
| エルカンポネーバ | Camponeva | 10 | cap; full El Campo Neva | |
| ルミネセンス | Luminesce | 10 | cap; full Luminescence | |
