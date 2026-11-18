"""Release: every gate, then the patch, re-applied to a clean original and compared, then the zip.

    python -X utf8 tools/release.py [--version 1.0] [--force]
    python -X utf8 tools/release.py --game kabuto [--version 1.0]   # the Kabuto Version patch (docs/re/kabuto.md)

Stops at the first failure. Steps: rom check -> build -> tools/check.py (tests + lint) -> smoke boot -> jp_left
(build/ text the game still points at, codes 52-78/A2-CF dropped from jp.tbl since English reuses them; known runs
in docs/jp_left_known.txt) -> qa_gate.py check on every work/qa/**/manifest.tsv (visual tour + story pass) ->
textcover (work/qa/sweep logs carried to this build by tools/coverremap.py) -> no unticked line in docs/polish.md ->
no template placeholder in README.md -> debug tool off (this build = a plain build.py run: the debug tool is Lua
outside the ROM) -> BPS patch -> re-apply to the original and compare sha1 -> release/<name>_v<ver>.zip (patch +
README.txt). Refuses to overwrite an existing version's files without --force. Never publishes anything.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL as _SKILL  # noqa: E402
import version  # noqa: E402

SKILL = Path(_SKILL)  # tools/skill.py gives a str

PY = [sys.executable, "-X", "utf8"]
TMP = ROOT / "work/release_tmp"
SWEEP_OLD = ROOT / "work/qa/sweep/strings_ef19ef1b.tsv"  # the build the sweep logs ran on
KABUTO_QA = ROOT / "work/qa/kabuto"  # the Kabuto build's visual tour (its manifest gates only --game kabuto)
# per game: base ROM, build, release name, zip README, base hashes file
GAMES = {
    "kuwagata": dict(orig=ROOT / "rom/Shingata Medarot - Kuwagata Version (Japan).gba",
                     built=ROOT / "build/medarot_kuwagata_en.gba", name="Shingata_Medarot_Kuwagata_EN",
                     zreadme=ROOT / "docs/release-readme.txt"),
    "kabuto": dict(orig=ROOT / "rom/Shingata Medarot - Kabuto Version (Japan).gba",
                   built=ROOT / "build/medarot_kabuto_en.gba", name="Shingata_Medarot_Kabuto_EN",
                   zreadme=ROOT / "docs/release-readme-kabuto.txt"),
}
ORIG, BUILT, NAME = GAMES["kuwagata"]["orig"], GAMES["kuwagata"]["built"], GAMES["kuwagata"]["name"]
STRINGS = BUILT.with_suffix(".strings.tsv")


def run(step, cmd, **kw):
    print(f"== {step}: {' '.join(str(c) for c in cmd)}", flush=True)
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT, **kw)
    if r.returncode:
        sys.exit(f"RELEASE STOPPED at {step} (exit {r.returncode})")


def fail(step, why):
    sys.exit(f"RELEASE STOPPED at {step}: {why}")


def hashes(path):
    b = Path(path).read_bytes()
    return {"size": len(b), "crc32": f"{zlib.crc32(b):08X}", "md5": hashlib.md5(b).hexdigest(),
            "sha1": hashlib.sha1(b).hexdigest()}


def jp_left_inputs(strings=None):
    strings = strings or STRINGS
    TMP.mkdir(parents=True, exist_ok=True)
    keep = []
    for line in (ROOT / "tbl/jp.tbl").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([0-9A-F]{2})=", line)
        if m and (0x52 <= int(m.group(1), 16) <= 0x78 or 0xA2 <= int(m.group(1), 16) <= 0xCF):
            continue
        keep.append(line)
    (TMP / "jp_left.tbl").write_text("\n".join(keep) + "\n", encoding="utf-8")
    rows = [l.split("\t") for l in strings.read_text(encoding="utf-8").splitlines() if "\t" in l]
    # docs/jp_left_known.txt holds Kuwagata offsets: map its ids to the build's version (tools/version.py)
    known = []
    for line in (ROOT / "docs/jp_left_known.txt").read_text(encoding="utf-8").splitlines():
        off, _, why = line.partition(" ")
        known.append(f"{version.at(int(off, 16)):06X} {why}" if re.fullmatch(r"[0-9A-F]{6}", off) else line)
    (TMP / "jp_left_known.txt").write_text("\n".join(known) + "\n", encoding="utf-8")
    (TMP / "slots.txt").write_text("".join(f"{int(a, 16) - 0x8000000:X} {int(a, 16) - 0x8000000:X}\n"
                                          for _, a in rows), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    ap.add_argument("--game", choices=sorted(GAMES), default="kuwagata",
                    help="which game's patch: kuwagata (default) or kabuto (docs/re/kabuto.md)")
    a = ap.parse_args()
    g = GAMES[a.game]
    orig, built, name = g["orig"], g["built"], g["name"]
    strings = built.with_suffix(".strings.tsv")
    kabuto = a.game == "kabuto"
    out = ROOT / "release"
    bps = out / f"{name}_v{a.version}.bps"
    zpath = out / f"{name}_v{a.version}.zip"
    if (bps.exists() or zpath.exists()) and not a.force:
        fail("start", f"{bps.name} / {zpath.name} exist; pass --force to overwrite")

    run("rom check", PY + ["tools/check_rom.py"] + (["--version", "kabuto"] if kabuto else []))
    run("build", PY + ["build.py"] + (["--version", "kabuto"] if kabuto else []))
    run("tests + lint", PY + ["tools/check.py"])
    run("smoke", PY + [SKILL / "scripts/emu.py", built, "--out", "work/qa/release_smoke", "--route",
                       "tools/routes/boot.txt", "--smoke"])
    version.select(a.game)
    jp_left_inputs(strings)
    run("jp_left", PY + [SKILL / "scripts/jp_left.py", built, "--tbl", TMP / "jp_left.tbl", "--slots",
                         TMP / "slots.txt", "--known", TMP / "jp_left_known.txt"])
    # the story pass (text, shared by both games) gates both; each game's visual tour gates its own build
    manifests = [m for m in sorted((ROOT / "work/qa").rglob("manifest.tsv"))
                 if "story" in m.parts or (KABUTO_QA in m.parents) == kabuto]
    if not any("story" in m.parts for m in manifests):
        fail("qa_gate", "no story-pass manifest (work/qa/story/manifest.tsv): run tools/story.py")
    if kabuto and not any(KABUTO_QA in m.parents for m in manifests):
        fail("qa_gate", f"no Kabuto visual-tour manifest under {KABUTO_QA.relative_to(ROOT)}")
    for m in manifests:
        verdicts = m.parent / ("verdicts" if "story" in m.parts else "verdicts_final")
        if not verdicts.is_dir():
            fail("qa_gate", f"no verdicts dir {verdicts.relative_to(ROOT)} for {m.relative_to(ROOT)}")
        run(f"qa_gate {m.relative_to(ROOT)}", PY + [SKILL / "scripts/qa_gate.py", "check", m, verdicts])
    if kabuto:
        # the sweep ran on Kuwagata: its coverage holds for the 8018 Kabuto strings that are byte-identical copies
        # (script_kabuto/ "src"); the 11 Kabuto-only strings are the version's own scenes (docs/re/kabuto.md)
        print("== textcover: covered through the Kuwagata sweep (script_kabuto/ src entries); skipped here")
    else:
        run("coverage remap", PY + ["tools/coverremap.py", "work/qa/sweep", SWEEP_OLD, strings,
                                    "work/qa/sweep_remap"])
        run("textcover", PY + [SKILL / "scripts/textcover.py", "work/qa/sweep_remap", strings, "--mask",
                               "0x1FFFFFF", "--waive", "docs/text_unshown.tsv"])
    unticked = [l for l in (ROOT / "docs/polish.md").read_text(encoding="utf-8").splitlines()
                if l.startswith("- [ ]")]
    if unticked:
        fail("polish", f"{len(unticked)} unticked line(s) in docs/polish.md, first: {unticked[0][:80]}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if m := re.search(r"<(Game title|platform|publisher|year|Name[^>]*|[A-Z][a-z]+ [a-z][^>]*)>", readme):
        fail("README", f"template placeholder {m.group(0)}")
    TMP.mkdir(parents=True, exist_ok=True)
    plain = TMP / "plain.gba"
    run("debug off (plain build)", PY + ["build.py", "--out", plain] + (["--version", "kabuto"] if kabuto else []))
    if hashes(plain)["sha1"] != hashes(built)["sha1"]:
        fail("debug off", "build/ differs from a plain build.py run")

    out.mkdir(exist_ok=True)
    run("patch", PY + ["tools/bps.py", "make", orig, built, bps])
    check = TMP / "reapplied.gba"
    run("re-apply", PY + ["tools/bps.py", "apply", orig, bps, check])
    h_orig, h_built, h_check = hashes(orig), hashes(built), hashes(check)
    if h_check["sha1"] != h_built["sha1"]:
        fail("re-apply", f"patched sha1 {h_check['sha1']} != build {h_built['sha1']}")
    listing = ROOT / ("rom_kabuto.sha1" if kabuto else "rom.sha1")
    if h_orig["sha1"] not in listing.read_text(encoding="utf-8"):
        fail("base ROM", f"rom/ sha1 not the one in {listing.name}")
    for key in ("crc32", "md5", "sha1"):
        if h_orig[key].lower() not in readme.lower():
            fail("README", f"base ROM {key} {h_orig[key]} missing from README.md")
    zname = g["zreadme"].relative_to(ROOT).as_posix()
    zreadme = g["zreadme"].read_text(encoding="utf-8")
    for key in ("crc32", "md5", "sha1"):
        if h_orig[key].lower() not in zreadme.lower():
            fail("zip README", f"base ROM {key} missing from {zname}")
    if h_built["crc32"].lower() not in zreadme.lower() or h_built["crc32"].lower() not in readme.lower():
        fail("README", f"patched CRC32 {h_built['crc32']} missing from README.md or {zname}")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(bps, bps.name)
        z.writestr("README.txt", zreadme)
    print(f"\nbase    {orig.name}  size {h_orig['size']}  CRC32 {h_orig['crc32']}  MD5 {h_orig['md5']}  "
          f"SHA-1 {h_orig['sha1']}")
    print(f"patched CRC32 {h_built['crc32']}  SHA-1 {h_built['sha1']}")
    print(f"release {zpath.relative_to(ROOT)} ({zpath.stat().st_size} bytes: {bps.name} + README.txt)")


if __name__ == "__main__":
    main()
