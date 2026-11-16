"""rereview.py: send each review group's fixed lines back to an independent reviewer until it says "Approved".

    python -X utf8 tools/rereview.py [--jobs 3] [--rounds 3] [--only b001,b014] [--extra ID ...]

A group is the batches of one work/tl/review/<first>.pairs.txt. Its re-review set = every id named in the group's
review (Critical/Important lines) or fix log (FIXED/REJECTED), plus --extra ids that fall in the group (lines changed
outside the pipeline). Per round: write work/tl/review/<first>.rereview<N>.pairs.txt (the ids with 2 neighbours each
side, the earlier finding and the fix-log verdict), run a read-only codex reviewer (docs/reviewer-brief.md), save its
report as <first>.rereview<N>.md; "Approved" ends the group, else a translator session applies its Critical/Important
findings to the .out.tsv files (`batches.py check` must pass) and the next round re-reviews them.
<first>.status becomes "READY: re-review approved (round N)" only on an Approved verdict. Merging into script/ is left
to the controller (`batches.py merge ... --overwrite`).
"""
import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import codex_tl  # noqa: E402

TL = ROOT / "work/tl"
REVIEW = TL / "review"
LOGS = TL / "logs"
PY = [sys.executable, "-X", "utf8"]
ID = re.compile(r"\b[0-9A-F]{6}\b")


def rows(path):
    return [ln.split("\t") for ln in path.read_text(encoding="utf-8").splitlines() if "\t" in ln]


def groups():
    """{first: [batches]} from the pairs files' '## batch bNNN' headers."""
    out = {}
    for p in sorted(REVIEW.glob("b???.pairs.txt")):
        out[p.name[:4]] = re.findall(r"^## batch (b\d{3})", p.read_text(encoding="utf-8"), re.M)
    return out


def findings(report):
    """{id: line} for the Critical and Important sections of a report."""
    text = report.read_text(encoding="utf-8") if report.exists() else ""
    m = re.search(r"^#+ *Critical.*?(?=^#+ *Minor|^#+ *Assessment|\Z)", text, re.M | re.S)
    out = {}
    for line in (m.group(0) if m else "").splitlines():
        if line.startswith("- "):
            for i in ID.findall(line.split(" - ")[0]):
                out.setdefault(i, line[2:].strip())
    return out


def fixlog(first):
    p = LOGS / f"{first}.fix.last.txt"
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    out = {}
    for kind in ("FIXED", "REJECTED"):
        for m in re.finditer(kind + r":(.*?)(?=FIXED:|REJECTED:|\n\n|\Z)", text, re.S):
            for i in ID.findall(m.group(1)):
                out[i] = kind + (": " + m.group(1).split(" - ", 1)[1].strip()[:300] if " - " in m.group(1) else "")
    return out


def pairs_file(first, batches, ids, notes, n):
    en = {}
    for p in (ROOT / "script").glob("*.json"):
        for e in json.loads(p.read_text(encoding="utf-8"))["strings"]:
            en[e["id"]] = e.get("en") or ""
    lines = [f"# Re-review round {n} of group {first} ({' '.join(batches)}): {len(ids)} lines marked >>.",
             "# '   (ctx)' lines are neighbours for context only; judge only the >> lines.", ""]
    for b in batches:
        jp = rows(TL / f"{b}.tsv")
        out = dict((r[0], r[1]) for r in rows(TL / f"{b}.out.tsv"))
        order = [r[0] for r in jp]
        jpd = {r[0]: r[4] for r in jp}
        for k, i in enumerate(order):
            if i not in ids:
                continue
            lines.append(f"## {i} (batch {b})  earlier: {notes.get(i, 'changed outside the pipeline')}")
            for j in order[max(0, k - 2):k + 3]:
                mark = ">>" if j == i else "  (ctx)"
                lines.append(f"{mark} {j} | {jpd[j]}")
                lines.append(f"   {out.get(j, en.get(j, ''))}")
            lines.append("")
    path = REVIEW / f"{first}.rereview{n}.pairs.txt"
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def verdict(report):
    m = re.search(r"#+ *Assessment\s*\n+\s*(\S.*)", report.read_text(encoding="utf-8")) if report.exists() else None
    return m.group(1).strip() if m else ""


def check(batches):
    return subprocess.run(PY + ["tools/batches.py", "check", *batches], cwd=ROOT, capture_output=True).returncode


