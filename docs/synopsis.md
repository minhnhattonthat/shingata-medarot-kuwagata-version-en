# Script synopsis and character guide

Spoilers throughout. Based on the Japanese extraction, not on a complete playthrough.
References such as `4F5940:135` mean table filename and zero-based `strings` index.
English names requested for the Ikki cast are used below. Other romanizations are suggestions.
Japanese is confined to the left column of reference tables; voice notes use romanized Japanese.

## Read this first: two different stories are present

The extraction contains two distinct casts and settings. Do not combine them into one chronology or globally replace names by portrait number.
The sixteen requested `4F...` tables contain the Ikki/Erika/Koji story. This is retained Medarot 2 Core material: `4F7E64:226` explicitly congratulates the player on clearing that title.
`50A9D8`, `4B50CC`, `46D598`, `46E0F0`, and `510124` instead contain Shingata's Gamma/Iris/Ryuki cast and M-PK setting. They are not merely supplementary NPC dialogue for Ikki's story.
The character-name table `46E60C` independently identifies Gamma and the Shingata cast. `{var:00}` is the entered player name in both story sets; it does not establish that both protagonists are Ikki.
Portrait IDs are reused: for example, face `0004` is Koji in the retained story but Yumari in Shingata; `0013` is the professor in the retained story but Rojo in Shingata.
This document describes both sets. Extraction alone does not establish which retained scenes can execute. Check event references before treating retained dialogue as playable Shingata content.

## A. Retained Ikki story, in narrative order

These are editorial acts, not asserted in-game chapter titles. ROM order interleaves later callbacks, earlier scenes, optional visits, and alternative routes.

