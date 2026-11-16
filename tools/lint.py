"""lint.py: width-gate lint of the English script against data/windows.json (pipeline.md §Width gate).

    python -X utf8 tools/lint.py [--all]     # exit 1 if any translated string is over its box budget

For every script entry with `en` text: the table's variant (windows.json "tables": table id, else "*ff"/"*fe")
gives the budget.
- FE names: text width (font advances) <= px, encoded bytes (without the FE) <= bytes.
- FF text: the engine's own word wrap is simulated (a word that would end past px goes to the next line; {n} breaks,
  {page} starts a page) and each page must fit in `lines`. {var:xx} counts as windows.json "vars"[xx] px.
  A page of 2+ lines must not end in a stub line under STUB_PX (pipeline.md §Checks).
- Every string a pointer reaches with Japanese text needs `en`, unless script/keep_jp.txt lists its id + reason.
Warnings (not failures): translated strings whose variant is still a guess, and strings with an unknown character.
--all also lints the marker text (tools/marker.py) instead of `en`, a self-test of the lint and the budgets.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import marker  # noqa: E402

WINDOWS = ROOT / "data" / "windows.json"
SCRIPT = ROOT / "script"
TOKEN = re.compile(r"(\{\w+(?::[0-9A-Fa-f]*)?\})")
STUB_PX = 24  # a wrapped page whose last line is narrower than this (~4-5 letters) reads as an orphan


def load_windows(path=WINDOWS):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def variant_for(win, table, kind):
    name = win["tables"].get(table) or win["tables"].get("*" + kind)
    return name, win["variants"].get(name)


def token_name(tok):
    return tok[1:-1].split(":")[0]


def name_px(text, w):
    """Width of a name entry (FE string) and the unknown characters in it."""
    plain = TOKEN.sub("", text)
    bad = sorted({c for c in plain if c not in w})
    return sum(w.get(c, 8) for c in plain), bad


def wrap_pages(text, budget, w, var_px):
    """Simulate the engine's word wrap: [[line px, ...] per page], unknown characters."""
    pages, lines, pen, bad = [], [], 0, set()

    def word_px(word):
        return sum(w.get(c, 8) for c in word)

    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("{"):
            name = token_name(part)
            if name == "n":
                lines.append(pen)
                pen = 0
            elif name in ("page", "end"):
                lines.append(pen)
                pages.append(lines)
                lines, pen = [], 0
            elif name == "var":
                arg = part[1:-1].split(":")[1]
                width = var_px.get(arg.upper(), var_px.get("default", 64))
                if pen and pen + width > budget:
                    lines.append(pen)
                    pen = 0
                pen += width
            continue
        for word in re.split(r"( )", part):
            if not word:
                continue
            bad.update(c for c in word if c not in w)
            wp = word_px(word)
            if word != " " and pen and pen + wp > budget:
                lines.append(pen)
                pen = 0
            pen += wp
    if pen or lines:
        lines.append(pen)
        pages.append(lines)
    return pages, sorted(bad)


def stub_page(text, budget, w, var_px):
    """1-based number of the first page the engine's wrap (no {n} of the author's) ends in a line under STUB_PX."""
    for i, page in enumerate(re.split(r"\{page\}", text)):
        if "{n}" in page:
            continue
        lines = wrap_pages(page, budget, w, var_px)[0]
        if lines and len(lines[0]) >= 2 and 0 < lines[0][-1] < STUB_PX:
            return i + 1
    return 0


def lint(entries, win, w, stubs=True):
    """(errors, warnings) for [(table, entry, text)]. stubs=False skips the stub-line rule (marker text)."""
    errors, warnings, guessed = [], [], {}
    var_px = win.get("vars", {})
    for table, e, text in entries:
        vname, v = variant_for(win, table, e["kind"])
        where = f"{e['id']} ({table}, {vname})"
        if v is None:
            errors.append(f"{where}: no window variant for this table")
            continue
        if v.get("status") != "measured":
            guessed[vname] = guessed.get(vname, 0) + 1
        if e["kind"] == "fe":
            width, bad = name_px(text, w)
            if width > v["px"]:
                errors.append(f"{where}: {width} px > {v['px']}: {text}")
            if "bytes" in v:
                n = len(TOKEN.sub("", text))
                if n > v["bytes"]:
                    errors.append(f"{where}: {n} bytes > {v['bytes']}: {text}")
        else:
            pages, bad = wrap_pages(text, v["px"], w, var_px)
            for i, page in enumerate(pages):
                if len(page) > v["lines"]:
                    errors.append(f"{where}: page {i + 1} wraps to {len(page)} lines > {v['lines']}: {text}")
                    break
                over = [p for p in page if p > v["px"]]
                if over:
                    errors.append(f"{where}: one word wider than {v['px']} px: {text}")
                    break
            if stubs and (n := stub_page(text, v["px"], w, var_px)):
                errors.append(f"{where}: page {n} wraps to a stub last line (rebalance with {{n}} or rephrase): {text}")
        if bad:
            warnings.append(f"{where}: characters not in the English font: {''.join(bad)}")
    for vname, n in sorted(guessed.items()):
        warnings.append(f"{n} translated strings in variant {vname!r}, whose budget is still a guess (measure it)")
    return errors, warnings


def untranslated(root=SCRIPT):
    """Ids a pointer reaches whose jp has text but en is empty, minus script/keep_jp.txt (id + reason per line)."""
    keep_file = Path(root) / "keep_jp.txt"
    keep = {ln.split()[0] for ln in keep_file.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")} if keep_file.exists() else set()
    out = []
    for path in sorted(Path(root).glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8"))["strings"]:
            if e["slots"] and not e.get("en") and TOKEN.sub("", e["jp"]).strip() and e["id"] not in keep:
                out.append(f"{e['id']} ({path.stem}): no English: {e['jp']}")
    return out


def script_entries(use_marker=False, root=SCRIPT):
    w = marker.widths()
    out = []
    for path in sorted(Path(root).glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        table = d.get("table")
        if not table:
            continue
        for e in d["strings"]:
            if not e["slots"]:
                continue
            text = marker.marker_text(e["id"], e["jp"], e["kind"], False, w) if use_marker else e.get("en", "")
            if text:
                out.append((table, e, text))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="lint the marker text instead of en (self-test)")
    ap.add_argument("-q", "--quiet", action="store_true", help="print only the summary and errors")
    a = ap.parse_args(argv)
    win = load_windows()
    entries = script_entries(a.all)
    errors, warnings = lint(entries, win, marker.widths(), stubs=not a.all)
    if not a.all:
        errors += untranslated()
    for line in errors:
        print("ERROR", line)
    if not a.quiet:
        for line in warnings:
            print("warn ", line)
    print(f"lint: {len(entries)} strings, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
