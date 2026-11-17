# Character voice reference

Use this alongside [the synopsis](synopsis.md) to review a whole chapter: compare register, recurring tics, relationships and changes under stress, while preserving reveal timing. [The glossary](../glossary.md) controls spellings; [decisions D1-D2, D10 and D13](decisions.md) control naming and this reference. Keep hyphenated honorifics, including addressed teachers' **-sensei**, and Western name order (given name first).

Examples quote the shipped `en` in `script/<table>.json`; references are **table:string id**, not row numbers. Short excerpts omit surrounding dialogue and display controls; `{n}`/`{page}` become spaces, while variables stay intact. These are voice anchors, not permission to copy a line's context into another scene. JP cues are romanized without macrons; pronouns guide register, not compulsory English wording.

Face IDs are the first four digits of `{face:XXYYZZ}`. They are **cast-local and not unique speaker identifiers**: generic portraits, disguises and even some named speakers share them. Attribute dialogue from the scene and JP as well as the portrait. The two protagonists use `{var:00}`; never substitute their default names in script. Keep English plain and lively, preserve audible tics, and do not invent accents or disclose identities early.

## Retained Ikki story — 4F… tables

| Character | Face id(s) | Voice in JP (romanized: quirks, register, sentence endings) | English voice rule | Example approved line (id + English, quoted from script/) |
|---|---|---|---|---|
| Ikki | `0100` | Boku; plain boyish speech; polite to adults. | Earnest, compassionate, occasionally deadpan; firm against cruelty. | `4F429C:4BB85C` “I can't forgive anyone who uses Medabots to do bad things!” |
| Erika | `0002` | Atashi, anta; yo/ne; brisk orders. | Pushy reporter, sharp teasing; let genuine concern show. | `4F3C84:4B8E8E` “I'm going to be a journalist, you know!” |
| Koji | `0004` | Ore, omae; ze/zo; rough contractions. | Proud, blunt rival; protective and reliable in danger. | `4F429C:4BF555` “I won't forgive anyone who put Karin in danger.” |
| Karin | `0003` | Watashi/watakushi; desu/masu, wa. | Gentle, courteous and self-directed; no helpless-baby voice. | `4F4B14:4C672F` “Yes, I've had plenty of rest.” |
| Samantha | `0006` | Atashi; yo/ne; stretched vowels. | Languid, theatrical bully; fashion-conscious, loyal to her crew. | `4F3C84:4B9531` “Waaait a minute!” |
| Sloan | `0007` | Ore; ze; anego; deferential -ssu. | Rough, talkative henchman; respectful to his boss. | `4F3C84:4BA4EA` “I couldn't leave the boss all alone!” |
| Spyke | `0008` | Boku; short flat statements; laundry fixation. | Understated, literal; keep the clothes/laundry callbacks. | `4F3C84:4B9649` “I'll make you do the laundry someday.” |
| Dad | `004F` | Papa self-reference; warm family register. | Affectionate, encouraging father; not Manson by name. | `4F3C84:4B8792` “Make sure you listen to your mom too, son.” |
| Mom | `0050` | Mama self-reference; familiar scolding. | Domestic warmth with sharp, practical discipline. | `4F3C84:4B855C` “Honestly! You're always running off!” |
| Salty | `0005` | Wan, whines and growls. | Dog sounds only; never translate them into dialogue. | `4F3C84:4B85A1` “Woof! Woof!” |
| Erika's mother | `0024` (shared) | Familiar feminine requests; ne. | Warm, sociable adult; teasing about dating stays gentle. | `4F3C84:4B8B81` “Be a good friend to Erika, won't you?” |
| Koji's mother | `0024` (shared) | Polite greetings; familiar ne. | Welcoming parent, straightforward courtesy. | `4F5024:4C90F0` “I'm sorry, dear. Koji is out right now.” |
| Karin's father | `0017` (shared) | Respectable adult plain speech; protective commands. | Overprotective authority softens into relief and gratitude. | `4F429C:4BF482` “Karin! Thank goodness! I was so worried.” |
| Karin's mother | `004D` (shared) | Yoroshii, wa; genteel honorific phrasing. | Composed, gracious, slightly formal maternal warmth. | `4F5D50:4D3769` “Do have a lovely time together.” |
| Household servants | `0018` (shared) | Gozaimasu, kudasaimase; respectful titles. | Courteous service; retain the household's honorific distinctions. | `4F5D50:4D36D6` “One moment, please. Madam!” |
| Hachiro Awano | `0009` | Boku; affected sa/yo; childish crying. | Smug rich-boy poise collapses into frightened vulnerability. | `4F429C:4BECB8` “Sniff... Sob...” |
| Hachiro's butler | `000A` | Watakushi; obocchama; elaborate humility. | Deferential, loyal; preserve the hitsuji/shitsuji joke's context. | `4F429C:4BC0F2` “Well, well! Are you a friend of the young master's?” |
| Hanazono headmaster | `0017` (shared) | Watashi; authoritative plain adult speech. | Distinguish the real collector from the impostor by scene. | `4F429C:4BEF60` “Those scoundrels! My collection!” |
| Shirafu-sensei | `0017` (shared) | Ordinary sincere adult speech. | Concerned teacher, not a sinister authority figure. | `4F429C:4BD375` “I see... It's a shame, but I'd better go and tell her.” |
| School principal / elder teacher | `0019` (shared) | Ja, zo; hearty laughter. | Genial educational authority; energetic encouragement. | `4F3C84:4BA337` “Study hard and Robattle hard, children! Hahaha!” |
| Dr. Aki | `0013` | Washi; ja/no/zoi. | Proud, gruff elder scientist; evasive about his helpers. | `4F3C84:4B7E4A` “I'm a busy man, you know.” |
| Natalie | `0014` | Watakushi; desu/masu, wa. | Gracious, capable researcher; encouraging without condescension. | `4F3C84:4B7CFC` “How do you do? My name is Natalie. And what is your name?” |
| Henry | `000E` | Boku; friendly everyday register. | Approachable young shop worker; weary humor stays casual. | `4F3C84:4B8C74` “Whew. The manager really gave me an earful.” |
| Phantom Retort | `000D` | Watashi; shonen; booming laughter. | Grand heroic entrances and mock dignity; protect the Henry reveal. | `4F3C84:4B891F` “Today, I appear before you bearing gifts!” |
| Kirara | `0012` | Atashi/watashi; lively familiar speech. | Friendly, knowing office worker; do not merge her with Natalie. | `4F5024:4CA046` “Oh? I haven't seen you before.” |
| Retort Lady | `0011` | Parodic heroic declarations. | Flamboyant masked rescuer; keep food-themed entrance jokes. | `4F5024:4CB005` “Shame on you!” |
| Metabee | `0010` | Casual, swaggering male speech. | Brash and colloquial; respect version-dependent scenes. | `4F5024:4CAACA` “I dunno about that...” |
| Rokusho | `000F` | Formal phrasing; mairu in entrance. | Restrained, dignified; do not borrow Metabee's swagger. | `4F5024:4CAAEE` “Y-yes, indeed...” |
| Dr. Meta-Evil | `003C` | Washi, onushi; ja/no; loud laughter. | Elderly scientific authority turns vain and grandiose. | `4F429C:4BB8D5` “Let's see just how far you can go, my boy.” |
| White-coated employee / spy | `001B` (shared) | Watashi; friendly explanations. | Helpful professional patter, disturbingly casual after exposure. | `4F6170:4D762C` “Yes, yes, a "Periscope", right? We have one here.” |
| Captain Awamori | `003F` | Washi, kisama; emphatic ja. | Pompous, obstructive credit-stealer; loud self-importance. | `4F3C84:4BB514` “Others do the work, and I take the credit!” |
| Deputy Tokkuri | `0040` | Polite subordinate register; watashitachi. | Dutiful officer; growing moral objection must remain sincere. | `4F3C84:4BB592` “I thought I sensed someone here...” |
| Select Corps | `003E` (shared) | Jibun; military de arimasu. | Stiff procedural courtesy and literal-minded misunderstandings. | `4F429C:4BD9ED` “If you're having trouble, we're always ready to listen!” |
| Select Three | `0028`, `0032`, `002E` (shared) | Hero-team slogans and emphatic introductions. | Hammy coordinated poses; preserve individual boasts. | `4F3C84:4B909B` “Together, we three are Select Three!!” |
| Rubberobo rank and file | `0036`, `003B` (shared) | Ore/wareware; sentence-final robo. | Keep “, robo” / “-robo” in threats, excuses and panic. | `4F3C84:4BB352` “Good work, robo. Flip more skirts and brighten up the world, robo!” |
| Seaslug | `0037` | Oresama; grand threats and laughter. | Arrogant adult commander; do not mechanically add grunt robo. | `4F429C:4BF064` “I am Seaslug, boss of the Rubberobo Gang! Remember that!” |
| Shrimplips | `0038` | Watakushi; desu wa/koto yo; ohoho. | Vain high-society villainess; elegant contempt and luxurious tastes. | `4F429C:4BE9B8` “Oh ho ho! How dare you pick on my darling henchmen!” |
| Squidguts | `0039` | Washi; ja/no; coughs, fofo. | Wheezy, evasive old schemer; keep age and responsibility-dodging. | `4F429C:4BE579` “Ho ho ho! A lively young lass, eh?” |
| Salami | `003A` | Atachi; deshu/mashu/shen. | Audible baby articulation masking calculated cruelty. | `4F4B14:4C3C7A` “We need more Rubberobo membersh!” |
| Kahlua | `0022`; costume by context | Sharp feminine speech; awkward added robo. | Rebellious child trying on gang manners, then shy gratitude. | `4F54A0:4CDE96` “Um, thank you. Uh...” |
| Kan-chan | `001A` (shared) | Atashi; rough elder speech; hihihi. | Cackling, intimidating hospitality with practical kindness. | `4F4654:4C153C` “All right. If you want to know, I'll tell you.” |
| Natsuko | `0024` (shared) | Watashi; warm polite conversation. | Kind, adult familiarity; preserve her connection to Kan-chan. | `4F65D8:4DCF64` “Oh, so that was you! Grandma wrote about you in her letter.” |
| Yanagi | `002A` (shared) | Oira; distorted, katakana-heavy robot speech. | Battered but personable; simple direct phrasing, not mindless menace. | `4F65D8:4DCC3D` “Kan-chan scolded me. I'll wait here for Natsuko to come home.” |
| Margarita | `0041` | Ceremonial public diction; private name self-reference. | Learned queenly speech gives way to an ordinary little girl. | `4F5940:4CFCCA` “Then, O hero, we entrust this to thee.” / `4F5940:4CFD02` “You'll come play with me, right? Promise?” |
| Ginjo / Jiiya | `0045` (shared) | Washi; desu ja; deferential court address. | Drowsy elder guardian; courtly but personally protective. | `4F5940:4D0257` “Hmm, I see... You have bested this old man, Princess.” |
| High Priest Jozo | `0045` (shared) | Ceremonial requests; desu ja, no. | Ritual authority and deferential concern; distinguish from Ginjo. | `4F5940:4D2C1A` “Ah, noble hero! Have you found Her Highness, eh?” |
| Pousse Cafe / Blue Hawaii | `0042` (shared) | Boku; broken mixed-kana speech. | Menacing monster demand precedes lonely, vulnerable childlike speech. | `4F5940:4D01DB` “I was so lonely.” |
| Mockingbird and lookalike relatives | `0042` (shared) | Playful calls; stretched vowels. | Mischievous, buoyant; do not simplify the tangled family explanation. | `4F74B4:4E998C` “Yup, that's meee! Do you like the sea too?” |
| Vodka | `0028` (shared) | Watashi; desu/masu; -san. | Unfailingly courteous and grateful, including under pressure. | `4F7E64:4F37CD` “You're most welcome. Please make yourself at home.” |
| Kir | `0046` | Unintelligible foreign syllables. | Preserve Ikki's inability to understand; no invented exposition. | `4F4B14:4C52FD` “...! Da?!! ...Gi.” |
| Shandy | `0047` | Showy English catchphrases; enthusiastic boasts. | Flashy tournament confidence; no fabricated phonetic accent. | `4F69DC:4DEB27` “America's the hottest country for Medabots!” |
| Spumoni | `0049` | Terse, forceful katakana delivery. | Blunt competitor, irritable in the heat; avoid accent caricature. | `4F69DC:4DEBDB` “Can't stand this heat. Let's finish this quickly!” |
| Tequila | `004A` | Me/atashi switching; ne; awkward Japanese. | Flamboyant, muddled bravado; preserve the language joke. | `4F4B14:4C5169` “When I meet you, it is Robattle fight, yes!” |
| Joe Suihan | `0048` | Courteous technical register. | Research-minded competitor; defeat is useful data. | `4F69DC:4DED4C` “I concede. I hope to use our Robattle to further my Medabot research.” |
| Ryo | `004B` | Ore; epic threats, fatalistic surrender. | Overblown justice melodrama for Ikki to puncture. | `4F4B14:4C4B92` “Take this! My iron fist of fury!” |
| Milky | `000C` (shared) | Watashi/name self-reference; elongated girlish delivery. | Sugary witch act, silly spells; keep menace and identity hints contextual. | `4F6170:4D7E8F` “Hiii! How is everyone? It's your adorable witch, Milky!” |
| Shiratama | `001B` (shared) | Watashi; pompous creator declarations. | Explicit fourth-wall god complex, then humiliating weakness. | `4F65D8:4DBAE3` “I created this game! I am as a god!” |
| Kawamuraa | `0017` (shared) | Ore; pushy status boasting. | Obnoxious adult self-promotion; not Shingata's Horiuchi. | `4F65D8:4DD8E1` “I've made it big, so I bought a new car! Jealous, aren't you!?” |
| Future Medafighter, “Koi...” | `0061` | Ore; boastful but friendly; interrupted name. | Keep his name unfinished and his origin teasingly vague. | `4F7E64:4F3A35` “I'm Koi... Th-that's not important!” |
| Three Ninja Brothers | `001C`, `001D`, `001E` | Sessha; de gozaru; formal self-announcements. | Ceremonial martial bravado; distinguish each brother's introduction. | `4F4654:4C0399` “Tejaku the Gale of the Three Ninja Brothers! I arrive as swiftly as the wind!” |
| Ninja Mansion ninjas | `001F`, `0027` (shared) | De gozaru; respectful challenges. | Theatrical, old-fashioned courtesy; clear puzzle instructions. | `4F74B4:4EA091` “Well done finding me! But can you best me in battle?” |
| Ant Medabots | `002C` | Sentence-final ari. | Preserve “, ari”; never replace with robo. | `4F54A0:4CEB2A` “This food is strong, ari! I'll go get backup, ari!” |
| Transport Medabot | `0034` | Borrowed sentence-final robo. | Matter-of-fact service with the tic; tic alone does not prove gang membership. | `4F4654:4C01CD` “I'll give you a ride for 100 yen, robo.” |
| Secret-base convenience clerk | `0056` | Stretched deesu/maasu service patter. | Cheerful retail sing-song amid an absurd location. | `4F54A0:4CEB65` “We look forward to seeing you agaaain!” |
| Catlike Medabot | `002F` (shared) | Nyaa endings in the catlike scene. | Use “meow” where present; do not spread it to other users of this face. | `4F4B14:4C41DF` “Hey! What are you doing barging into someone's house, meow?” |
| Tournament announcer | `004E` | Public address; excited questions and introductions. | Big sporting energy; names and results stay clear. | `4F4B14:4C53A9` “Ladies and gentlemen! Are you having fun!?” |