1. **A first Medabot and a false accusation.** Ikki spends the money for his mother's retort-pouch curry on Medabot equipment and is sent upstairs. Phantom Retort supplies his father with a Medal and Medawatch; Dad gets the Medabot running. Erika introduces friendly Robattles, pursues school-paper scoops, and photographs Ikki's victories over the Screws. The professor and Natalie introduce Medal research and the Elemental prototypes. Koji arrives from Hanazono Academy seeking the culprit who lifted Karin's skirt and wrongly suspects the local children. Erika makes Ikki wear a skirt as bait. The Rubberobo Gang is implicated, but the Select Corps gets the public credit. Sources: `4F3C84`, especially 72-83, 101-159, 252-309.
2. **The mountain ghost.** Erika takes Ikki to Odoro Mountain for a ghost photograph; Koji and Karin are also visiting. Ikki falls into the river and reaches Kan-chan's isolated home. Her flying Medabots rescue him; she asks him to deal with troublesome strays. Her absent granddaughter Natsuko and missing Medabot Yanagi explain the apparent ghost: Yanagi is badly damaged and frightening people for parts. The Screws obstruct the investigation, while the Rubberobo Gang exploits the local Medabots. Phantom Retort takes Yanagi for repairs. Erika has been genuinely worried about Ikki drowning. Sources: `4F4654`, `4F7E64:0` onward; repair/Medaforce follow-up in `4F4B14:0-15`.
3. **Medabot Island: holiday, tournament, and missing children.** With his parents busy, Ikki feels neglected; Erika's family takes him to the amusement island. The tournament moves from local entrants to overseas guests and a final against Koji. Medal recovery and other detours interrupt the outing and can upset Erika. Ride photographs marked with circles are selecting children for abduction. The Witch's Castle attraction hides captive children; Salami wants to train children into more competent Rubberobo members. Ikki rescues them, then returns home with a renewed appreciation of his parents. Sources: `4F4B14` and `4F69DC`, including the international bracket at `4F69DC:42-63` and castle investigation at 80-267. Do not mistake this first visit for the later island trap.
4. **Medaropolis and Hanazono Academy.** Reports of a suspiciously capable Rubberobo member lead Erika and Ikki to the wealthy neighboring district. Ikki meets Kirara at the Medabot company, gains access and travel equipment, and encounters Dr. Hebereke as an apparently helpful expert. Karin's father initially shuts out her adventurous friends. Lonely rich boy Hachiro is stealing Medabots after a false academy head promises him friends. The real head is imprisoned; the gang takes over the academy and holds pupils hostage. Ikki and Koji cooperate to recover classroom keys and rescue Erika/Karin. Ikki later saves Hachiro from a fall and chooses kindness over punishment; Koji reluctantly accepts this. Sources: `4F5024`, `4F429C`, `4F6E38:100-145`, with callbacks in `4F54A0` and `4F7E64`.
5. **The children's kingdom underground.** Runaways near the station are recruited into the Rubberobo Gang and sent to cause trouble. Karua's quarrel with her parents makes the attraction of rebellion explicit. Ikki infiltrates the underground base, where the leaders plan uniforms with embedded Medals and new ranks. Children who try to quit are imprisoned. Ant Medabots feed and protect the prisoners and ultimately seek useful work with the children outside. The investigation opens a route toward ancient ruins beneath the city. Sources: `4F54A0`, `4F7950:180-241`, `4F5940:0-47`; some discovery/reporting lines recur in `4F7E64`.
6. **Kodain and its supposed monster.** A transporter in submerged ruins sends Ikki into an ancient kingdom, with Rubberobo intruders also present. Child queen Margarita is formal in public but playful in private. Her guardian Ginjo secretly abandoned her mischievous Medabot, Pousse-Cafe, in the sea; it became the feared Blue Hawaii. Ikki is treated as a prophesied hero, although arriving at the predicted time was coincidence. The gang attempts to trade Margarita for Surume's safety. Ikki rescues both sides and reunites the queen with her companion. The Fuyun Stone sustains the kingdom; its technology came from visitors from the sky. Hebereke steals the great stone while others are distracted. Sources: `4F5940`, `4F6E38:30-86`; later return visits in `4F74B4`.
7. **Fuyun, the flying fortress.** Forged date invitations lure Erika, Karin, or both into Hebereke's trap; these are alternative scene versions, not three successive kidnappings. The professor and Natalie supply flight equipment. Aboard Fuyun, Ikki meets Vodka, a courteous flying Medabot whom Hebereke repaired. Special oil and an alarm trigger loosen the Medabots' limiters, causing them to attack. Vodka struggles against the effect; a Medabot that missed lunch supplies the clue. Hebereke's use of the stolen stone imperils the fortress. Ikki and Koji divide pursuit and course correction, and humans and Medabots work together to prevent a crash onto Omikuji Town. Sources: `4F5D50`, `4F7950:0-179`, aftermath in `4F6E38:0-29`. The first rescue's romantic exchanges depend on the route.
8. **The second island visit and the real final battle.** New invitations bring the children to the closed amusement island as bait for Ikki. He returns using water-travel equipment, works with the Screws, recovers confiscated Medawatches, and frees his friends. The helpful white-coated company employee is exposed as Hebereke's data-leaking spy. Phantom Retort and Retort Lady confront the villain; God Emperor attacks Retort, exposing Henry and Kirara's identities in the ensuing crisis. Removed limiters allow attacks on people, even Hebereke himself. Ikki defeats the machines; Hebereke activates the base's self-destruct. Everyone must escape, including hostile people who keep delaying him. The professor confronts his old schoolmate; Tokkuri and the officers reject Awamori's theft of the children's credit. Sources: `4F6170`, `4F710C`, with invitation variants in `4F7E64`.
9. **Aftermath, friendships, and the Parts Rally.** Henry and Kirara discuss their past; optional meetings develop Erika/Karin's relationship with Ikki. A rally commemorating Hebereke's defeat asks entrants to assemble three Medabots, twelve parts total, through exploration and challenges. Old opponents, Kan-chan, Natsuko, Kodain, and the Screws recur. The prize ceremony turns into Shiratama's absurd creator-as-god challenge. Extra encounters include Mockingbird, Kawamuraa's autograph business, and Milky's future Medafighter guest. Sources: `4F65D8`, `4F74B4`, `4F7E64:208-295`, plus `4F710C` aftermath. These extras do not belong before the main villain's defeat.

## B. Shingata story, separately

Main source: `50A9D8`; field descriptions: `4B50CC`; character names and short voices: `46E60C`, `46D598`, `46E0F0`; mechanics instruction: `510124`. The following orders explicit story dependencies, not every optional excursion.

