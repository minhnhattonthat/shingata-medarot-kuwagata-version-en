"""Event tour: play every story event (A mashed) with the text-coverage probe, for textcover.py.

    python -X utf8 tools/debug/eventtour.py [ROM] [--from 0 --to 687] [--qa work/qa/events_en] [--per-run 80]

One cold boot plays many events in a row (warp.lua EVENTS=): each run starts at the first event not yet started,
so an event that leaves the field (robattle, cutscene, map change) ends that run (EVSTUCK) and the next run resumes
after it. Runs go to QA/run_NNN (log.txt with TEXT lines, shots every --shot-every frames). Resumable: re-running
skips events already started in an earlier run_* log. One job at a time (memory); each run is capped at 590 s.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill import SKILL  # noqa: E402
import prove  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EV_RE = re.compile(r"^EV(START|STUCK) ([0-9A-F]+)")


def started(qa):
    """Events already started (EVSTART) in earlier runs, and the ones that got stuck."""
    seen, stuck = set(), set()
    for log in qa.glob("run_*/log.txt"):
        for ln in log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = EV_RE.match(ln)
            if m:
                (seen if m.group(1) == "START" else stuck).add(int(m.group(2), 16))
    return seen, stuck


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "medarot_kuwagata_en.gba"))
    ap.add_argument("--from", dest="lo", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--to", dest="hi", type=lambda s: int(s, 0), default=687)
    ap.add_argument("--qa", type=Path, default=ROOT / "work" / "qa" / "events_en")
    ap.add_argument("--per-run", type=int, default=80)
    ap.add_argument("--shot-every", type=int, default=90)
    ap.add_argument("--max-runs", type=int, default=1000)
    a = ap.parse_args()
    a.qa.mkdir(parents=True, exist_ok=True)
    ranges = prove.text_ranges(a.rom)
    for _ in range(a.max_runs):
        seen, stuck = started(a.qa)
        todo = [e for e in range(a.lo, a.hi + 1) if e not in seen][:a.per_run]
        if not todo:
            break
        n = len(list(a.qa.glob("run_*")))
        out = a.qa / f"run_{n:03d}"
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), a.rom, "--out", str(out),
               "--frames", "200000", "--timeout", "590", "--shot-every", str(a.shot_every),
               "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
               "--var", "EVENTS='" + ",".join(f"{e:X}" for e in todo) + "'", "--var", "STOP=1",
               "--var", "HOLD=30", "--var", "NOENC=1",
               "--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "textcover.lua"),
               "--var", f"RANGES='{ranges}'"]
        subprocess.run(cmd, capture_output=True, text=True)
        now, now_stuck = started(a.qa)
        new = sorted(now - seen)
        print(f"run_{n:03d}: events {todo[0]:X}..: {len(new)} started, stuck {sorted(f'{e:X}' for e in now_stuck - stuck)}",
              flush=True)
        if not new:  # the boot itself failed: skip this event so the tour can't loop forever
            (out / "log.txt").open("a", encoding="utf-8").write(f"EVSTART {todo[0]:X} (skipped: no progress)\n")
    seen, stuck = started(a.qa)
    print(f"{len(seen)} events started, {len(stuck)} stuck: {' '.join(f'{e:X}' for e in sorted(stuck))}")


if __name__ == "__main__":
    main()
