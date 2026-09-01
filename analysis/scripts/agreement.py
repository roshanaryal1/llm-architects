#!/usr/bin/env python3
"""Inter-rater agreement for the 9-dimension rubric (issue #9).

Stdlib only. Reads analysis/scoring/scores-<rater>-<date>.csv files
(header: slug,D1..D9; cells in {0,1,2}) and reports:

  * exact and within-1 agreement, per dimension and overall
  * Cohen's kappa (unweighted and quadratic-weighted) for each rater pair
  * Krippendorff's alpha (ordinal) for the full rater set
  * per-rater mean score (severity)
  * the >=1-point disagreement list for the canonical pair (adjudication queue)

Usage:
    python3 analysis/scripts/agreement.py                 # uses the default file set
    python3 analysis/scripts/agreement.py a.csv b.csv ...  # explicit files

The FIRST file is treated as rater-1; the SECOND as the canonical rater-2.
Extra files are included in alpha and the severity table only.
"""
from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path

DIMS = [f"D{i}" for i in range(1, 10)]
DIM_NAMES = {
    "D1": "hardware-constraint", "D2": "recency", "D3": "tool-factuality",
    "D4": "model-factuality", "D5": "benchmark-factuality", "D6": "citation-quality",
    "D7": "actionability", "D8": "security-model", "D9": "internal-consistency",
}
DEFAULT_FILES = [
    "analysis/scoring/scores-rater-1-2026-09-01.csv",
    "analysis/scoring/scores-gpt-5.6-sol-2026-09-01.csv",
    "analysis/scoring/scores-grok-4-2026-09-01.csv",
    "analysis/scoring/scores-deepseek-chat-2026-09-01.csv",
]


def load(path):
    rows = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            rows[r["slug"]] = {d: int(r[d]) for d in DIMS}
    return rows


def rater_label(path):
    stem = Path(path).stem
    return stem.replace("scores-", "").rsplit("-2026", 1)[0]


def cohen_kappa(pairs, weighted=False):
    """pairs: list of (a, b) integer ratings on categories {0,1,2}."""
    cats = [0, 1, 2]
    n = len(pairs)
    if n == 0:
        return float("nan")
    # observed
    if not weighted:
        po = sum(1 for a, b in pairs if a == b) / n
    else:
        # quadratic weights: 1 - ((a-b)/(k-1))^2
        po = sum(1 - ((a - b) / 2) ** 2 for a, b in pairs) / n
    # marginals
    ca = {c: sum(1 for a, _ in pairs if a == c) / n for c in cats}
    cb = {c: sum(1 for _, b in pairs if b == c) / n for c in cats}
    if not weighted:
        pe = sum(ca[c] * cb[c] for c in cats)
    else:
        pe = sum(
            (1 - ((i - j) / 2) ** 2) * ca[i] * cb[j]
            for i in cats for j in cats
        )
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def krippendorff_alpha_ordinal(units):
    """units: list of lists; each inner list = all ratings given to one item.

    Ordinal metric on {0,1,2}. Standard formula via the coincidence matrix.
    """
    cats = [0, 1, 2]
    # coincidence matrix
    o = {(c, k): 0.0 for c in cats for k in cats}
    total_pairable = 0
    for vals in units:
        m = len(vals)
        if m < 2:
            continue
        total_pairable += m
        for a, b in itertools.permutations(vals, 2):
            o[(a, b)] += 1.0 / (m - 1)
    n = total_pairable
    if n == 0:
        return float("nan")
    nc = {c: sum(o[(c, k)] for k in cats) for c in cats}

    # ordinal difference function
    def delta(c, k):
        lo, hi = (c, k) if c <= k else (k, c)
        s = nc[lo] / 2 + nc[hi] / 2 + sum(nc[g] for g in cats if lo < g < hi)
        return s * s

    do = sum(o[(c, k)] * delta(c, k) for c in cats for k in cats)
    de = sum(nc[c] * nc[k] * delta(c, k) for c in cats for k in cats) / (n - 1)
    if de == 0:
        return 1.0
    return 1 - do / de