1. **Gamma becomes a Medafighter.** Walking Kamui leads into finding a Medal and reporting it to M-PK. Dad supplies/assembles the first Medabot. Iris, his childhood friend, is a major reason for his interest, though he cannot admit it. Masky, Pyorori, and Boyoyo bully other children; wealthy classmates Ryuki and Chiffon provide contrasting rivals. The chick seller teaches the basics. Sources: `50A9D8:12-13,154,169,184-188,619-646,741-746`; opening field text in `4B50CC`.
2. **School, local competition, and exploration.** Gamma progresses through neighborhood and district tournaments. His teacher sends the children exploring the beach, mountain/shrine area, and Fontana ruins. Rubberobo incidents include stolen parts, a monkey disguise, and activity around Oceano Tower, where Dad works. Masked heroine La Mascara repeatedly intervenes. M-PK publicly acts as protector; the mysterious alien presence is initially rumor and fragmentary encounters. Sources: `50A9D8:20-96,301-317,340-375,485-489,927-946,1046,1115,1134`; exploration order can vary.
3. **The main tournament and the mask.** Foreign guests join the competition; Ryuki is a semifinal rival and Dad is the surprise final opponent. Oro offers the champion a last battle. Before that confrontation, Oro threatens captive La Mascara; Iris's dropped phone exposes her identity, and Oro's speech exposes his connection to the Rubberobo boss. Gamma wins, but his Medabot explodes and its Medal cracks. Sources: `50A9D8:88-98,189-220`.
4. **Repair and the citywide crisis.** Normal repair methods fail. Ryuki remembers that a damaged Medal can revive in Fontana's lake under a full moon. Gamma sleeps there, hears enigmatic beings, and awakens with the Medal restored and an additional Medal. Yumari reports that only M-PK Medals are making Medabots run wild. Sources: `50A9D8:197-200,280-283,351-358,538`.
5. **Oceano Tower and the real aliens.** Captive workers reveal that M-PK Medals are designed to go berserk under a signal. Gamma disables the control/barrier systems, while friends and La Mascara help on the approach to Oro. Oro admits inventing an alien story to advance his scheme. After his defeat, the unfinished Duo Kaiser awakens, rejects orders, and fights solely to destroy. The tower collapses. Actual aliens save Gamma, explain that they gave humanity Medals, and terrify the disbelieving Oro. Officers arrest Oro as the Rubberobo boss; the chick seller sends Gamma home. Sources: `50A9D8:135-138,911-912,951-998,1000`. Optional Iris/Yumari relationship scenes must not be merged into one compulsory ending.

## Who is who: retained Ikki cast

Pronouns below are textual voice cues, not instructions to translate every first-person reference literally. Do not give all gang executives the rank-and-file's verbal suffix.

