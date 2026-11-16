import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import lint  # noqa: E402
import marker  # noqa: E402

W = marker.widths()
WIN = {"variants": {"box": {"px": 40, "lines": 2, "status": "measured"},
                    "name": {"px": 24, "bytes": 3, "status": "guess"}},
       "tables": {"T": "box", "*fe": "name"}, "vars": {"00": 24}}  # A-E are 6 px each


def entry(kind):
    return {"id": "000001", "kind": kind}


def test_wrap_breaks_words_like_the_engine():
    pages, bad = lint.wrap_pages("AAAA AAAA{n}AA{page}A{end:00}", 40, W, {})
    assert [len(p) for p in pages] == [3, 1]  # "AAAA " | "AAAA" | "AA" ; "A"
    assert not bad


def test_lines_and_names_over_budget_fail():
    errs, warns = lint.lint([("T", entry("ff"), "AAAA AAAA AAAA{end:00}"),
                             ("X", entry("fe"), "ABCDE{item}")], WIN, W)
    assert len(errs) == 3  # 3 lines > 2; 30 px > 24; 5 bytes > 3
    assert any("guess" in w for w in warns)


def test_fitting_text_passes_and_var_counts():
    errs, _ = lint.lint([("T", entry("ff"), "AB{var:00}{n}AB{end:00}")], WIN, W)
    assert errs == []
    errs, _ = lint.lint([("T", entry("ff"), "ABC{var:00}{n}A{n}A{end:00}")], WIN, W)
    assert errs  # var pushes past 40 px -> wraps -> 4 lines


def test_wrapped_stub_last_line_fails_but_authored_break_passes():
    errs, _ = lint.lint([("T", entry("ff"), "AAAAAA A{end:00}")], WIN, W)  # wraps to "AAAAAA " | "A": 6 px
    assert any("stub" in e for e in errs)
    errs, _ = lint.lint([("T", entry("ff"), "AAAA{n}A{end:00}")], WIN, W)  # the author's {n}: left alone
    assert errs == []
    assert lint.lint([("T", entry("ff"), "AAAAAA A{end:00}")], WIN, W, stubs=False)[0] == []