def run_group(first, batches, extra, rounds):
    status = REVIEW / f"{first}.status"
    notes = {i: "reviewer finding: " + f for i, f in findings(REVIEW / f"{first}.review.md").items()}
    for i, v in fixlog(first).items():
        notes[i] = (notes.get(i, "") + " | fix log: " + v).strip(" |")
    in_group = {r[0] for b in batches for r in rows(TL / f"{b}.tsv")}
    for i in extra & in_group:
        notes.setdefault(i, "changed by the controller after the phase 6 review (docs/decisions.md D11-D12)")
    ids = set(notes) & in_group
    if not ids:
        status.write_text("READY: no Critical/Important findings to re-review\n", encoding="utf-8")
        return first, "nothing to re-review"
    for n in range(1, rounds + 1):
        pairs = pairs_file(first, batches, ids, notes, n)
        report = REVIEW / f"{first}.rereview{n}.md"
        prompt = (f"Read docs/reviewer-brief.md and follow it, with these changes. This is a RE-REVIEW: the pairs "
                  f"file {pairs.relative_to(ROOT).as_posix()} holds only lines that an earlier review flagged (its "
                  "finding and the fix-log verdict are in each '## id' header) or that were changed afterwards. Judge "
                  "each >> line fresh against its JP, and say whether the earlier finding is resolved or the "
                  "rejection is sound. Also read docs/decisions.md D4 and D10-D12 and glossary.md sections 'Capped "
                  "part names' and 'Name-box labels': a name box holds at most 10 bytes (measured, widening ruled "
                  "out), so a shortened name listed there is correct unless you give a closer form of at most 10 "
                  "characters. You are read-only: edit no file. Return the whole report (the brief's Markdown "
                  "format, ending with the ### Assessment line 'Approved' or 'Needs fixes') as your final message.")
        codex_tl.run(prompt, f"{first}.rereview{n}", read_only=True)
        last = LOGS / f"{first}.rereview{n}.last.txt"
        if last.exists():
            report.write_text(last.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        v = verdict(report)
        if v.lower().startswith("approved"):
            status.write_text(f"READY: re-review approved (round {n})\n", encoding="utf-8")
            return first, f"approved in round {n}"
        if not report.exists() or not v:
            status.write_text(f"FAILED: no re-review verdict (round {n})\n", encoding="utf-8")
            return first, "no verdict"
        codex_tl.run(f"Read docs/translator-brief.md (you are the translator) and the re-review "
                     f"{report.relative_to(ROOT).as_posix()} of batches {' '.join(batches)}. Apply every Critical and "
                     "Important finding to the matching line of work/tl/<batch>.out.tsv with your file-editing tool, "
                     "one line at a time (judge each against the Japanese in work/tl/<batch>.tsv; reject a wrong one "
                     "and say why; names in glossary.md's capped tables need the controller, so reject those). Leave "
                     f"Minor findings alone. Run `python -X utf8 tools/batches.py check {' '.join(batches)}` until it "
                     "prints OK for every batch. Reply with: FIXED: id ... / REJECTED: id - reason.",
                     f"{first}.fix{n + 1}")
        if check(batches):
            status.write_text(f"FAILED: check after re-review fixes (round {n})\n", encoding="utf-8")
            return first, "check failed"
        new = findings(report)
        fixed = (LOGS / f"{first}.fix{n + 1}.last.txt")
        log = fixed.read_text(encoding="utf-8") if fixed.exists() else ""
        notes = {i: f"re-review {n} finding: {f} | fix log: {log[:300]}" for i, f in new.items() if i in in_group}
        ids = set(notes) or ids
    status.write_text(f"FAILED: not approved after {rounds} rounds\n", encoding="utf-8")
    return first, f"not approved after {rounds} rounds"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--only", default="")
    ap.add_argument("--extra", nargs="*", default=[])
    a = ap.parse_args(argv)
    gs = groups()
    if a.only:
        gs = {k: v for k, v in gs.items() if k in a.only.split(",")}
    with ThreadPoolExecutor(a.jobs) as ex:
        for first, result in ex.map(lambda kv: run_group(kv[0], kv[1], set(a.extra), a.rounds), gs.items()):
            print(f"{first}: {result}", flush=True)
    bad = [p.name for p in REVIEW.glob("*.status") if not p.read_text(encoding="utf-8").startswith("READY:")]
    print("all groups approved" if not bad else f"not approved: {' '.join(sorted(bad))}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
