"""Read-only visual-QA verdicts with codex, one `codex exec -s read-only` per chunk of `qa_gate.py todo --out-dir`.

    python -X utf8 tools/qa_verdicts.py work/qa/manifest.tsv work/qa/chunks12 work/qa/verdicts12

Each chunk_NNN.txt (sheet paths) gets the brief docs/visual-qa-brief.md + docs/decisions.md and the sheets as
images; the answer's last "id<TAB>ok|issue<TAB>note" lines become verdicts/chunk_NNN.tsv (+ .answer.txt, .log).
Chunks that already have a .tsv are skipped. Ids come from the manifest (path -> id).
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROMPT = (
    "You are a read-only visual-QA reviewer for an English fan translation of a GBA game. Read "
    "docs/visual-qa-brief.md and docs/decisions.md first and follow the brief. Each attached image is a pair "
    "sheet: left = English build, right = Japanese original, one pair per scene. The sheet ids and paths are:\n"
    "{table}\n"
    "Judge every sheet. End your answer with exactly one line per sheet: id<TAB>ok|issue<TAB>short note "
    "(use a real tab character)."
)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("chunks")
    ap.add_argument("verdicts")
    a = ap.parse_args()
    codex = shutil.which("codex")
    if not codex:
        sys.exit("codex not on PATH")
    ids = {}
    for line in Path(a.manifest).read_text(encoding="utf-8").splitlines():
        f = line.split("\t")
        if len(f) >= 2:
            ids[Path(f[1]).as_posix()] = f[0]
    out = Path(a.verdicts)
    out.mkdir(parents=True, exist_ok=True)
    bad = 0
    for chunk in sorted(Path(a.chunks).glob("chunk_*.txt")):
        tsv = out / (chunk.stem + ".tsv")
        if tsv.exists():
            continue
        # chunk lines: "path" or qa_gate todo's "id<TAB>path"
        paths = [Path(p.strip().split("\t")[-1]).as_posix() for p in chunk.read_text(encoding="utf-8").splitlines()
                 if p.strip()]
        want = {ids.get(p, Path(p).stem): p for p in paths}
        table = "\n".join(f"{i}\t{p}" for i, p in want.items())
        answer = out / (chunk.stem + ".answer.txt")
        cmd = [codex, "exec", "-s", "read-only", "-o", str(answer)]
        for p in paths:
            cmd += ["-i", p]
        cmd.append("-")  # prompt on stdin: -i takes several values and would swallow a positional prompt
        with open(out / (chunk.stem + ".log"), "w", encoding="utf-8") as log:
            subprocess.run(cmd, input=PROMPT.format(table=table), text=True, encoding="utf-8",
                           stdout=log, stderr=subprocess.STDOUT)
        text = answer.read_text(encoding="utf-8") if answer.exists() else ""
        rows = {}
        for line in text.splitlines():
            m = re.match(r"^\s*(\S+)\t(ok|issue)\t(.*)$", line)
            if m and m.group(1) in want:
                rows[m.group(1)] = f"{m.group(1)}\t{m.group(2)}\t{m.group(3).strip()}"
        missing = [i for i in want if i not in rows]
        if missing:
            bad += 1
            print(f"{chunk.name}: no verdict for {', '.join(missing)} (see {answer})")
            continue
        tsv.write_text("\n".join(rows[i] for i in want) + "\n", encoding="utf-8")
        for r in rows.values():
            print(r)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
