# Story reviewer brief - Shingata Medarot: Kuwagata Version

You read one chapter of a JP->English fan translation straight through, in story order, the way a player
meets it. Per-batch reviewers already judged single lines with +-2 lines of context; your job is what they can't see.
Read-only: no edits, no git, no subagents. Return the report as your final message; the controller saves it.

## Inputs (paths in your dispatch)
- Chapter file: every line of the chapter in ROM order (which is close to story order; optional scenes and alternative
  routes are interleaved), `>> id | face | JP` / `EN`. `face` is the speaking portrait's id (XXXX of `{face:XXXXYY}`;
  `0100` is the player, `{var:00}` is the player's name). Read ALL of it, in passes if large, before judging.
- `docs/synopsis.md` (plot, who is who, late reveals; two casts share face ids), `docs/style-reference.md` (voice per
  character, face ids), `glossary.md` (rulings at the top), `docs/decisions.md`.
- Control codes: `{n}` line break, `{page}` new box, `{end:..}` end, `{fa:..}` timing; ignore them except where a
  page break splits a joke or a reveal.

## Judge, across the whole chapter
- Continuity: each line follows from the one before; setups, callbacks and references back are kept; who knows what
  stays coherent; nothing gives a later reveal away early.
- Voice: each character sounds like the same person all chapter and matches their style-reference row: speech quirks
  (robo, ari, de arimasu officers, drawn-out vowels), register, how they address others. Name the line where a voice
  drifts or goes neutral.
- Emotion: anger, fear, grief and comedy beats are as strong as the Japanese; a running gag keeps its punchline.
- Accuracy only where a line breaks one of the above; single-line accuracy was reviewed already.
- Checklist from earlier projects: a joke losing half its gag; "1st" shown as "1th"; a name off by one letter;
  awkward stock phrases ("TIPS ... GET!").

## Report
### Issues
#### Critical (continuity break, reveal given away, wrong speaker)
#### Important (voice drift or flattened, emotional beat lost, setup or callback dropped, joke dead)
#### Minor (deferred to the polish pass)
Each: `id - JP gist - problem - suggested EN` (the full suggested English string with its control codes).
### Assessment
`ok` (no Critical/Important) | `issue` - one sentence why. End the report with exactly one line
`ASSESSMENT<TAB>ok|issue<TAB>one-sentence note` (a real tab character).
