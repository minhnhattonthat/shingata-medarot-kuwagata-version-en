"""The debug scene list parses the way warp.lua reads it: name<TAB>{table}<TAB>description, unique names."""
import re
from pathlib import Path

SCENES = Path(__file__).resolve().parents[1] / "tools" / "debug" / "scenes.txt"
LINE = re.compile(r"^([A-Za-z0-9_]+)\t+(\{[^\t]*\})\t+\S")


def test_scene_lines_parse():
    names = []
    for n, line in enumerate(SCENES.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        m = LINE.match(line)
        assert m, f"scenes.txt:{n} does not parse: {line!r}"
        assert m.group(2).count("{") == m.group(2).count("}"), f"scenes.txt:{n} unbalanced braces"
        assert re.search(r"\b(map|mode|run|events)\s*=", m.group(2)), f"scenes.txt:{n} has no map/mode/run/events"
        names.append(m.group(1))
    assert len(names) == len(set(names)), "duplicate scene names"
    assert len(names) >= 30