| Japanese name / label | English, role, relationships, and voice |
|---|---|
| イッキ / テンリョウ | Ikki; player `{var:00}` in the retained story. Enthusiastic, compassionate Medabot fan; Erika's childhood friend, Koji's rival, potential romantic partner of Erika or Karin. Usually boku, plain boyish speech; polite to adults, increasingly firm with villains. |
| アリカ / アマザケ | Erika; aspiring journalist and school-paper reporter. Drives investigations, bosses Ikki around, and hides affection behind teasing. Atashi; anta, yo/ne, brisk imperatives and indignant outbursts. Her concern is real, not just bullying. |
| コウジ / カラクチ | Koji; Hanazono rival and Karin's childhood companion/protector; also knew Hachiro as a child. Ore, omae, ze/zo, rough contractions; proud and competitive but dependable in emergencies. |
| カリン / ジュンマイ | Karin; wealthy, physically frail Hanazono pupil, much more adventurous than her father permits. Watashi/watakushi; desu/masu, wa, courteous requests. Gentle, not helpless; challenges her father and chooses outings herself. |
| キクヒメ | Samantha; leader of the Screws. Atashi, drawn-out vowels and yo/ne; languid, theatrical threats and fashion concerns. Can protect her followers and help Ikki. |
| イワノイ | Sloan, using the requested mapping; Samantha's outspoken subordinate. Ore; rough ze, anego for his boss, deferential -ssu toward her. Plots tricks and handles useful information/doors. |
| カガミヤマ | Spyke, using the requested mapping; the other Screw. Boku; short, comparatively flat statements, recurring concern about dirty clothes and laundry. |
| スクリューズ | The Screws; the three-person bully team. Their claim that all three count as one opponent rationalizes unfair consecutive fights. |
| パパ / ママ | Ikki's parents; Dad encourages his hobby and installs the Medal, Mom handles discipline and domestic errands. Dad uses papa as self-reference; Mom similarly mama. Warm family speech, with Mom's sharp scolding. Do not import Shingata's parental names. |
| ソルティ | Salty; Ikki's dog. Barks and growls, not literal spoken sentences. Friends repeatedly remind Ikki to care for a living pet as well as Medabots. |
| アリカのママ | Erika's mother; supportive adult who teases about dating and brings Ikki on the island trip. Familiar feminine speech. |
| カリンのおとうさま / おかあさま | Karin's parents; her father is overprotective, then apologetic and grateful after the rescue. Respectable adult speech; her mother uses notably genteel phrasing. |
| ハチロウ / アワノ | Hachiro Awano; lonely rich boy manipulated into theft, later an ally/rally opponent. Boku, affected sa/yo and smug familiarity; frightened crying exposes the child beneath the pose. |
| ヒツジ / しつじ | Hachiro's butler; loyal and aware of the boy's loneliness. Watakushi, elaborate honorific humility, obocchama. Hachiro's hitsuji address plays against shitsuji, 'butler'; do not assume a new animal character. |
| がくえんちょう | Hanazono Academy head; impersonated and confined, then grateful; owns a secret Medal collection. Watashi, authoritative adult plain speech. Distinguish real and false head from scene context. |
| シラフせんせい | Mr. Shirafu; Hanazono teacher who tries to recover a confiscated Medawatch for a pupil. Sincere ordinary adult speech, not a villain. |
| メダロットはかせ / アキハバラ | The Medabot professor, Akihabara; Natalie's grandfather, Henry/Kirara's old acquaintance, Hebereke's former schoolmate. Washi, ja/no/zoi; gruff, proud, evasive about his helpers. |
| ナエ | Natalie; professor's granddaughter and researcher developing the Elemental series. Watakushi, desu/masu, wa; gracious, encouraging, capable. Gives Medals/prototypes and knows more about Ikki's exploits than she initially explains. |
| ヒカル / かいとうレトルト | Henry / Phantom Retort; ordinary friendly young man and masked helper, identities united late. Henry uses boku; Retort uses watashi, booming laughter, grand entrances and shonen address. Childhood friend of Kirara; hero of an incident seven years earlier. |
| キララ / レトルトレディ | Kirara / Retort Lady; company office worker and undercover ally. Everyday atashi/watashi, lively familiar speech; masked entrances parody heroic speeches. Childhood friend of Henry, not Natalie. |
| メタビー / ロクショウ | Metabee / Rokusho; Henry's Medabots in version-dependent battle lines. Metabee's brief entrance is swaggering; Rokusho announces himself formally with mairu. Do not assign both entrances to one version's scene. |
| ヘベレケはかせ | Dr. Hebereke; helpful-seeming scientist, then mastermind. Washi, onushi, ja/no, loud laughter and wounded vanity. Wants acclaim and female admiration and resents Akihabara's success. |
| はくい | The white-coated company employee; gives travel equipment before being exposed as Hebereke's spy. Watashi, friendly explanatory speech, disturbingly casual even when caught. Shared generic appearance is part of the joke. |
| アワモリ | Captain Awamori, Select Corps commander; obstructive, pompous and eager to steal credit. Washi, kisama, emphatic ja endings, often capitalized in Japanese. His men eventually repudiate him. |
| トックリ | Deputy Tokkuri; initially follows Awamori, later objects to taking children's credit. Polite subordinate speech, watashitachi in the collective protest. |
| セレクトたい / セレクトスリー | Select Corps / Select Three; public protectors, often ineffectual. Jibun and military de arimasu; literal-minded misunderstandings and rigid procedure. Not Shingata's M-PK force. |
| ロボロボ団 | Rubberobo Gang; rank and file use ore or wareware and append robo, including to protests and excuses. The costume makes people mistake Ikki for a criminal. |
| サケカース | Sakekasu; commanding gang boss under Hebereke. Oresama, grandiose threats and laughter; takes humiliation personally. Strong adult arrogance, not baby talk. |
| スルメ | Surume; female executive, status-conscious and vain, with a luxury habit and other work. Watakushi, desu wa/koto yo, ohoho laughter; exaggerated high-society manners. Subordinates care about rescuing her. |
| シオカラ | Shiokara; elderly executive involved in the skirt incident and child recruitment. Washi, ja/no, wheezing coughs and fofo laughter; dodges responsibility and complains about children. |
| サラミ | Salami; child executive who wants children trained as gang members. Atachi; deshu, mashu, shen and other baby substitutions. Juvenile articulation coexists with calculating cruelty. |
| カルア | Karua; runaway girl recruited into the gang, resisting pressure to study. Ordinary sharp feminine speech with awkwardly added robo; not one of the four established executives. |
| カンちゃん | Kan-chan; Natsuko's grandmother on Odoro Mountain. Atashi, rough elderly familiarity, cackling hihihi; insists on her nickname rather than 'grandma'. Menacing hospitality masks practical kindness. |
| ナツコ | Natsuko; Kan-chan's granddaughter, away working in Medaropolis, associated with Yanagi's backstory. Watashi; warm polite conversation. The kimono/letter exchange confirms the family connection. |
| ヤナギ | Yanagi; damaged Medabot behind the ghost scare, once helped lost Natsuko. Oira, distorted/katakana robot speech; boasts that his battered appearance is fashionable. |
| マルガリータ | Margarita; child queen of Kodain. Public ceremonial speech is learned; privately self-refers by name, asks childish questions, evades lessons, and adores her Medabot. Calls Ikki the hero. |
| ギンジョウ | Ginjo; Kodain chancellor, Margarita's guardian/'Jiiya', prone to dozing. Washi, deferential desu ja, courtly address. Secretly responsible for disposing of her Medabot. |
| ジョウゾウ | Jozo; high priest of Kodain, responsible for prophecy/transport and preserving the temple with the stone. Ceremonial, deferential court speech. Do not confuse him with Ginjo. |
| プース・カフェ / ブルーハワイ | Pousse-Cafe / Blue Hawaii; Margarita's companion and its feared monster identity. Boku, broken mixed-kana speech; wants Margarita back. The monstrous demand for a sacrifice precedes the vulnerable explanation. |
| モッキンバード | Mockingbird; later part-stealing relative of Pousse-Cafe. Margarita's sprawling family explanation is intentionally hard to follow; do not simplify it into a firmly established sibling. |
| ウォッカ | Vodka; Fuyun's Medabot coordinator, named and repaired by Hebereke. Watashi, desu/masu and -san; unfailingly courteous and grateful, even while resisting dangerous commands. |
| キール | Kir; prince representing the Shochu Kingdom. His brief foreign utterances are unintelligible to Ikki; preserve that fact rather than inventing translated exposition. |
| シャンデー | Shandy; American tournament guest with trademark sunglasses. Enthusiastic boasts and conspicuous English catchphrases. |
| スプモーニ | Spumoni; Russian/Siberian entrant, uncomfortable in the heat. Terse, forceful katakana speech; no need to invent a heavy phonetic accent. |
| テキーラ | Tequila; flamboyant guest from a Latin country. Comic me/atashi pronoun switching and ne; awkward Japanese is explicitly commented on. Recreate the muddled bravado without arbitrary ethnic spelling. |
| ジョー・スイハン / ジャー・スイハン | Joe Suihan and his father Dr. Jar Suihan; research/development pair. Joe is a courteous tournament guest and treats defeat as research. Their names also invoke a rice cooker. |
| リョウ | Ryo; wandering theatrical justice-minded challenger, later a race opponent. Ore, grand threats and fatalistic surrender; Ikki punctures the drama with practical replies. |
| ミルキー | Milky; sugary witch persona associated with the castle attraction, child collecting, and magical bonus encounters. Watashi/name self-reference, elongated girlish delivery and absurd spells. Her last Henry/mask remark is suggestive, not an explicit unmasking as Kirara. |
| シラタマ | Shiratama; absurd postgame intruder claiming to be the game's creator and god. Watashi, pompous declarations; humiliatingly weak. Natalie takes responsibility for removing him. |
| カワムラー | Kawamuraa; boastful cameo obsessed with status, a new car, and his autograph. Ore, pushy adult bragging; a later 'admirer' sounds suspiciously like him. |
| コイ... | Unnamed future Medafighter; starts to give his name, then refuses. Ore, boastful but friendly. Preserve the interrupted name; do not expand it from franchise knowledge. |

