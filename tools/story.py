"""Story pass (phase 9): chapter files in story order, and one read-only codex reviewer per chapter.

    python -X utf8 tools/story.py chapters            work/qa/story/chapters/<chapter>.txt (rewritten each run)
    python -X utf8 tools/story.py review [--jobs 3] [CHAPTER ..]   codex per chapter with no verdict yet

Then: qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt", and
qa_gate.py check work/qa/story/manifest.tsv work/qa/story/verdicts.

Chapters are whole story tables in ROM order (close to story order; docs/synopsis.md maps tables to acts), big tables
cut into parts of about 250 lines. Each line: ">> id | face | JP" then the English. review sends
docs/story-reviewer-brief.md + the chapter path to `codex exec -s read-only`; the report goes to
work/qa/story/reports/<chapter>.md and its "ASSESSMENT<TAB>ok|issue<TAB>note" line to verdicts/<chapter>.tsv.
A chapter whose verdict file exists is skipped (delete it, or write a newer "fixed" line, after a fix).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORY = ROOT / "work/qa/story"
PART = 250

# (chapter name, [tables]) in story order: docs/synopsis.md part B (Shingata), then part A (retained Ikki story)
CHAPTERS = [
    ("s1_shingata_story", ["50A9D8"]),
    ("s2_shingata_fields", ["4B50CC"]),
    ("s3_shingata_voices", ["46E60C", "46D598", "46E0F0"]),
    ("s4_tutorials", ["50EF18", "510124"]),
    ("s5_battle", ["46F0BC", "4702F0"]),
] + [(f"i{n:02d}_{t}", [t]) for n, t in enumerate(
    ["4F3C84", "4F429C", "4F4654", "4F4B14", "4F5024", "4F54A0", "4F5940", "4F5D50", "4F6170",
     "4F65D8", "4F69DC", "4F6E38", "4F710C", "4F74B4", "4F7950", "4F7E64", "4F86B8"], 1)]

FACE = re.compile(r"\{face:([0-9A-F]{4})")
PROMPT = (
    "You are a read-only story reviewer for an English fan translation of a GBA game. Read docs/story-reviewer-brief.md "
    "and follow it exactly; it names the other files to read (docs/synopsis.md, docs/style-reference.md, glossary.md, "
    "docs/decisions.md). The chapter file is {path} ({lines} lines). Read all of it before judging. Return the report "
    "as your final message, ending with the ASSESSMENT line."
)


def chapter_files():
    out = []
    for name, tables in CHAPTERS:
        rows = []
        for t in tables:
            for s in json.loads((ROOT / f"script/{t}.json").read_text(encoding="utf-8"))["strings"]:
                m = FACE.search(s["jp"])
                rows.append(f">> {s['id']} | {m.group(1) if m else '-'} | {s['jp']}\n{s['en']}\n")
        parts = max(1, round(len(rows) / PART))
        size = -(-len(rows) // parts)
        for k in range(parts):
            out.append((f"{name}_{k + 1}" if parts > 1 else name, rows[k * size:(k + 1) * size]))
    return out


def write_chapters():
    d = STORY / "chapters"
    d.mkdir(parents=True, exist_ok=True)
    names = set()
    for name, rows in chapter_files():
        names.add(name)
        path = d / f"{name}.txt"
        text = "".join(rows)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
        print(f"{name}: {len(rows)} lines")
    for stale in d.glob("*.txt"):
        if stale.stem not in names:
            stale.unlink()


def review_one(name):
    codex = shutil.which("codex")
    path = (STORY / "chapters" / f"{name}.txt").relative_to(ROOT).as_posix()
    lines = (ROOT / path).read_text(encoding="utf-8").count(">> ")
    report = STORY / "reports" / f"{name}.md"
    with open(STORY / "reports" / f"{name}.log", "w", encoding="utf-8") as log:
        subprocess.run([codex, "exec", "-s", "read-only", "-o", str(report), "-"], cwd=ROOT,
                       input=PROMPT.format(path=path, lines=lines), text=True, encoding="utf-8",
                       stdout=log, stderr=subprocess.STDOUT)
    text = report.read_text(encoding="utf-8") if report.exists() else ""
    m = re.search(r"^\s*ASSESSMENT\s*\t\s*(ok|issue)\s*\t(.*)$", text, re.M | re.I)
    if not m:
        return f"{name}: no ASSESSMENT line (see {report})"
    (STORY / "verdicts" / f"{name}.tsv").write_text(f"{name}\t{m.group(1).lower()}\t{m.group(2).strip()}\n",
                                                    encoding="utf-8")
    return f"{name}\t{m.group(1).lower()}\t{m.group(2).strip()}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["chapters", "review"])
    ap.add_argument("names", nargs="*")
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    if a.cmd == "chapters":
        write_chapters()
        return
    if not shutil.which("codex"):
        sys.exit("codex not on PATH")
    for sub in ("reports", "verdicts"):
        (STORY / sub).mkdir(parents=True, exist_ok=True)
    names = a.names or [p.stem for p in sorted((STORY / "chapters").glob("*.txt"))
                        if not (STORY / "verdicts" / f"{p.stem}.tsv").exists()]
    bad = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for line in ex.map(review_one, names):
            bad += "no ASSESSMENT" in line
            print(line, flush=True)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
