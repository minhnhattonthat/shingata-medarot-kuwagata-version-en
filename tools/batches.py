"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500] [--tables T1,T2]   work/tl/bNNN.tsv + build/terms_bNNN.txt
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/
    python -X utf8 tools/batches.py fit ID "English"      dry-run one line against its box (width, pages, codes)
    python -X utf8 tools/batches.py fixset NAME ID ...    fix batch of shipped lines: NAME.tsv + NAME.out.tsv = current en
    python -X utf8 tools/batches.py terms [bNNN ...]      rewrite build/terms_<batch>.txt from the current glossary

Copied from the skill's assets/batches.py; ADAPTER fitted to this game (script/<table>.json "strings", {codes},
widths from tools/lint.py + the English font). Identical JP in the same box variant is batched once: merge copies
the English to every entry with that JP and variant that has none yet.
Batch TSV: id, speaker, form, limit, JP. Output: work/tl/bNNN.out.tsv, id<TAB>English, every id once, same order.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lint  # noqa: E402
import marker  # noqa: E402

TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"\{\w+(?::[0-9A-Fa-f]*)?\}")  # control codes; must survive translation
FREE = {"{n}", "{page}"}  # layout codes the English may place freely (the engine word-wraps; {page} = new box)
VARIABLE = r"\{var[^}]*\}"  # a name or number the game draws: "1st" comes out as "1th"
# せんせい is left out on purpose: after a name it is often rendered "Teacher"/"Doctor", so it isn't machine-checked.
HONORIFICS = {"さん": "-san", "くん": "-kun", "ちゃん": "-chan", "さま": "-sama"}
HONORIFIC_AFTER = re.compile(r"(?:[ァ-ヿ]|\{var:00\})(さん|くん|ちゃん|さま)(?![ぁ-ゟ])")
WIN = lint.load_windows()
WIDTHS = marker.widths()


def docs():
    """(path, doc, entries) per script file; every entry gets a private '_table' key (not written back)."""
    for path in sorted(SCRIPT.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for e in doc["strings"]:
            e["_table"] = doc["table"]
        yield path, doc, doc["strings"]


def variant(entry):
    return lint.variant_for(WIN, entry["_table"], entry["kind"])


def needs_english(entry):
    """Empty JP and unused strings (no pointer slot) aren't "untranslated"."""
    return bool(TOKEN.sub("", entry.get("jp", ""))) and not entry.get("en") and bool(entry["slots"])


def group_of(entry):
    return (entry["jp"], variant(entry)[0])


def limit_label(entry):
    name, v = variant(entry)
    if entry["kind"] == "fe":
        return f"{name} {v['px']}px/{v.get('bytes', '-')}B"
    return f"{name} {v['px']}px x{v['lines']} lines per page"


def form(entry):
    return "name" if entry["kind"] == "fe" else "dlg"


def width_problems(entry, en):
    errors, warnings = lint.lint([(entry["_table"], entry, en)], WIN, WIDTHS)
    return [x.split(": ", 1)[1] if ": " in x else x for x in errors + [w for w in warnings if "not in the" in w]]


def encodable(char):
    return char in WIDTHS or char == " "
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


def problems(entry, en, terms):
    """Every rule, on one line of English."""
    jp = entry["jp"]
    if not TOKEN.sub("", en).strip():
        return ["empty English"]
    out = []
    plain = TOKEN.sub("", en)
    if bad := sorted({c for c in plain if not encodable(c) and c != "\n"}):
        out.append(f"unencodable characters {bad}")
    if re.search(r"\\u[0-9a-fA-F]{4}", en) or "\t" in en or "\n" in en or "\\n" in en:
        out.append("escape sequence, newline or tab in the English (use {n} / {page})")
    if re.search(r"\{(?!\w+(?::[0-9A-Fa-f]*)?\})", en):
        out.append("stray '{' (only control codes use braces)")
    want = Counter(t for t in TOKEN.findall(jp) if t not in FREE)
    have = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    if want != have:
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    elif [t for t in TOKEN.findall(jp) if t not in FREE] != [t for t in TOKEN.findall(en) if t not in FREE]:
        out.append("control codes out of order")
    jt, et = TOKEN.findall(jp), TOKEN.findall(en)
    if jt and et and jt[-1] != et[-1]:
        out.append(f"must end with {jt[-1]}")
    if "{page}{end" in en.replace(" ", "") or "{n}{end" in en.replace(" ", "") or "{page}{page}" in en:
        out.append("empty page or line before the end")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (write "No. {var}")')
    jp_plain = TOKEN.sub("", jp)
    # longest terms first, each masked once found: メダロット inside メダロットはかせ (Dr. Aki) needs no "Medabot"
    texts = {"all": jp_plain, "quoted": " ".join(re.findall(r"「([^」]*)」", jp_plain))}
    for jps, ens, avoid in sorted(terms, key=lambda t: -max(len(j) for j in t[0])):
        def found(j):
            # a hiragana-only term in running dialogue is often an ordinary word: enforce it only when quoted
            key = "quoted" if all(kind(c) == "hiragana" for c in j) and entry["kind"] == "ff" else "all"
            if has_term(texts[key], j):
                for k in texts:
                    texts[k] = texts[k].replace(j, "□" * len(j))
                return True
            return False
        if any([found(j) for j in jps]) and not any(e.lower() in en.lower() for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    for m in HONORIFIC_AFTER.finditer(jp):
        en_form = HONORIFICS[m.group(1)]
        if en_form.lower() not in en.lower():
            out.append(f"honorific {m.group(1)} needs {en_form}")
    return out + width_problems(entry, en)


def index():
    return {e["id"]: e for _, _, entries in docs() for e in entries}


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size, tables=None):
    """Numbers on from the last batch and leaves out JP already batched, so a repeat run can't duplicate work."""
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    ents = index()
    taken = {group_of(ents[r[0]]) for p in existing() for r in read_tsv(p) if r[0] in ents}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups = {}
    for _, doc, entries in docs():
        if tables and doc["table"] not in tables:
            continue
        for e in entries:
            if needs_english(e) and group_of(e) not in taken:
                groups.setdefault(group_of(e), e)
    batches, cur, chars, table = [], [], 0, None
    for e in groups.values():
        c = len(TOKEN.sub("", e["jp"]))
        if cur and (chars + c > size or len(cur) >= MAX_ENTRIES or e["kind"] != table):
            batches.append(cur)
            cur, chars = [], 0
        cur.append(e)
        chars += c
        table = e["kind"]
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{e['id']}\t{e.get('speaker', '')}\t{form(e)}\t{limit_label(e)}\t{e['jp']}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        write_terms(name, terms)
        print(f"{name}: {batch[0]['_table']} {len(batch)} entries")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} JP strings already batched")


