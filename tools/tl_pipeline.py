"""tl_pipeline.py: translate -> review -> fix for groups of batches, through codex exec (tools/codex_tl.py).

    python -X utf8 tools/tl_pipeline.py "b014 b015 b016" "b017 b018" ...    # groups run one after another

Per group: translate the batches that have no .out.tsv yet (one codex session), write the pairs file
(tools/pairs.py), run an independent reviewer session (docs/reviewer-brief.md) that writes
work/tl/review/<first>.review.md, then a fix session that applies its Critical/Important findings to the .out.tsv
files and re-checks, then tools/rereview.py until a reviewer approves the fixed lines. Merging into script/ is left to the controller (`tools/batches.py merge ... --overwrite`), so
parallel lanes never write script/ at the same time. Status per group: work/tl/review/<first>.status.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
REVIEW = TL / "review"
PY = [sys.executable, "-X", "utf8"]


def codex(prompt, name, read_only=False):
    sys.path.insert(0, str(ROOT / "tools"))
    import codex_tl
    return codex_tl.run(prompt, name, read_only)


def check(batches):
    return subprocess.run(PY + ["tools/batches.py", "check", *batches], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8").returncode


def group(batches):
    first = batches[0]
    REVIEW.mkdir(parents=True, exist_ok=True)
    status = REVIEW / f"{first}.status"
    todo = [b for b in batches if not (TL / f"{b}.out.tsv").exists()]
    if todo:
        codex(f"Read docs/translator-brief.md and follow it for batches {' '.join(todo)}. Work in the repo root. "
              "Write each work/tl/<batch>.out.tsv with your file-editing tool and run the check command until it "
              "prints OK for each batch.", f"{todo[0]}")
    if check(batches):
        codex(f"Read docs/translator-brief.md. Batches {' '.join(batches)} were translated but "
              f"`python -X utf8 tools/batches.py check {' '.join(batches)}` still fails (or an .out.tsv is missing). "
              "Finish or fix them per the brief until the check prints OK for every batch.", f"{first}.retry")
    if check(batches):
        status.write_text("FAILED check after translation\n", encoding="utf-8")
        return 1
    subprocess.run(PY + ["tools/pairs.py", *batches], cwd=ROOT, capture_output=True)
    report = REVIEW / f"{first}.review.md"
    if not report.exists():
        codex(f"Read docs/reviewer-brief.md and follow it. Pairs file: work/tl/review/{first}.pairs.txt (batches "
              f"{' '.join(batches)}). You are read-only: return the whole report (the brief's Markdown format) as "
              "your final message instead of writing a file.", f"{first}.review", read_only=True)
        last = ROOT / f"work/tl/logs/{first}.review.last.txt"
        if last.exists():
            report.write_text(last.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    if not report.exists():
        status.write_text("FAILED no review report\n", encoding="utf-8")
        return 1
    codex(f"Read docs/translator-brief.md (you are the translator) and the review work/tl/review/{first}.review.md "
          f"of batches {' '.join(batches)}. Apply every Critical and Important finding to the matching line of "
          "work/tl/<batch>.out.tsv with your file-editing tool (judge each suggestion against the Japanese in "
          "work/tl/<batch>.tsv; reject a wrong one and say why). Leave Minor findings alone. Then run "
          f"`python -X utf8 tools/batches.py check {' '.join(batches)}` until it prints OK for every batch. Reply "
          "with: FIXED: id ... / REJECTED: id - reason.", f"{first}.fix")
    ok = check(batches) == 0
    # READY only comes from tools/rereview.py, after a reviewer approves the fixed lines (phase 6 review item 1)
    status.write_text("FIXED: re-review with tools/rereview.py\n" if ok else "FAILED check after fixes\n",
                      encoding="utf-8")
    if ok:
        ok = subprocess.run(PY + ["tools/rereview.py", "--jobs", "1", "--only", first], cwd=ROOT).returncode == 0
    return 0 if ok else 1


def main(groups):
    rc = 0
    for g in groups:
        rc |= group(g.split())
        print(f"{g}: {(REVIEW / (g.split()[0] + '.status')).read_text(encoding='utf-8').strip()}", flush=True)
    return rc


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):  # "--help" once started a pipeline for group "--help"
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