## Who is who: Shingata cast

Names checked against `46E60C`. These are separate people, even where a retained portrait slot or scene pattern resembles the Ikki cast.

| Japanese name / label | English, role, relationships, and voice |
|---|---|
| ガンマ | Gamma; Shingata's default player name, replaced by `{var:00}`. Ore, plain energetic speech, sharper comebacks than retained-story Ikki's boku. Initially plays partly to impress Iris. |
| アイリス | Iris; Gamma's childhood friend, coach, teasing romantic interest, and secret helper. Watashi/atashi, anta, yo/ne, brisk orders; affectionate confidence rather than Karin's formality. |
| ラ・マスカーラ | La Mascara; Iris's masked persona. Watashi, flamboyant heroic introductions, poses and emphatic denials. The phone reveal comes before her late-game jokes about already being recognized. |
| リューキ | Ryuki; wealthy classmate, self-proclaimed eternal rival, linked to the Medabot company. Boku, kimi, condescending remarks about commoners and refinement. Helps with the broken Medal despite rivalry. |
| シフォン | Chiffon; wealthy classmate close to Ryuki, devoted to her bear Betty. Watashi/name self-reference, desu wa, babyishly sweet -chan address. Pushes Gamma into Robattles while pretending Betty requested them. |
| ベティ | Betty; Chiffon's bear, treated by Chiffon as making requests and wanting to compete. Do not turn Chiffon's claims into independently verified speech by Betty. |
| マスキー | Masky; boss of the local bullying trio. Atashi, rough commands, anego to followers; mixes girlish taunts with tough-guy delivery. Eventually helps at the tower. |
| ピョロリ | Pyorori; talkative subordinate, rough male colloquial speech, respectful -ssu to Masky. |
| ボヨヨ | Boyoyo; hulking subordinate. Ore, very short broken clauses, growls, and repeated echoes of the previous speaker's ending; others notice and mock the echoing. |
| マンソン | Manson; Gamma's father, works at Oceano Tower and is a formidable Medafighter. Papa self-reference, warm explanatory authority; the surprise tournament finalist. |
| マミーア | Mamiia; Gamma's mother, domestic guide and source of the Kamui-walking errand. Familiar parental speech and gentle commands. |
| カムイ | Kamui; Gamma's dog, prompts exploration and receives Iris's apparent 'thank-you kiss'. Barking only; distinct from Salty. |
| ユマリ | Yumari; courteous researcher who asks Gamma to test parts, likes stars, and can show romantic interest. Watashi, desu/masu, hesitant unfinished invitations. Reports the M-PK Medal pattern. Not Koji despite face `0004`. |
| メダロットはかせ | Medabot professor; boasts about developing Medabots and provides research/collection rewards. Washi, ja/no, hoho laughter. Do not automatically attach retained-story family relationships. |
| ソンチョー | Soncho, the village chief; elder with item requests, including food to accompany a drink and clay for pottery. Elderly ja/no speech. |
| ひよこうり | Chick seller; recurring rough-spoken tutorial mentor, unusually well informed about M-PK and the finale. Ore, bozu, clipped informal explanations. His deeper role is hinted at, not named in the sampled reveal dialogue. |
| オーロたいちょう / ロボロボだんボス | Captain Oro / Rubberobo boss. Public heroic commander of M-PK; secretly directs the plot. Watashi, pompous authority, sinister laughter and threats. His matching manner of speech is a recognition clue. |
| アマリロ | Amarillo; child Rubberobo executive, uses a monkey disguise and ambushes Ryuki. Atachi, deshu and infantile pronunciation; being physically present but unseen is a joke. |
| アズル | Azul; Rubberobo executive associated with stolen parts and beach trouble. Atashi, contemporary slang, cho-, jan, drawn-out complaints; shamelessly claims stolen property as her own. |
| ロジョ | Rojo; Rubberobo executive at the tower and other hideouts. Watakushi, desu wa/koto, ohoho laughter; insists on 'big sister' treatment and belittles Gamma as a child. |
| MーPKたい | M-PK force; nominal public defenders. Rank-and-file military de arimasu; do not reveal the commander's conspiracy in early innocent service dialogue. |
| ブリレッツ / テラ / ラシオネ / ビオラ / コテツ / モレア | Suggested Brilets, Terra, Rasione, Viola, Kotetsu, Morea; named competition/NPC roster. Brilets is introduced as the previous European champion, Terra as an African guest, Viola as a glamorous entrant. Treat short battle lines individually; no unsupported family links or invented accents. |
| こうちょう / ほけん・としょ・おんがく・たいいく・りかのせんせい | Principal and health/library/music/PE/science teachers; roles rather than personal names. The energetic excursion-giving teacher repeatedly calls himself sensei and ends with zo. The science teacher's Medal experiment produces alarming smoke. |
| ホリウチー | Horiuchii; named cameo in the character roster. Keep distinct from retained-story Kawamuraa; the sampled story does not establish a major plot role. |
| グレイ / デュオカイザー | Grey / Duo Kaiser; actual alien visitor(s) and the destructive late boss. Alien speech is fragmentary, solemn and katakana-heavy; Duo Kaiser uses watashi and repetitive destruction declarations. |

