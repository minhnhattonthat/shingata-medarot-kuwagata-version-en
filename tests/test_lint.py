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
    errs, warns = lint.lint([("T", entry("ff"), "AAAA AAAA AAAAAA{end:00}"),
                             ("X", entry("fe"), "ABCDE{item}")], WIN, W)
    assert len(errs) == 3  # 3 lines > 2; 30 px > 24; 5 bytes > 3
    assert any("guess" in w for w in warns)


def test_fitting_text_passes_and_var_counts():
    errs, _ = lint.lint([("T", entry("ff"), "AB{var:00}{n}ABCDEF{end:00}")], WIN, W)
    assert errs == []
    errs, _ = lint.lint([("T", entry("ff"), "ABC{var:00}{n}A{n}A{end:00}")], WIN, W)
    assert errs  # var pushes past 40 px -> wraps -> 4 lines


def stub_errs(text):
    return [e for e in lint.lint([("T", entry("ff"), text)], WIN, W, page_tables=set())[0] if "stub" in e]


def test_stub_last_line_fails_wrapped_or_authored():
    assert stub_errs("AAAAAA A{end:00}")  # the engine's wrap: "AAAAAA " | "A"
    assert stub_errs("AAAA{n}A{end:00}")  # the author's {n} too
    assert stub_errs("AAAA{n}ABCD!{end:00}")  # 5 characters ("kid!", "team!")
    assert not stub_errs("AAAA{n}ABCDE!{end:00}")  # 6
    assert not stub_errs("AAAA{n}...{end:00}")  # punctuation only: a deliberate beat
    assert not stub_errs("AAAA{n}{var:00}!{end:00}")  # a name
    assert not stub_errs("ABCD{end:00}")  # one line
    assert lint.lint([("T", entry("ff"), "AAAAAA A{end:00}")], WIN, W, stubs=False)[0] == []


def test_name_blanks_follow_the_jp():
    e = dict(entry("fe"), jp="　ア")
    assert any("blanks" in x for x in lint.lint([("X", e, "AB")], WIN, W)[0])
    assert not any("blanks" in x for x in lint.lint([("X", e, " AB")], WIN, W)[0])


def page_errs(jp, en, table="T", page_tables=frozenset()):
    e = dict(entry("ff"), jp=jp)
    return [x for x in lint.lint([(table, e, en)], WIN, W, page_tables=set(page_tables))[0] if "{page} in" in x]


def test_added_page_needs_a_paging_screen():
    assert page_errs("{fa:FF}A{n}B{end:04}", "{fa:FF}ABCDEF{page}ABCDEF{end:04}")  # one-shot pane
    assert page_errs("A{n}B{fa:50}{end:04}", "ABCDEF{page}ABCDEF{fa:50}{end:04}")  # timed battle line
    assert page_errs("A{n}B{end:00}", "ABCDEF{page}ABCDEF{end:00}")  # table whose JP never pages
    assert not page_errs("A{n}B{end:00}", "ABCDEF{page}ABCDEF{end:00}", page_tables={"T"})  # JP pages here
    assert not page_errs("A{page}B{end:00}", "ABCDEF{page}ABCDEF{end:00}")  # the JP's own page
