# Visual-QA reviewer brief - Shingata Medarot: Kuwagata Version (GBA)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- `glossary.md` for names.

## How the sheets are laid out
- `work/qa/tour/sheet*.png`: scene sheets. Each tile is a **pair**: left = the English build, right = the original
  Japanese ROM at the same scene (warped there by the debug tool), labelled with the scene name. The single
  shots are `work/qa/scenes_en/shots/<scene>.png` (English) and `work/qa/scenes/shots/<scene>.png` (original).
- `work/qa/events_en/...` sheets: story events played back to back with A mashed (English only).

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHOT.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, compare with the right-hand (original) tile. If the original shows the same thing,
  it is the game's own behaviour: `ok`, with a note.
- Zoom into every Yes/No prompt, selection box, menu row and speech bubble: a few pixels of misalignment don't show
  at sheet scale. To measure one: `python -X utf8 $SKILL/scripts/inkbox.py SHOT.png x,y,w,h`.

## Judge
An `issue` is any of:
- Japanese still visible (in the English tile);
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its selection box or cursor brackets, a label, a bubble;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp; the two tiles of a pair caught at different animation frames or
  different lines of the same dialogue (emulator timing differs run to run);
- anything identical in the original tile;
- the player is named "Ikki" in English (the debug tool pokes it); the original tile shows the name the boot
  left (ガンマアアア...);
- the robattle_intro info-box squiggle (the name sliding in; the original does it too);
- events played on the start map: actors missing, odd positions, black screens between events.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
