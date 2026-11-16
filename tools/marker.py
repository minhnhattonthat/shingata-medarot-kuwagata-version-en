"""marker.py: the marker build's text: every string replaced by `ID: The quick brown fox...`, control codes kept.

    python -X utf8 build.py --marker [--full]    # -> build/marker.gba (or marker_full.gba)

Each line (text between the string start, {n}, {page} and the end) keeps its control codes in place; its text runs
become filler as wide as the Japanese line was (8 px per kana), and the first run of the string starts with the
string id, so every box on screen names the string behind it. --full fills every line of an FF string to the
dialogue wrap limit (208 px) instead: the width test for dialogue boxes. FE strings (name lists) get the id and
filler only up to the Japanese width.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font as fontmod  # noqa: E402

PANGRAM = "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. "
WRAP = 208
LINE_BREAKS = {"n", "page"}
TOKEN = re.compile(r"(\{\w+(?::[0-9A-Fa-f]*)?\})")


def widths():
    """{char: advance} for the English font, from the glyph file (+ space)."""
    w = {ch: adv for ch, adv, _ in fontmod.load_glyphs().values()}
    w[" "] = 4
    return w


def px(text, w):
    return sum(w[c] for c in text)


def fill(start, budget, w, words=PANGRAM):
    """`start` + pangram text up to `budget` px (at least `start`)."""
    out = start
    for c in words * 4:
        if px(out + c, w) > budget:
            break
        out += c
    return out.rstrip(" ") if len(out) > len(start) else out


def marker_text(sid, jp, kind, full=False, w=None):
    """The marker for one string (jp: its decoded text with {controls})."""
    w = w or widths()
    parts = TOKEN.split(jp)
    # group text runs into lines
    lines, cur = [], []
    for p in parts:
        if not p:
            continue
        if p.startswith("{"):
            name = p[1:].split(":")[0].rstrip("}")
            if name in LINE_BREAKS or name == "end":
                lines.append(cur)
                cur = []
        else:
            cur.append(p)
    lines.append(cur)
    out, first = [], True
    line_runs = iter(lines)
    runs = next(line_runs)
    for p in parts:
        if not p:
            continue
        if p.startswith("{"):
            out.append(p)
            name = p[1:].split(":")[0].rstrip("}")
            if name in LINE_BREAKS or name == "end":
                runs = next(line_runs, [])
            continue
        total_jp = sum(len(r) for r in runs) or 1
        budget_line = WRAP if full and kind == "ff" else 8 * total_jp
        budget = max(1, budget_line * len(p) // total_jp)
        start = f"{sid}: " if first else ""
        text = fill(start, max(budget, px(start, w)), w)
        if kind == "fe":
            text = text.rstrip(": ") if first else text
        if p.startswith(" ") and not text.startswith(" "):
            text = " " + text
        out.append(text)
        first = False
    s = "".join(out)
    if first:  # no text at all (control codes only): leave it
        return jp
    return s


def marker_strings(table, full=False, script=None):
    """{string offset: encoded marker bytes} for every string with slots."""
    import json
    import rombuild
    w = widths()
    out = {}
    for path in sorted(Path(script or rombuild.SCRIPT).glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8"))["strings"]:
            if not e["slots"]:
                continue
            out[int(e["id"], 16)] = table.encode(marker_text(e["id"], e["jp"], e["kind"], full, w))
    return out


if __name__ == "__main__":
    w = widths()
    for sid, jp, kind in (("4FCE18", "{face:005500}ごめんなさい{n}まだ じゅんびちゅうなの{page}メダロットの{end:00}", "ff"),
                          ("465B8C", "クワガタ{item}", "fe")):
        print(marker_text(sid, jp, kind, False, w))
        print(marker_text(sid, jp, kind, True, w))