def main(argv):
    files = argv[1:] or DEFAULT_FILES
    raters = [(rater_label(f), load(f)) for f in files]
    slugs = list(raters[0][1].keys())

    print("=" * 70)
    print("INTER-RATER AGREEMENT — 9-dimension rubric (issue #9)")
    print("=" * 70)
    print(f"raters: {', '.join(name for name, _ in raters)}")
    print(f"items:  {len(slugs)} responses x {len(DIMS)} dimensions "
          f"= {len(slugs) * len(DIMS)} ratings each\n")

    # severity
    print("-- per-rater mean score (severity) --")
    for name, data in raters:
        allv = [data[s][d] for s in slugs for d in DIMS]
        tot = [sum(data[s][d] for d in DIMS) for s in slugs]
        print(f"  {name:<22} mean/dim {sum(allv)/len(allv):.2f}   "
              f"mean total {sum(tot)/len(tot):.1f}/18")
    print()

    r1_name, r1 = raters[0]
    if len(raters) > 1:
        r2_name, r2 = raters[1]
        print(f"-- canonical pair: {r1_name}  vs  {r2_name} --")
        allpairs = [(r1[s][d], r2[s][d]) for s in slugs for d in DIMS]
        exact = sum(1 for a, b in allpairs if a == b) / len(allpairs)
        within1 = sum(1 for a, b in allpairs if abs(a - b) <= 1) / len(allpairs)
        print(f"  overall exact agreement : {exact:5.1%}")
        print(f"  overall within-1        : {within1:5.1%}")
        print(f"  Cohen kappa (unweighted): {cohen_kappa(allpairs):+.3f}")
        print(f"  Cohen kappa (quad-wtd)  : {cohen_kappa(allpairs, True):+.3f}")
        print()
        print("  per-dimension:")
        print(f"  {'dim':<24}{'exact':>8}{'kappa':>9}{'kappa_w':>9}")
        for d in DIMS:
            dp = [(r1[s][d], r2[s][d]) for s in slugs]
            ex = sum(1 for a, b in dp if a == b) / len(dp)
            print(f"  {d + ' ' + DIM_NAMES[d]:<24}{ex:>8.0%}"
                  f"{cohen_kappa(dp):>+9.3f}{cohen_kappa(dp, True):>+9.3f}")
        print()

    # pairwise exact-agreement matrix (all raters)
    if len(raters) > 2:
        print("-- pairwise exact agreement (all raters) --")
        names = [n for n, _ in raters]
        print("  " + " " * 22 + "".join(f"{n[:10]:>12}" for n in names))
        for na, da in raters:
            cells = []
            for nb, db in raters:
                pp = [(da[s][d], db[s][d]) for s in slugs for d in DIMS]
                cells.append(sum(1 for a, b in pp if a == b) / len(pp))
            print(f"  {na:<22}" + "".join(f"{c:>11.0%} " for c in cells))
        print()

    # Krippendorff alpha over the full set
    units = [[data[s][d] for _, data in raters] for s in slugs for d in DIMS]
    print(f"-- Krippendorff alpha (ordinal, all {len(raters)} raters): "
          f"{krippendorff_alpha_ordinal(units):+.3f}")
    if len(raters) >= 2:
        units2 = [[r1[s][d], r2[s][d]] for s in slugs for d in DIMS]
        print(f"   Krippendorff alpha (ordinal, canonical pair only): "
              f"{krippendorff_alpha_ordinal(units2):+.3f}")
    print()

    # adjudication queue: >=1 point gaps on the canonical pair
    if len(raters) > 1:
        print("-- adjudication queue: canonical-pair gaps >= 1 point --")
        gaps = []
        for s in slugs:
            for d in DIMS:
                a, b = r1[s][d], r2[s][d]
                if abs(a - b) >= 1:
                    gaps.append((s, d, a, b, abs(a - b)))
        gaps.sort(key=lambda g: (-g[4], g[0], g[1]))
        print(f"  {len(gaps)} of {len(slugs) * len(DIMS)} cells "
              f"({len(gaps) / (len(slugs) * len(DIMS)):.0%})")
        for s, d, a, b, g in gaps:
            flag = "  <-- 2pt" if g == 2 else ""
            print(f"  {s:<28}{d} {DIM_NAMES[d]:<22} "
                  f"{r1_name}={a}  {r2_name}={b}{flag}")


if __name__ == "__main__":
    main(sys.argv)