## Shingata Gamma story — 50A9D8 and related 50… / 51… tables

| Character | Face id(s) | Voice in JP (romanized: quirks, register, sentence endings) | English voice rule | Example approved line (id + English, quoted from script/) |
|---|---|---|---|---|
| Gamma | `0100`; `0101` in costume | Ore; ze; energetic, rougher comebacks. | Confident, impulsive and quick-witted; wants to impress Iris. | `50A9D8:4FCF5F` “What makes you think I'm new to Medabots?” |
| Iris | `0002` | Watashi/atashi, anta; yo/ne; brisk orders. | Affectionate confidence and teasing coaching, not Karin's formality. | `50A9D8:4FCF16` “Looking good! Keep it up!” |
| La Mascara | `0003` | Watashi; heroic declarations, emphatic denials. | Flamboyant posing; retain the Iris reveal and later recognition jokes. | `50A9D8:508F9D` “The beautiful Medafighter from the heavens, La Mascara...” |
| Yumari | `0004` | Watashi; desu/masu; hesitant invitations. | Courteous, capable researcher; shy romantic pauses. Not Koji. | `50A9D8:4FD38C` “May I come over and play sometime?” |
| Ryuki | `0005` | Boku, kimi; refined condescension. | Smug wealthy rival; let sincere respect emerge. | `50A9D8:4FE665` “Fight well enough that I won't be ashamed to call you my rival.” |
| Chiffon / attributed Betty requests | `0006` | Watashi/name self-reference; desu wa; -chan. | Sweet, privileged insistence; Betty's wishes are Chiffon's claims, not a separate verified voice. | `50A9D8:4FE689` “Don't be too mean to Ryuki-chan, please.” |
| Masky | `0007` | Atashi; rough imperatives; girlish taunts. | Tough boss with swagger and pride; later help stays in character. | `50A9D8:4FD913` “I haven't lost yet! I was just going easy on you!” |
| Pyorori | `0008` | Rough male colloquial speech; -ssu to anego. | Talkative tough-guy subordinate; deferential to Masky. | `50A9D8:50154A` “We're cheatin'? Don't be stupid.” |
| Boyoyo | `0009` | Ore; broken clauses, growls; echoes sentence tails. | Very brief, halting speech; repeat the previous speaker's tail, including after the scene seems over. | `50A9D8:508D2A` “To shine...” / “On screen...” |
| Manson | `000A` | Papa self-reference; warm explanatory authority. | Proud, affectionate dad who can also be a formidable rival. | `50A9D8:4FF9E5` “Y-your dad's so proud! You've grown into such a fine young man!” |
| Mamia | `000B` | Familiar parental requests; ne. | Gentle domestic guidance and practical errands. | `50A9D8:4FF45B` “Be nice to your friends at the park, now.” |
| Kamui | `000C` | Wan/wafu; barking only. | Preserve barking and the delayed kiss-recipient joke; not Salty. | `50A9D8:4FFC40` “Woof! Woof!” |
| Dr. Aki / Medabot professor | `000D` | Washi; ja/no; hoho. | Proud elder researcher; do not import retained-story family ties. | `50A9D8:500D81` “I am the great Medabot professor!” |
| Chief | `000E` | Elderly ja/no; food, drink and pottery requests. | Folksy elder with practical wants; keep the glossary's “Chief.” | `50A9D8:4FDBEE` “Just what this old fellow wanted with his drink!” |
| Chick seller / Chick Man | `0017` | Ore, bozu; clipped informal explanations. | Rough, helpful mentor; knowledgeable hints do not establish an unnamed identity. | `510124:50F1E4` “Kid, a Medabot is a robot friend with feelings and a will of its own.” |
| Leader Oro / Gang Boss | `0016` / `0015` | Watashi; pompous authority, sinister laughter. | Carry recognizable grandiosity between personas; preserve the conspiracy's reveal timing. | `50A9D8:5020DE` “Leader Oro of M-PK has arrived!” / “But before me, you are nothing more than a fool!” |
| Amarillo | `000F`, `0010`; unseen `0053` | Atachi; deshu; baby substitutions. | Maintain the shipped w/r baby diction even in calculating threats; it is a recognition clue. | `50A9D8:508D8C` “You can't go any fawther!” |
| Azul | `0011`, `0012` | Atashi; cho-, jan; stretched complaints. | Slangy, brazen and petulant; distinct from Rojo's aristocratic act. | `50A9D8:4FF0AC` “Tch. You've got pretty good instincts.” |
| Rojo | `0013`, `0014` | Watakushi; desu wa/koto; ohoho. | Haughty, flirtatious “big sister”; belittle Gamma as a child. | `50A9D8:503254` “I have no business with children, dear.” |
| M-PK agents | `0018`, `0019` | De arimasu; military politeness. | Crisp service and “sir” where natural; early agents need not sound conspiratorial. | `510124:50F3F1` “Defeat the Rubberobo Gang in a Robattle to obtain Rubberobo Medals, sir!” |
| Rubberobo grunts | `001A`, `001B`; hidden `0053` | Sentence-final robo; bluster and excuses. | Keep robo audible; do not apply it automatically to executives. | `50A9D8:4FFE5E` “Y-you'll pay for this, robo!” |
| Brilletz | `003F` | Mixed-kana foreign speech; polite boasts. | Confident European champion; mild odd phrasing, no invented accent. | `50A9D8:500128` “Me, I'm Brilletz. Europe's representative, yes!” |
| Terra | `0040` | Me; conspicuous foreign catchphrase delivery. | Exclamatory and theatrical; no ethnic phonetic spelling. | `50A9D8:4FE5F2` “Me? In shock!!” |
| Racione | `0041` | Boku; solemn katakana; mamieru. | Formal, declarative challenge; preserve the shipped emphatic delivery. | `50A9D8:4FE601` “MY NAME IS RACIONE. PERHAPS WE SHALL MEET AGAIN SOMEDAY...” |
| Viola | `0042` | Omae; mixed-kana, composed plain speech. | Self-possessed tournament competitor; avoid invented relationships. | `50A9D8:4FD14C` “You beat me. We'll meet again somewhere.” |
| Kotetsu | `0043` | Ja/no; familiar elder enthusiasm. | Eager old Robattler; direct and spirited. | `50A9D8:50170B` “Let's start a Robattle right away!” |
| Morea | `0044` | Atashi; no; hohoho. | Kindly elder teasing; preserve the joke that she does not Robattle. | `50A9D8:501804` “...Is what I'd like to say, but I don't Robattle, you see. Ho ho ho!” |
| Principal | `0045` | Washi; ja/no; reminiscing. | Genial school authority, personally fond of Robattles. | `50A9D8:4FD249` “I've loved Robattles since way back, you know.” |
| Health teacher / Nurse | `0046` | Sensei self-reference; ordinary caring speech. | Practical concern for children's safety. | `50A9D8:50610E` “Oh? You want to Robattle with your sensei?” |
| Library teacher / Librarian | `0047` | Watashi; reflective plain speech; yo. | Mild, thoughtful, averse to destruction. | `50A9D8:506E01` “But I don't much care for defeating or destroying things.” |
| Music teacher | `0048` | Familiar feminine yo; sharp accusation when provoked. | Ordinary teacherly complaint turning indignant. | `50A9D8:505E32` “This is a Medabot part!? You switched it, didn't you!!” |
| PE teacher | `0049` | Sensei self-reference; zo; excited exhortations. | Boisterous, proud and instructive; preserve excursion warnings. | `50A9D8:4FDB1D` “Oh, I forgot one warning!” |
| Science teacher | `004A` | Plain explanations; polite experiment offers. | Matter-of-fact experimenter; alarming smoke is the comic contrast. | `50A9D8:505EB8` “Would you like to change your Medal?” |
| Horiuchi | `0052` | Ore; grandiose self-promotion. | Loud cameo braggart; distinguish from Kawamuraa. | `50A9D8:50A5D1` “Hey, hold it! I'm the great Horiuchi!! I'm the world's greatest Medafighter!” |
| Grey / alien visitor | `0051`; silhouette `0064` | Fragmentary, solemn katakana speech. | Sparse, portentous statements; preserve pauses and alien mystery. | `50A9D8:4FED43` “EVEN NOW, YOU CANNOT BELIEVE...!?” |
| Duo Kaiser | `004C` | Watashi; repeated destruction declarations. | Cold, relentless purpose; repetition is intentional. | `50A9D8:5092C6` “I exist here solely to destroy. I will destroy everything before me!” |
| Ninja Village ninjas | `001C`, `001D`, `001F` | De gozaru; stylized martial speech. | Formal challenges and “indeed” where the shipped tic uses it. | `50A9D8:502DA9` “A dead end lies ahead. You must not enter, indeed.” |
| Kunoichi | `001E` | Courteous guest address; feminine wa/ne. | Playful but helpful; clear directions amid ninja theatrics. | `50A9D8:4FD079` “You have a Ninja Ticket, so you must be our guest.” |
| Wolf Man | `004B` | Hesitant challenge; howling. | Preserve the nervous stammer and animal interruption. | `50A9D8:50952E` “Hey, kid. L-let's Robattle...” |
| Kappa | `004D` | Sentence-final ke; shirikodama threat. | Keep abrupt “Keh!” and the creature-specific threat. | `50A9D8:5098F8` “I'll yank out your shirikodama! Keh!” |
| Snowman | `004E` | Quiet plain remarks about reading. | Mild, reflective seasonal joke; no invented monster snarl. | `50A9D8:507008` “Is it autumn reading season yet...?” |
| Komainu | `004F` | Barking. | Animal sounds only. | `50A9D8:50762D` “Arf! Arf!” |
| Octomed | `0050` | Sentence-final tako. | Persistent, pushy patter; retain “, tako.” | `50A9D8:5080A8` “Who the heck are you, tako? Keep your nose out of this, tako!” |
| Mermaid | `0061` | Firm refusal, then polite gratitude. | Clear agency and sincere thanks; not merely a rescue prop. | `50A9D8:508086` “No means no!” |
| Kintaro | `0060` | Oresama; yaya; emphatic challenges. | Booming folk-hero bravado and eager repetition. | `50A9D8:509A53` “Come on! Fight me! Fight me!” |
| Monkey / monkey guise | `0056`; Amarillo uses `000F` | Monkey cries; revealed impostor reverts to deshu. | Keep animal “Ook!” distinct from Amarillo's baby pronunciation. | `50A9D8:509964` “Nice hot water! Ook!” |
| Shop clerks | `0054`, `0055` (shared) | Irasshaimase; stretched greeting; everyday sales talk. | Friendly sales patter; preserve elongation where used, without inventing a universal tic. | `50A9D8:4FFD12` “Welcome! How about some very rare parts?” |
| Chiffon's household maid | `005D` | -sama; formal protective service. | Polite gatekeeping, suspicious of unsuitable visitors. | `50A9D8:50116A` “It would be dreadful if some unsavory boy latched on to Chiffon-sama.” |
| Link attendant | `005E` | Polite explanations; friendly yo. | Welcoming and precise; keep rules easy to understand. | `50D614:50D3F5` “Enjoy a casual Robattle with a friend! No parts are at stake!” |
| Referee / tournament announcer | `005F` | Formal public announcements; -kun/-san. | Excited sporting patter; preserve names, rounds and results. | `50A9D8:4FE0EE` “It's Terra, all the way from Africa!” |
| Medabot Weekly hosts | `0125`, `002E` | Stretched greeting; lively question-and-answer banter. | Bright broadcast delivery; distinguish host from impatient cohost. | `50E8F4:50E6E0` “Hellooo, everyone!!” / `50E8F4:50E723` “Hey, hey! What's this week's topic?” |
