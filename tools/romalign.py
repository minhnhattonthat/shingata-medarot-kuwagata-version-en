"""romalign.py: map offsets of the Kuwagata ROM to the Kabuto ROM (or any two builds of one game).

The two versions share code and data, but every block after the first difference sits a few bytes away. Anchors are
16-byte windows at 4-aligned offsets of A that occur exactly once (4-aligned) in B; runs of anchors with one delta
grow byte by byte while the bytes still match, giving segments (a_start, a_end, delta) of identical bytes. A gap
between two segments of the same delta is the same layout with a few changed bytes (BL offsets, literals); a gap
between different deltas is content that moved or differs between the versions.

    python -X utf8 tools/romalign.py A.gba B.gba --out data/kabuto_map.tsv   # write the segment map
    python -X utf8 tools/romalign.py A.gba B.gba --at 548E7C 786FC4          # map single offsets (hex)

tools/version.py loads the map; every hard-coded offset the build uses is mapped through it and checked against
the bytes it expects (tests/test_kabuto.py).
"""
import argparse
import bisect
import sys
from pathlib import Path

W = 16


def _plain(win):
    return len(set(win)) < 5  # padding, fills and runs: not unique enough to anchor on


def segments(a, b):
    idx = {}
    for i in range(0, len(b) - W, 4):
        k = b[i:i + W]
        if _plain(k):
            continue
        idx[k] = -1 if k in idx else i
    anchors = []
    for p in range(0, len(a) - W, 4):
        k = a[p:p + W]
        j = idx.get(k, -1)
        if j >= 0 and not _plain(k):
            anchors.append((p, j - p))
    segs = []  # [start, end) in A, delta
    for p, d in anchors:
        if segs and segs[-1][2] == d and p < segs[-1][1] + 4 * W:
            if all(a[x] == b[x + d] for x in range(segs[-1][1], p)):
                segs[-1][1] = p + W
                continue
        if segs and p < segs[-1][1]:
            continue  # inside the last segment already
        segs.append([p, p + W, d])
    # grow each segment both ways while bytes match, within the neighbours' bounds
    for n, s in enumerate(segs):
        lo = segs[n - 1][1] if n else 0
        hi = segs[n + 1][0] if n + 1 < len(segs) else len(a)
        st, en, d = s
        while st > lo and 0 <= st - 1 + d < len(b) and a[st - 1] == b[st - 1 + d]:
            st -= 1
        while en < hi and en + d < len(b) and a[en] == b[en + d]:
            en += 1
        s[0], s[1] = st, en
    return [tuple(s) for s in segs]


def load(path):
    segs = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            st, en, d = line.split("\t")
            segs.append((int(st, 16), int(en, 16), int(d)))
    return segs


class Map:
    """offset in A -> offset in B. exact(): only inside a matching segment; at(): also inside a gap whose two
    neighbour segments share the delta (same layout, a few changed bytes)."""

    def __init__(self, segs):
        self.segs = sorted(segs)
        self.starts = [s[0] for s in self.segs]

    def segment(self, off):
        n = bisect.bisect_right(self.starts, off) - 1
        if n >= 0 and off < self.segs[n][1]:
            return self.segs[n]
        return None

    def exact(self, off):
        s = self.segment(off)
        return None if s is None else off + s[2]

    def at(self, off):
        s = self.segment(off)
        if s:
            return off + s[2]
        n = bisect.bisect_right(self.starts, off) - 1
        if 0 <= n < len(self.segs) - 1 and self.segs[n][2] == self.segs[n + 1][2]:
            return off + self.segs[n][2]
        raise KeyError(f"{off:06X}: between segments of different deltas, no single mapping")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--at", nargs="*", default=[])
    ap.add_argument("--min", type=int, default=64, help="drop segments shorter than this (bytes)")
    a = ap.parse_args()
    da, db = a.a.read_bytes(), a.b.read_bytes()
    segs = [s for s in segments(da, db) if s[1] - s[0] >= a.min]
    if a.out:
        a.out.write_text(f"# {a.a.name} -> {a.b.name}: a_start a_end(excl) delta, identical bytes (tools/romalign.py)\n"
                         + "".join(f"{s:06X}\t{e:06X}\t{d}\n" for s, e, d in segs), encoding="utf-8", newline="\n")
    m = Map(segs)
    covered = sum(e - s for s, e, _ in segs)
    print(f"{len(segs)} segments, {covered:#x} of {len(da):#x} bytes matched ({100 * covered / len(da):.1f}%)")
    for h in a.at:
        off = int(h, 16)
        try:
            print(f"{off:06X} -> {m.at(off):06X}" + ("" if m.exact(off) is not None else " (gap)"))
        except KeyError as e:
            print(e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