## Reveal timing and translation traps

- **Retained story:** Hachiro is manipulated, not an irredeemable gang mastermind. Preserve the false head's apparent authority until the captive real head explains it (`4F429C:73`).
- **Retained story:** the ghost is Yanagi; Natsuko is Kan-chan's granddaughter; Blue Hawaii is abandoned Pousse-Cafe. Preserve the initial uncertainty and the later emotional reframe (`4F4654`, `4F5940:135-138`).
- **Retained story:** Hebereke first gives useful advice. His vanity and rivalry explain later wrongdoing; do not make every early line overtly villainous.
- **Retained story:** Henry/Retort and Kirara/Retort Lady become explicit at `4F710C:101-107`. Natalie knows their work; that does not make her Retort Lady. The white-coated employee's betrayal is exposed at 74-77.
- **Retained story:** Milky's Henry reference and the future visitor's truncated name remain hints. Do not turn either into a definitive identity statement (`4F7E64:293-295`).
- **Retained story:** the Fuyun and final-base scenes include Erika-only, Karin-only, and combined alternatives. Translate the actual speakers and affection level, not a single imagined canonical route.
- **Shingata:** Iris's phone connects her to La Mascara (`50A9D8:205,218-220`); preserve her earlier denials. Oro's boss identity is explicit by the hostage scene, before the tower confession.
- **Shingata:** Oro's invented alien story and the real aliens are deliberately different revelations (`50A9D8:989` versus 135-138). The heroes' uncertainty must survive until the rescue.
- **Shingata:** M-PK Medals, not every Medal, contain the berserk mechanism (`50A9D8:281,951`). The retained story's limiter/oil explanation is a separate plot and must not be substituted.

