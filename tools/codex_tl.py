"""codex_tl.py: run translator (or reviewer) passes through `codex exec` (Orca workers can't nest agents).

    python -X utf8 tools/codex_tl.py tl b001 b002 b003        # one codex session, batches in order
    python -X utf8 tools/codex_tl.py prompt FILE.txt LOG       # any prompt file (reviews, fit passes)

Logs and the last message go to work/tl/logs/<first batch>.log / .last.txt. Exit code = codex's.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "work/tl/logs"


def run(prompt, name):
    LOGS.mkdir(parents=True, exist_ok=True)
    with open(LOGS / f"{name}.log", "w", encoding="utf-8") as log:
        p = subprocess.run(["codex", "exec", "--skip-git-repo-check", "-s", "workspace-write",
                            "-o", str(LOGS / f"{name}.last.txt"), "-"],
                           input=prompt, text=True, encoding="utf-8", stdout=log, stderr=subprocess.STDOUT,
                           cwd=ROOT, shell=sys.platform == "win32")
    print(f"{name}: codex exit {p.returncode}")
    return p.returncode


def main(argv):
    if len(argv) >= 2 and argv[0] == "tl":
        batches = argv[1:]
        prompt = (f"Read docs/translator-brief.md and follow it for batches {' '.join(batches)}. "
                  "Work in the repo root. Write each work/tl/<batch>.out.tsv with your file-editing tool and run "
                  "the check command until it prints OK for each batch.")
        return run(prompt, batches[0])
    if len(argv) == 3 and argv[0] == "prompt":
        return run(Path(argv[1]).read_text(encoding="utf-8"), argv[2])
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
