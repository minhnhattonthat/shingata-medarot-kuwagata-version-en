# Translator brief - Shingata Medarot: Kuwagata Version (GBA, 2003)

You translate part of the Japanese script of Shingata Medarot (Kuwagata Version) into English for a fan patch. It is a
kids' RPG: a schoolboy (the player, {var:00}) builds Medabots from parts and medals, fights "Robattles" and runs into
the comic villains of the Rubberobo Gang. Tone: light, funny, warm; the jokes and character quirks matter.
The ROM holds two casts (docs/synopsis.md): Shingata's own story (hero Gamma, Iris, Ryuki, La Mascara, M-PK, Oro;
tables 50A9D8 4B50CC 46D598 46E0F0 510124) and retained Medarot 2 Core story text (Ikki, Erika, Koji, Karin, Dr.
Meta-Evil; tables 4F3C84-4F7E64). {var:00} is the player's name in both; never replace it with a fixed name.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before the
next. Do all translation yourself; do not dispatch subagents. Do not edit any file except your own `.out.tsv` files.

## Read first
1. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table in `glossary.md`; read its Rulings and
   Style rules sections once).
2. `docs/synopsis.md` - plot, who is who, voices and the late reveals. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. form is `dlg` (a text box, FF string) or `name` (a short label,
FE string). Lines are in ROM order, which is mostly story order: use neighbours for context.

Control codes are in braces and must be copied exactly, same order:
- `{face:XXYYZZ}` picks the speaker portrait (the speaker changes when it changes). Keep each one at the same place
  relative to the text it introduces.
- `{end:XX}` ends the string: it must stay last. `{item}` ends a name: it stays last.
- `{var:00}` = the player's name; `{var:01}`-`{var:04}` = an item, part, attack or number the game fills in.
- `{fa:FF}`, `{f7}` and any other code: copy as is, same position.
- `{n}` (line break) and `{page}` (new box, waits for a button) are free: the engine word-wraps by itself, so drop
  every JP `{n}` you don't need and let lines wrap; add `{page}` wherever a box would overflow. Keep a `{page}` where
  the JP has one between two speakers/faces or before a dramatic beat.

## Limits (hard, checked)
- `dlg`: each box is 2 lines of 208 px. Most letters are 6 px, i/l/./,/!/' are 2-4 px, M/W are 8 px: about 40-45
  characters a line, ~85 a box. A longer utterance simply gets more `{page}`s - don't cut meaning to save a box.
- `name`: px and byte (character) caps are given in the limit column (often 10 characters!). Names in the glossary
  already fit. For other names, choose the clearest English that fits; if you have to compress, report `CUT:`.
- Dry-run any line: `python -X utf8 tools/batches.py fit <id> "<English>"` prints the wrap and every problem.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Only characters the font has: A-Z a-z 0-9 space and
`! " % & ' ( ) + , - . / : ; ?` - no `* ~ < > [ ] _ = # $ @`, no Japanese, no fullwidth, no curly quotes, no tabs or
newlines inside the English (line breaks are `{n}`).

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Keep the speaker audible. JP register markers carry voice and must turn into English devices, not vanish:
  old men's じゃ/のう/わし ("eh?", "my boy", "back in my day"), rough boys' ぜ/ねぇ/オレ ("ain't", "ya", clipped
  grammar), feminine かしら/わよ/のね ("I wonder...", "you know", "dear"), polite です/ます adults vs. casual kids,
  whines and drawls (〜ぅ/なぁ: "but Mooom", stretched words). Rubberobo grunts end lines with ロボ: keep "robo!".
  A line any speaker could have said is a mistake.
- Use names and terms exactly as in the glossary (Medabot, Robattle, Medawatch, Medafighter, Tinpet, Medaforce,
  Rubberobo Gang...). Full names and terms; never abbreviate to fit a dialogue box (add a {page} instead).
- Honorifics kept, hyphenated: カリンちゃん -> Karin-chan, {var:00}くん -> {var:00}-kun, せんせい as a title ->
  -sensei / "Sensei". Western name order. Punctuation: 「」 -> "...", 『』 -> '...', ・・・ -> `...`, ！？ -> `!?`.
- Sound effects as plain words: ドンッ！ -> `BAM!`, ワンッ！ -> `Woof!`.
- No suffix glued onto a variable (write "No. {var:02}" not "{var:02}th"); no a/an right before {var:..}; a number
  variable takes neutral wording ("x{var:02}", "{var:02} of them").
- Menu labels and yes/no options: short, title case where the Japanese is a label.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `CUT: id - what was
dropped`.
