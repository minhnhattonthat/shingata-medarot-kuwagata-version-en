"""Text sweep: show every dialogue string nobody reached yet in the game's own dialogue box, for textcover.py.

    python -X utf8 tools/debug/sweep.py [ROM] [--qa work/qa/sweep] [--seen work/qa/scenes_en11 ..] [--jobs 2]

Replays one short dialogue event over and over in a single boot (warp.lua EVENTS='5,5,5,..', A mashed; event 5
shows 5 lines and returns to the field) with tools/lua/sweep.lua: each dialogue start (0x08040F6C) shows the next
string of a list instead of the event's own line, so every `ff` string (dialogue, signs, NPC talk, battle messages,
info panes) goes through the real runner and box, ~95 frames each. Before each round the list is rebuilt from the
build's strings.tsv minus every string already read (TEXT lines in QA/run_*/log.txt and the --seen dirs) and split
between --jobs emulators (~560 MB each). Name-list strings (`fe`) are not swept: the runner would read past their
FE into the next entry. Runs go to QA/run_NNN; resumable; each run capped at 590 s. Stops when the list is empty or
two rounds in a row show nothing new.
(--loop-event 0 instead plays the story events in order, eventtour-style: far slower, stuck events end a run.)
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill import SKILL  # noqa: E402
import prove  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TEXT = re.compile(r"^TEXT ([0-9A-Fa-f]+)", re.M)
EVSTART = re.compile(r"^EVSTART ([0-9A-F]+)", re.M)
MASK = 0x1FFFFFF
LAST_EVENT = 687


def shown(dirs):
    out = set()
    for d in dirs:
        for f in Path(d).rglob("log.txt"):
            out.update(int(x, 16) & MASK for x in TEXT.findall(f.read_text(encoding="utf-8", errors="replace")))
    return out


def sweep_strings(strings_tsv):
    """CPU addresses of every `ff` string with a pointer (script/*.json except unused.json), in script order."""
    addr = {}
    for ln in Path(strings_tsv).read_text(encoding="utf-8").splitlines():
        if ln.strip():
            i, h = ln.split("\t")[:2]
            addr[i] = int(h, 16)
    out = []
    for f in sorted((ROOT / "script").glob("*.json")):
        if f.stem == "unused":
            continue
        for s in json.loads(f.read_text(encoding="utf-8"))["strings"]:
            if s.get("kind") == "ff" and s["id"] in addr:
                out.append(addr[s["id"]])
    return out


def next_event(qa):
    """The event after the last one started in the newest run (0 when none)."""
    runs = sorted(qa.glob("run_*/log.txt"))
    for log in reversed(runs):
        evs = EVSTART.findall(log.read_text(encoding="utf-8", errors="replace"))
        if evs:
            return (int(evs[-1], 16) + 1) % (LAST_EVENT + 1)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "medarot_kuwagata_en.gba"))
    ap.add_argument("--qa", type=Path, default=ROOT / "work" / "qa" / "sweep")
    ap.add_argument("--seen", nargs="*", default=[], help="more log dirs whose TEXT reads count as shown")
    ap.add_argument("--loop-event", type=lambda s: int(s, 0), default=5, help="event to replay; 0 = story order")
    ap.add_argument("--per-run", type=int, default=0, help="events per run (default 2000 looped, 80 story)")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--max-runs", type=int, default=200)
    a = ap.parse_args()
    a.qa.mkdir(parents=True, exist_ok=True)
    rom = Path(a.rom)
    ranges = prove.text_ranges(str(rom))
    every = sweep_strings(rom.with_suffix(".strings.tsv"))
    per_run = a.per_run or (2000 if a.loop_event else 80)
    idle = 0
    for _ in range(a.max_runs):
        seen = shown([a.qa, *a.seen])
        todo = [x for x in every if x & MASK not in seen]
        if not todo:
            break
        jobs = []
        for j in range(min(a.jobs, len(todo))):
            n = len(list(a.qa.glob("run_*")))
            out = a.qa / f"run_{n:03d}"
            out.mkdir(parents=True, exist_ok=True)
            lst = out / "list.txt"
            lst.write_text("".join(f"{x:X}\n" for x in todo[j::a.jobs]), encoding="utf-8")
            if a.loop_event:
                evs = [a.loop_event] * per_run
            else:
                ev0 = next_event(a.qa)
                evs = [(ev0 + i) % (LAST_EVENT + 1) for i in range(per_run)]
            cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
                   "--frames", "200000", "--timeout", "590", "--shot-every", "600",
                   "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
                   "--var", "EVENTS='" + ",".join(f"{e:X}" for e in evs) + "'", "--var", "STOP=1",
                   "--var", "HOLD=30", "--var", "NOENC=1",
                   "--script", str(ROOT / "tools" / "lua" / "sweep.lua"),
                   "--var", f"LIST='{lst.resolve().as_posix()}'",
                   "--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "textcover.lua"),
                   "--var", f"RANGES='{ranges}'"]
            jobs.append((out.name, subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
        for _, p in jobs:
            p.wait()
        now = shown([a.qa, *a.seen])
        new = len([x for x in todo if x & MASK in now])
        print(f"{', '.join(n for n, _ in jobs)}: {new} new strings shown, {len(todo) - new} left", flush=True)
        idle = idle + 1 if new == 0 else 0
        if idle >= 2:
            print("two rounds without progress: stopping")
            break
    seen = shown([a.qa, *a.seen])
    left = [x for x in every if x & MASK not in seen]
    print(f"{len(every) - len(left)}/{len(every)} ff strings shown, {len(left)} left")


if __name__ == "__main__":
    main()