## Places and suggested English

| Japanese | Suggested English and context |
|---|---|
| おみくじまち | Omikuji Town; Ikki's home, threatened by falling Fuyun. |
| おどろやま / おどろいけ | Odoro Mountain / Odoro Pond; ghost investigation area. Retain the shared stem. |
| メダロポリス | Medaropolis; neighboring urban district. |
| はなぞのがくえん | Hanazono Academy; Karin, Koji, and Hachiro's school. |
| メダロットけんきゅうじょ / メダロットはくぶつかん | Medabot Research Institute / Medabot Museum. |
| メダロットしゃ / メダロットカンパニー | Medabot Company; check story set before assigning employees. |
| メダロッターズ | Medafighters' Center; service venue/organization, Medalink and rally context. |
| セレクトほんぶ | Select Corps HQ; retained story. |
| メダロッとう | Medabot Island; amusement island, with a name that blends Medabot and 'island'. |
| ビックリサイト | Surprise Site; tournament venue, with a possible Big Sight sound joke. |
| まじょのしろ / ミルキーランド | Witch's Castle / Milky Land; attraction and associated fantasy setting. |
| こどもおうこく / しん・こどもおうこく | Children's Kingdom / New Children's Kingdom; gang scheme and later Screws takeover. |
| コーダインおうこく | Kingdom of Kodain; ancient civilization. The name evokes 'ancient'. |
| フユーン / フユーンストーン | Fuyun / Fuyun Stone; flying fortress and levitation power source. Preserve the connection. |
| ショーチューおうこく | Kingdom of Shochu; Kir's island homeland, liquor-name joke. |
| ボナパルトのぞう | Bonaparte Statue; meeting landmark, not a newly introduced speaking character. |
| ベント・デル・マーレ / ベント・ベルマーレ | Vento del Mare; Shingata home district. Both forms occur in dialogue; standardize only after checking map labels. |
| ビーチ・デル・ソル | Beach del Sol; coastal exploration area. |
| セントラル・モール / ヴォーグ・タウン | Central Mall / Vogue Town. |
| オセアノ・タワー | Oceano Tower; Dad's workplace and final enemy stronghold. |
| フォンタナいせき | Fontana Ruins; lake, alien encounters, and Medal restoration. |
| サザンコロシアム | Southern Colosseum; main tournament venue. |
| しのびのさと / てんたいドーム | Ninja Village / Observatory Dome; exploration sites. |
| MーPKたい ベント・デル・マーレ しぶ | M-PK Vento del Mare Branch; Shingata public-security office. |