def write_terms(name, terms):
    """build/terms_<batch>.txt: the glossary rows whose JP occurs in the batch (re-run after the glossary grows)."""
    jps = " ".join(TOKEN.sub("", r[-1]) for r in read_tsv(TL / f"{name}.tsv"))
    used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                  or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    out = TL / f"{batch}.out.tsv"
    if not out.exists():
        return [f"{out.name} missing"], {}
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(out)]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, en in rows:
        if eid in entries:
            bad += [f"{eid}: {p}: {en!r}" for p in problems(entries[eid], en, terms)]
    return bad, dict(rows)


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written. Copies each line to every
    untranslated entry with the same JP and box variant, and with --overwrite to every such entry still holding the
    line's old English."""
    ents = index()
    by_group = {}
    for eid, en in new.items():
        by_group[group_of(ents[eid])] = (eid, en)
    if not overwrite:
        for eid, en in new.items():
            e = ents[eid]
            if e.get("en") and e["en"] != en:
                sys.exit(f"{eid} would lose {e['en']!r}: pass --overwrite if that is meant")
    # A copy merged earlier from a line (same JP and variant, same old English) follows that line when it changes.
    old = {group_of(ents[eid]): ents[eid].get("en") for eid in new if ents[eid].get("en")}
    changed = 0
    for path, doc, entries in docs():
        touched = False
        for e in entries:
            hit = new.get(e["id"])
            g = group_of(e)
            if hit is None and g in by_group and (not e.get("en") or (overwrite and e["en"] == old.get(g))):
                hit = by_group[g][1]
            if hit is not None and e.get("en") != hit:
                e["en"], e["status"] = hit, "done"
                touched = True
                changed += 1
        for e in entries:
            e.pop("_table", None)
        if touched:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged: {changed} entries changed")


def fixset(name, ids):
    """A fix batch for shipped English: work/tl/<name>.tsv (batch rows) and <name>.out.tsv seeded with the current
    English, so a fit pass edits the live text (never a stale bNNN.out.tsv); merge it back with --overwrite."""
    ents = index()
    for path in (TL / f"{name}.tsv", TL / f"{name}.out.tsv"):
        if path.exists():
            sys.exit(f"{path} already exists")
    rows = [ents[i] for i in ids]
    (TL / f"{name}.tsv").write_text("".join(f"{e['id']}\t{e.get('speaker', '')}\t{form(e)}\t{limit_label(e)}\t{e['jp']}\n"
                                            for e in rows), encoding="utf-8", newline="\n")
    (TL / f"{name}.out.tsv").write_text("".join(f"{e['id']}\t{e['en']}\n" for e in rows), encoding="utf-8", newline="\n")
    write_terms(name, glossary())
    print(f"{name}: {len(rows)} entries")


def fit(eid, en):
    e = index()[eid]
    name, v = variant(e)
    print(f"{eid} {limit_label(e)}  JP: {e['jp']}")
    if e["kind"] == "fe":
        px, bad = lint.name_px(en, WIDTHS)
        print(f"  {px} px, {len(TOKEN.sub('', en))} bytes")
    else:
        pages, bad = lint.wrap_pages(en, v["px"], WIDTHS, WIN.get("vars", {}))
        for i, p in enumerate(pages):
            print(f"  page {i + 1}: line px {p}")
    ps = problems(e, en, glossary())
    print("OK" if not ps else "\n".join("  PROBLEM " + p for p in ps))
    return 1 if ps else 0


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        size = int(args[args.index("--size") + 1]) if "--size" in args else 3500
        tables = set(args[args.index("--tables") + 1].split(",")) if "--tables" in args else None
        return split(size, tables)
    if cmd == "fit":
        return fit(args[0], args[1])
    if cmd == "fixset":
        return fixset(args[0], args[1:])
    if cmd == "terms":
        terms = glossary()
        for name in args or [p.stem for p in existing()]:
            write_terms(name, terms)
        return 0
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e.get("en") for p in problems(e, e["en"], terms)]
        print(f"{len(entries)} entries, {len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    new, failed = {}, 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        new.update(rows)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
    if failed:
        return 1
    if cmd == "merge":
        merge(new, overwrite)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
