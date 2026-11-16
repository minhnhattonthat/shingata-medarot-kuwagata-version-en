"""collect_reviews.py: keep the translation review evidence in git and gather Minors into docs/polish.md.

    python -X utf8 tools/collect_reviews.py

Copies work/tl/review/*.review.md, *.rereview*.md and work/tl/logs/*.fix*.last.txt into docs/reviews/ (work/ is
gitignored), and appends every Minor finding (the "#### Minor" bullets of each report) that docs/polish.md doesn't hold
yet as `- [ ] id - note (source)`. Existing lines, ticked or not, are never touched, so a rerun only adds.
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "work/tl/review"
LOGS = ROOT / "work/tl/logs"
OUT = ROOT / "docs/reviews"
POLISH = ROOT / "docs/polish.md"
HEAD = """# Polish pass

Every Minor finding, one line each. The polish pass ticks each line `[x]`, fixed or `waived: reason`; the release
script refuses to run while any line is unticked (references/translation.md §Review). Sources: docs/reviews/.

"""


def minors(text):
    m = re.search(r"^#+ *Minor.*?$(.*?)(?=^#+ |\Z)", text, re.M | re.S)
    if not m:
        return []
    return [re.sub(r"\s+", " ", b).strip() for b in re.findall(r"^- (.+?)(?=^- |\Z)", m.group(1), re.M | re.S)
            if not b.strip().lower().startswith("none")]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reports = sorted(REVIEW.glob("*.review.md")) + sorted(REVIEW.glob("*.rereview*.md"))
    for p in reports + sorted(LOGS.glob("*.fix*.last.txt")):
        shutil.copyfile(p, OUT / p.name)
    text = POLISH.read_text(encoding="utf-8") if POLISH.exists() else HEAD
    added = 0
    for p in reports:
        for note in minors(p.read_text(encoding="utf-8")):
            line = f"- [ ] {note} ({p.name})"
            if note not in text:
                text += line + "\n"
                added += 1
    POLISH.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(reports)} reports copied to {OUT.relative_to(ROOT)}; {added} Minors added to docs/polish.md")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