## Running jokes and wordplay

- Alcohol names connect many retained-story people: the principal cast's surnames, gang names, Hebereke ('blind drunk'), Shirafu ('sober'), Awamori, Tokkuri, Ginjo, Jozo, and the cocktail cast. Preserve recognizable drink names where possible; explain no joke inside dialogue unless the original does.
- Retort curry and Phantom Retort share a name; the shopping errand makes the hero's grand title funnier. Retort Lady's rice-flower entrance extends the food imagery.
- Retained-story authority repeatedly takes credit for Ikki's work. Erika's newspaper can praise the wrong people while she dismisses the real hero; the final officers' protest pays this off.
- Robo is contagious enough that a transport Medabot claims to have acquired it from customers. It is a clue, not infallible proof of gang membership. Ant Medabots instead use ari endings.
- The mountain pun says the speaker is 'mountainously' eager to visit the mountain; a gang member later accuses Ikki of stealing this masterpiece (`4F54A0:215`). Use one consistent English joke for setup and callback.
- Cross-dressing embarrasses Ikki long after Erika's skirt-bait scheme; Koji keeps finding opportunities to mention it. The joke depends on who witnessed the disguise and who has not heard about it.
- Parts/pants confusion recurs during the Parts Rally; the lemon-pack item is mistaken for a facial treatment. Do not silently repair the deliberate mishearings.
- Hachiro is offended at not being kidnapped because rich children 'ought' to be targets. Ryo's epic threats collapse against Ikki's deadpan refusal to play along.
- Public versus private speech matters: Margarita's queenly vocabulary collapses into little-girl speech; Salami/Amarillo's baby diction conceals calculating plans; Vodka remains polite under terrible strain.
- Shingata's Boyoyo echoes sentence tails, even when the group thinks its scene has ended. La Mascara poses toward the audience, insists Iris is 'cute', and complains that Gamma is spoiling his own final-boss entrance.
- Shingata's chick seller jokes about colored chicks and the chicken/egg problem while hinting at the relationship between M-PK and Rubberobo. Gamma's hoped-for kiss is for Kamui instead; preserve the delayed barking reveal.
- Both sets break the fourth wall. Shiratama claims creator-god status, Surume invokes the digital world, and Gamma recognizes the extra-boss pattern. These are explicit jokes, not translator commentary.

Terminology throughout: Medabot, Medafighter, Medawatch, Robattle, Tinpet, Medaforce, and Rubberobo Gang. Keep control codes and player-name variables intact when applying this guide to actual translations.
