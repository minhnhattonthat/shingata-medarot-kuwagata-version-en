"""build.py: build the patched ROM from rom/ + the repo's sources.

    python -X utf8 build.py                  # -> build/medarot_kuwagata_en.gba (+ .writes.txt for romdiff --writes)
    python -X utf8 build.py --relocate-all   # -> build/relocate_all.gba: every script string moved past 8 MiB and
                                             #    repointed, the pointer-writer stress build (docs/status.md)
    python -X utf8 build.py --relocate-all --poison   # -> build/relocate_poison.gba: same, old copies overwritten
                                             #    with ア: any ア run in a scene is a reference the tables miss

Checks the dump against rom.sha1 first. Until text is inserted (phase 7) the default build is byte-identical to the
original ROM (tests/test_identity.py).
"""
import argparse
import hashlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import rombuild  # noqa: E402

ROM = ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba"
OUT = ROOT / "build" / "medarot_kuwagata_en.gba"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--relocate-all", action="store_true", help="move every script string (pointer-writer test)")
    ap.add_argument("--poison", action="store_true",
                    help="with --relocate-all: overwrite the old copies with ア, so a reference the tables miss shows")
    ap.add_argument("--marker", action="store_true",
                    help="marker build: every string -> `ID: The quick brown fox...` (tools/marker.py)")
    ap.add_argument("--full", action="store_true", help="with --marker: fill every dialogue line to 208 px")
    ap.add_argument("--set", action="append", default=[], metavar="ID=TEXT",
                    help="override one string (hex id = its offset; TEXT in en.tbl form with {controls}); repeatable."
                         " Width-gate stress lines: needs --out or --marker")
    ap.add_argument("--out", type=Path, help="output path")
    a = ap.parse_args()
    if a.poison and not a.relocate_all:
        ap.error("--poison needs --relocate-all")
    if a.full and not a.marker:
        ap.error("--full needs --marker")

    check_rom.check()
    t0 = time.time()
    orig = ROM.read_bytes()
    strings = None
    if a.marker:
        import marker
        strings = marker.marker_strings(rombuild.en_table(), a.full)
    if a.set:
        if not (a.out or a.marker):
            ap.error("--set needs --out or --marker (keep build/medarot_kuwagata_en.gba the real build)")
        strings = strings or {}
        for item in a.set:
            sid, _, text = item.partition("=")
            strings[int(sid, 16)] = rombuild.en_table().encode(text)
    data, report = rombuild.build(orig, strings=strings, relocate_all=a.relocate_all, poison=a.poison)
    name = "relocate_poison.gba" if a.poison else "relocate_all.gba"
    if a.marker:
        name = "marker_full.gba" if a.full else "marker.gba"
    out = (a.out.resolve() if a.out else None) or (ROOT / "build" / name if a.relocate_all or a.marker else OUT)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    rombuild.write_log(report, out.with_suffix(".writes.txt"))
    sha = hashlib.sha1(data).hexdigest()
    same = "identical to the original" if data == orig else f"{len(report.writes)} writes"
    print(f"{out.relative_to(ROOT)}: {len(data):#x} bytes, sha1 {sha}, {same}")
    print(f"text: {report.strings} strings, {report.in_place} in place, {report.moved} moved, "
          f"{report.slots_repointed} slots repointed ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
