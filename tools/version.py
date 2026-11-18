"""version.py: which game version a build targets, and where a Kuwagata offset sits in it.

The repo's sources (tools/*.py constants, script/, gfx/labels.json) are written against the Kuwagata ROM. The Kabuto
ROM has the same code and data a few bytes away (and a handful of version-specific blocks), so every hard-coded
offset goes through at(): identity for Kuwagata; for Kabuto the segment map data/kabuto_map.tsv
(tools/romalign.py), with OVERRIDES for offsets inside blocks the two versions don't share. Each stage still checks
the bytes it expects at the mapped offset, so a wrong mapping fails the build instead of patching the wrong place.

The version comes from select() (build.py --version) or the MEDAROT_VERSION environment variable (default kuwagata),
so subprocesses and tests follow it.
"""
import functools
import os
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import romalign  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ENV = "MEDAROT_VERSION"


@dataclass(frozen=True)
class Version:
    name: str
    title: str        # for messages and the release zip
    rom: Path         # the original dump (its SHA-1: rom.sha1 / rom_kabuto.sha1, tools/check_rom.py)
    out: Path        # the default build
    script: Path      # string table files: script/ (Kuwagata) or script_kabuto/ (overlay, tools/kabuto_script.py)


VERSIONS = {
    "kuwagata": Version("kuwagata", "Kuwagata", ROOT / "rom" / "Shingata Medarot - Kuwagata Version (Japan).gba",
                        ROOT / "build" / "medarot_kuwagata_en.gba", ROOT / "script"),
    "kabuto": Version("kabuto", "Kabuto", ROOT / "rom" / "Shingata Medarot - Kabuto Version (Japan).gba",
                      ROOT / "build" / "medarot_kabuto_en.gba", ROOT / "script_kabuto"),
}
BASE = "kuwagata"   # the version the sources are written against
MAP = ROOT / "data" / "kabuto_map.tsv"

# Kuwagata offset -> Kabuto offset where the segment map has no single answer (blocks that differ between the
# versions). Each is found from the pointer that loads it (the literal at the mapped slot), see docs/re/kabuto.md.
OVERRIDES = {
    "kabuto": {
        # title screen (tools/logo.py): the shared tile block and the BG0 map hold the version's own Medabot art;
        # literals at Kuwagata 077518/077524 = Kabuto 0774FC/077508
        0x786FC4: 0x78789C,
        0x789B28: 0x78A59C,
        # minigame glyph lists (tools/minifont.py), read through the literals at 077BE4 / 0788DC (Kabuto 077BC4 /
        # 0788BC); the starter-part tutorial before them is longer in Kuwagata
        0x50EB4C: 0x50EB0C,
        0x50EC08: 0x50EBC8,
        # the starter's part tutorial table (Kuwagata: antenna head ...; Kabuto: missile head ...)
        0x50E8F4: 0x50E8B4,
    },
}


def select(name):
    if name not in VERSIONS:
        raise SystemExit(f"unknown version {name!r}: one of {', '.join(VERSIONS)}")
    os.environ[ENV] = name


def current():
    return VERSIONS[os.environ.get(ENV, BASE) or BASE]


def is_base():
    return current().name == BASE


@functools.lru_cache(maxsize=None)
def _map(name):
    return romalign.Map(romalign.load(MAP))


def at(off):
    """Kuwagata ROM offset -> the same thing's offset in the current version."""
    v = current().name
    if v == BASE:
        return off
    o = OVERRIDES[v].get(off)
    if o is not None:
        return o
    return _map(v).at(off)
