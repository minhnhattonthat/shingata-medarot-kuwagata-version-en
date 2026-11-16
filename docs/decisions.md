# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

All of D1-D7 came with the dispatch brief from the owner's Orca coordinator (pre-approved one-shot run).

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-17 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western name order (given name first). Owner's standing answer. |
| D2 | 2026-11-17 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist (Medabots anime/GBA localisations), else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-17 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-17 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms, engine work before abbreviating. |
| D5 | 2026-11-17 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); leave the original Japanese logo only if it has no official English version. |
| D6 | 2026-11-17 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints without asking. |
| D7 | 2026-11-17 | Existing saves / savestates | user supplies, none | None provided; build the debug tool as usual. Git identity already set; do not change it. |
| D8 | 2026-11-17 | Font code layout (agent's call under D6, pre-approved) | lowercase/punctuation at free codes D0-F6; at hiragana codes 52-78 | Hiragana codes 52-78. The menu-name sprite charset (Le 0x5518A0) holds only codes 01-CF and has no VRAM room to grow, so English glyphs must sit below D0 for names to render. Cost: an untranslated hiragana string shows as English letters, so leftover-Japanese checks go by script status (and katakana) rather than by decoding hiragana. |
