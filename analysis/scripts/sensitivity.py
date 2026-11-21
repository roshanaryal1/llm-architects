#!/usr/bin/env python3
"""Sensitivity and uncertainty analyses for the Cureus 2026-11-21 editorial review.

Stdlib only. Every number this script prints is computed from files already in
the repository; nothing is re-scored and no rater file is modified.

Sections (each maps to one editor issue):

  A  rater exclusion        (#3)  drop the author-derived rater; LLM-only agreement;
                                   rank-based thirds under alternative score sets
  B  dimension sensitivity  (#6)  drop weakly reliable dimensions; leave-one-out
  C  rank-based thirds      (#7)  the explicit rule that replaces the named bands
  D  bootstrap intervals    (#12) 95% percentile intervals, resampling responses
  E  memory assumptions     (#8)  break-even non-model reserve per captured design,
                                   swept over reserve and KV-cache multipliers
  F  consensus uncertainty  (#9, #12) bootstrap interval and permutation test for
                                   the structural-vs-product agreement gap

Usage:
    python3 analysis/scripts/sensitivity.py            # print everything
    python3 analysis/scripts/sensitivity.py --csv DIR  # also write CSVs for figures
    python3 analysis/scripts/sensitivity.py --boot 2000  # fewer resamples (faster)

Seeded, so repeated runs print identical output.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import agreement as ag
import consensus_split as cs
import memory_budget as mb

ROOT = HERE.parent.parent
SCORING = ROOT / "analysis" / "scoring"
DIMS = ag.DIMS
ANCHOR = "claude-sonnet-5"
SEED = 20261121

FILES = {
    "rater-1": SCORING / "scores-rater-1-2026-09-01.csv",
    "gpt-5.6-sol": SCORING / "scores-gpt-5.6-sol-2026-09-01.csv",
    "grok-4": SCORING / "scores-grok-4-2026-09-01.csv",
    "deepseek-chat": SCORING / "scores-deepseek-chat-2026-09-01.csv",
}
ADJUDICATED = SCORING / "scores-adjudicated-2026-09-01.csv"
GPT_CLEAN_D3D4 = SCORING / "scores-d3d4-gpt-5.6-sol-2026-09-01.csv"

# Per-dimension reliability tiers, from the canonical-pair unweighted kappa that
# agreement.py prints (reliable >= 0.6; weak 0.2-0.4; weakest < 0.2). D4 (0.46)
# sits between the reliable and weak tiers and is kept in every reduced set.
WEAKEST = ["D1", "D9"]
WEAK_OR_WEAKEST = ["D1", "D6", "D7", "D8", "D9"]


# ---------------------------------------------------------------- loading ---

def load_d3d4(path):
    with open(path, newline="") as fh:
        return {r["slug"]: {"D3": int(r["D3"]), "D4": int(r["D4"])}
                for r in csv.DictReader(fh)}


def load_all():
    raters = {name: ag.load(p) for name, p in FILES.items()}
    adjudicated = ag.load(ADJUDICATED)
    clean = load_d3d4(GPT_CLEAN_D3D4)
    gpt_clean = {s: dict(v) for s, v in raters["gpt-5.6-sol"].items()}
    for s, v in clean.items():
        gpt_clean[s].update(v)
    return raters, adjudicated, gpt_clean


def totals(scores, slugs, dims=DIMS):
    return {s: sum(scores[s][d] for d in dims) for s in slugs}


# ------------------------------------------------------- rank-based thirds ---

def thirds(total_by_slug):
    """Upper / middle / lower third by average rank (ties share a rank).

    With n items, an item is 'upper' if its average rank <= n/3 + 0.5,
    'lower' if >= 2n/3 + 0.5, otherwise 'middle'. For n = 12 that is
    rank <= 4.5 and rank >= 8.5. Ties straddling a boundary therefore land in
    the middle third rather than being split arbitrarily.
    """
    slugs = sorted(total_by_slug)
    vals = [-total_by_slug[s] for s in slugs]  # descending score -> rank 1 = best
    ranks = ag._rank(vals)
    n = len(slugs)
    hi_cut, lo_cut = n / 3 + 0.5, 2 * n / 3 + 0.5
    out = {}
    for s, r in zip(slugs, ranks):
        out[s] = "upper" if r <= hi_cut else ("lower" if r >= lo_cut else "middle")
    return out, dict(zip(slugs, ranks))


def compare_thirds(ref, alt):
    moved = sorted(s for s in ref if ref[s] != alt[s])
    upper_same = {s for s in ref if ref[s] == "upper"} == {s for s in alt if alt[s] == "upper"}
    lower_same = {s for s in ref if ref[s] == "lower"} == {s for s in alt if alt[s] == "lower"}
    return moved, upper_same, lower_same


def rho_between(a, b, slugs):
    return ag.spearman_rho([a[s] for s in slugs], [b[s] for s in slugs])


# --------------------------------------------------------------- bootstrap ---

def percentile(xs, q):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = (len(xs) - 1) * q
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return xs[int(k)]
    return xs[f] + (xs[c] - xs[f]) * (k - f)


def kappa_or_none(pairs, weighted=False):
    """Cohen's kappa, or None when chance agreement is 1 (undefined)."""
    cats = [0, 1, 2]
    n = len(pairs)
    ca = {c: sum(1 for a, _ in pairs if a == c) / n for c in cats}
    cb = {c: sum(1 for _, b in pairs if b == c) / n for c in cats}
    if weighted:
        pe = sum((1 - ((i - j) / 2) ** 2) * ca[i] * cb[j] for i in cats for j in cats)
    else:
        pe = sum(ca[c] * cb[c] for c in cats)
    if abs(1 - pe) < 1e-12:
        return None
    return ag.cohen_kappa(pairs, weighted)


def boot(stat, slugs, B, rng):
    """Percentile bootstrap over responses (the unit of analysis)."""
    vals, skipped = [], 0
    for _ in range(B):
        sample = [rng.choice(slugs) for _ in slugs]
        v = stat(sample)
        if v is None or (isinstance(v, float) and math.isnan(v)):
            skipped += 1
            continue
        vals.append(v)
    return percentile(vals, 0.025), percentile(vals, 0.975), skipped


def wilson(k, n, z=1.959964):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - half, centre + half


# ----------------------------------------------------------------- sections ---

def section_a(raters, adjudicated, gpt_clean, slugs12, out):
    print("=" * 74)
    print("A. RATER EXCLUSION (editor issue #3)")
    print("=" * 74)
    slugs13 = list(raters["rater-1"].keys())
    llm = ["gpt-5.6-sol", "grok-4", "deepseek-chat"]

    units_all = [[raters[r][s][d] for r in FILES] for s in slugs13 for d in DIMS]
    units_llm = [[raters[r][s][d] for r in llm] for s in slugs13 for d in DIMS]
    print(f"Krippendorff ordinal alpha, all four raters      : "
          f"{ag.krippendorff_alpha_ordinal(units_all):+.3f}")
    print(f"Krippendorff ordinal alpha, three LLM raters only: "
          f"{ag.krippendorff_alpha_ordinal(units_llm):+.3f}")
    print("\nPairwise quadratic-weighted kappa among LLM raters (117 cells each):")
    for i in range(len(llm)):
        for j in range(i + 1, len(llm)):
            pairs = [(raters[llm[i]][s][d], raters[llm[j]][s][d])
                     for s in slugs13 for d in DIMS]
            print(f"  {llm[i]:<14} vs {llm[j]:<14} kappa_w {ag.cohen_kappa(pairs, True):+.3f}"
                  f"   AC1_w {ag.gwet_ac1(pairs, True):+.3f}")

    ref_tot = totals(adjudicated, slugs12)
    ref_thirds, _ = thirds(ref_tot)
    llm_mean = {s: statistics.mean(
        [sum(gpt_clean[s][d] for d in DIMS)]
        + [sum(raters[r][s][d] for d in DIMS) for r in ("grok-4", "deepseek-chat")])
        for s in slugs12}
    conditions = [
        ("adjudicated (as reported)", ref_tot),
        ("canonical LLM rater only (GPT-5.6 Sol, clean D3/D4)", totals(gpt_clean, slugs12)),
        ("mean of the three LLM raters (no author rater)", llm_mean),
        ("Grok 4 only", totals(raters["grok-4"], slugs12)),
        ("DeepSeek chat run only", totals(raters["deepseek-chat"], slugs12)),
        ("author-derived rater only (for contrast)", totals(raters["rater-1"], slugs12)),
    ]
    print("\nRank-based thirds under alternative score sets (12 non-anchor responses):")
    print(f"  {'score set':<54}{'rho':>7}  upper  lower  moved")
    rows = []
    for name, tot in conditions:
        th, _ = thirds(tot)
        moved, up, lo = compare_thirds(ref_thirds, th)
        r = rho_between(ref_tot, tot, slugs12)
        print(f"  {name:<54}{r:>+7.2f}  {'same' if up else 'DIFF':<5}  "
              f"{'same' if lo else 'DIFF':<5}  {len(moved)}")
        if moved:
            print(f"      moved: {', '.join(f'{s} ({ref_thirds[s]}->{th[s]})' for s in moved)}")
        rows.append({"score_set": name, "rho_vs_adjudicated": round(r, 3),
                     "upper_same": up, "lower_same": lo, "moved": ";".join(moved)})
    out["rater_exclusion"] = rows

    # Agreement between LLM raters only: shows whether the reliable tier
    # depends on the author-derived rater being one side of the pair.
    pair_list = [("rater-1", "gpt-5.6-sol")] + [
        (llm[i], llm[j]) for i in range(len(llm)) for j in range(i + 1, len(llm))]
    print("\nPer-dimension unweighted kappa / Gwet AC1 (13 responses each):")
    short = {"rater-1": "author", "gpt-5.6-sol": "gpt", "grok-4": "grok", "deepseek-chat": "dschat"}
    print(f"  {'dimension':<26}" + "".join(f"{short[a] + '~' + short[b]:>16}" for a, b in pair_list))
    dim_rows = []
    for d in DIMS:
        cells = []
        for a, b in pair_list:
            pairs = [(raters[a][s][d], raters[b][s][d]) for s in slugs13]
            k = kappa_or_none(pairs)
            ac1 = ag.gwet_ac1(pairs)
            cells.append(f"{('  n/a' if k is None else f'{k:+.2f}')}/{ac1:+.2f}")
            dim_rows.append({"dim": d, "pair": f"{a} vs {b}",
                             "kappa": "" if k is None else round(k, 3), "ac1": round(ac1, 3)})
        print(f"  {d + ' ' + ag.DIM_NAMES[d]:<26}" + "".join(f"{c:>16}" for c in cells))
    print("  (first column is the canonical pair reported in the paper; the other three"
          " exclude the author-derived rater)")
    out["dimension_agreement_by_pair"] = dim_rows
    print()


def section_b(adjudicated, slugs12, out):
    print("=" * 74)
    print("B. DIMENSION SENSITIVITY (editor issue #6)")
    print("=" * 74)
    ref_tot = totals(adjudicated, slugs12)
    ref_thirds, _ = thirds(ref_tot)
    sets = [("all nine dimensions (as reported)", DIMS),
            ("drop D1 (kappa 0.15)", [d for d in DIMS if d != "D1"]),
            ("drop D9 (kappa 0.14)", [d for d in DIMS if d != "D9"]),
            ("drop D1 and D9", [d for d in DIMS if d not in WEAKEST]),
            ("drop all five weak dims (keep D2-D5)", [d for d in DIMS if d not in WEAK_OR_WEAKEST])]
    for d in DIMS:
        sets.append((f"leave out {d} only", [x for x in DIMS if x != d]))
    print(f"  {'dimension set':<40}{'max':>5}{'rho':>8}  upper  lower  moved")
    rows = []
    for name, dims in sets:
        tot = totals(adjudicated, slugs12, dims)
        th, _ = thirds(tot)
        moved, up, lo = compare_thirds(ref_thirds, th)
        r = rho_between(ref_tot, tot, slugs12)
        print(f"  {name:<40}{2 * len(dims):>5}{r:>+8.2f}  {'same' if up else 'DIFF':<5}  "
              f"{'same' if lo else 'DIFF':<5}  {len(moved)}")
        if moved:
            print(f"      moved: {', '.join(f'{s} ({ref_thirds[s]}->{th[s]})' for s in moved)}")
        rows.append({"dimension_set": name, "max": 2 * len(dims), "rho_vs_full": round(r, 3),
                     "upper_same": up, "lower_same": lo, "moved": ";".join(moved)})
    out["dimension_sensitivity"] = rows
    print()


def section_c(adjudicated, raters, gpt_clean, slugs12, out):
    print("=" * 74)
    print("C. RANK-BASED THIRDS WITH RATER RANGE (editor issue #7)")
    print("=" * 74)
    ref_tot = totals(adjudicated, slugs12)
    th, ranks = thirds(ref_tot)
    per_rater = {"rater-1": totals(raters["rater-1"], slugs12),
                 "gpt-5.6-sol (clean D3/D4)": totals(gpt_clean, slugs12),
                 "grok-4": totals(raters["grok-4"], slugs12),
                 "deepseek-chat": totals(raters["deepseek-chat"], slugs12)}
    print(f"  {'response':<28}{'adj':>5}{'rank':>6}  third   rater range (min-max)")
    rows = []
    for s in sorted(slugs12, key=lambda x: (ranks[x], x)):
        vals = [per_rater[r][s] for r in per_rater]
        print(f"  {s:<28}{ref_tot[s]:>5}{ranks[s]:>6.1f}  {th[s]:<7} {min(vals)}-{max(vals)}")
        rows.append({"slug": s, "adjudicated": ref_tot[s], "rank": ranks[s], "third": th[s],
                     **{f"total_{k}": v[s] for k, v in per_rater.items()},
                     "rater_min": min(vals), "rater_max": max(vals)})
    out["thirds"] = rows
    print()


def section_d(raters, adjudicated, slugs12, B, rng, out):
    print("=" * 74)
    print(f"D. BOOTSTRAP 95% INTERVALS (editor issue #12; {B} resamples of responses)")
    print("=" * 74)
    slugs13 = list(raters["rater-1"].keys())
    r1, r2 = raters["rater-1"], raters["gpt-5.6-sol"]

    def pairs_for(sample, dims=DIMS):
        return [(r1[s][d], r2[s][d]) for s in sample for d in dims]

    stats = [
        ("kappa unweighted", lambda smp: kappa_or_none(pairs_for(smp)), ag.cohen_kappa(pairs_for(slugs13))),
        ("kappa quadratic-weighted", lambda smp: kappa_or_none(pairs_for(smp), True),
         ag.cohen_kappa(pairs_for(slugs13), True)),
        ("Gwet AC1 quadratic-weighted", lambda smp: ag.gwet_ac1(pairs_for(smp), True),
         ag.gwet_ac1(pairs_for(slugs13), True)),
        ("Krippendorff alpha (pair)",
         lambda smp: ag.krippendorff_alpha_ordinal([[r1[s][d], r2[s][d]] for s in smp for d in DIMS]),
         ag.krippendorff_alpha_ordinal([[r1[s][d], r2[s][d]] for s in slugs13 for d in DIMS])),
        ("Krippendorff alpha (all four)",
         lambda smp: ag.krippendorff_alpha_ordinal(
             [[raters[r][s][d] for r in FILES] for s in smp for d in DIMS]),
         ag.krippendorff_alpha_ordinal([[raters[r][s][d] for r in FILES] for s in slugs13 for d in DIMS])),
    ]
    rows = []
    print("Canonical pair (author-derived baseline vs GPT-5.6 Sol), 13 responses:")
    for name, fn, point in stats:
        lo, hi, sk = boot(fn, slugs13, B, rng)
        note = f"  ({sk} degenerate resamples skipped)" if sk else ""
        print(f"  {name:<30} {point:+.2f}  [{lo:+.2f}, {hi:+.2f}]{note}")
        rows.append({"statistic": name, "scope": "canonical pair" if "four" not in name else "four raters",
                     "point": round(point, 3), "lo": round(lo, 3), "hi": round(hi, 3), "skipped": sk})

    print("\nPer-dimension unweighted kappa, canonical pair:")
    for d in DIMS:
        point = kappa_or_none(pairs_for(slugs13, [d]))
        lo, hi, sk = boot(lambda smp, d=d: kappa_or_none(pairs_for(smp, [d])), slugs13, B, rng)
        note = f"  ({sk} undefined resamples skipped)" if sk else ""
        print(f"  {d} {ag.DIM_NAMES[d]:<22} {point:+.2f}  [{lo:+.2f}, {hi:+.2f}]{note}")
        rows.append({"statistic": f"kappa {d}", "scope": "canonical pair", "point": round(point, 3),
                     "lo": round(lo, 3), "hi": round(hi, 3), "skipped": sk})

    print("\nSpearman rho between rater totals (13 responses):")
    names = list(FILES)
    tot = {n: totals(raters[n], slugs13) for n in names}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            point = rho_between(tot[a], tot[b], slugs13)
            lo, hi, sk = boot(lambda smp, a=a, b=b: ag.spearman_rho(
                [tot[a][s] for s in smp], [tot[b][s] for s in smp]), slugs13, B, rng)
            note = f"  ({sk} skipped)" if sk else ""
            print(f"  {a:<14} vs {b:<14} {point:+.2f}  [{lo:+.2f}, {hi:+.2f}]{note}")
            rows.append({"statistic": f"rho {a} vs {b}", "scope": "totals", "point": round(point, 3),
                         "lo": round(lo, 3), "hi": round(hi, 3), "skipped": sk})

    print("\nRater mean total /18 (13 responses), Table 7:")
    for n in names:
        point = statistics.mean(tot[n].values())
        lo, hi, _ = boot(lambda smp, n=n: statistics.mean(tot[n][s] for s in smp), slugs13, B, rng)
        print(f"  {n:<14} {point:5.1f}  [{lo:4.1f}, {hi:4.1f}]")
        rows.append({"statistic": f"mean total {n}", "scope": "13 responses", "point": round(point, 2),
                     "lo": round(lo, 2), "hi": round(hi, 2), "skipped": 0})

    print("\nThird-membership stability when each response's total is drawn from one")
    print("of the four raters at random (independently per response):")
    per = {n: totals(raters[n], slugs12) for n in names}
    ref_thirds, _ = thirds(totals(adjudicated, slugs12))
    same = {s: 0 for s in slugs12}
    for _ in range(B):
        draw = {s: per[rng.choice(names)][s] for s in slugs12}
        th, _ = thirds(draw)
        for s in slugs12:
            same[s] += th[s] == ref_thirds[s]
    for s in sorted(slugs12, key=lambda x: (-same[x], x)):
        print(f"  {s:<28} {ref_thirds[s]:<7} kept in {same[s] / B:6.1%} of draws")
        rows.append({"statistic": f"third kept {s}", "scope": ref_thirds[s],
                     "point": round(same[s] / B, 3), "lo": "", "hi": "", "skipped": 0})

    print("\nWilson 95% intervals for counts reported in the text:")
    for label, k, n in [("Meta URLs non-supporting or unresolvable", 59, 99)] + \
            [(f"modal agreement {k}/10", k, 10) for k in (4, 5, 6, 7, 8, 9, 10)]:
        lo, hi = wilson(k, n)
        print(f"  {label:<42} {k}/{n} = {k / n:5.1%}  [{lo:5.1%}, {hi:5.1%}]")
    out["bootstrap"] = rows
    print()


def section_e(out):
    print("=" * 74)
    print("E. MEMORY-BUDGET ASSUMPTIONS (editor issue #8)")
    print("=" * 74)
    print("Break-even non-model reserve R* = 32 - weights - KV: the largest OS + browser +")
    print("workers + DB allowance under which the stated co-resident set still fits")
    print("(free >= 0). Headroom target (free >= 2 GB) needs R <= R* - 2.")
    print("KV uses memory_budget.py's own per-1k-token rate at the preset's context;")
    print("x0.5 and x2 bracket that rate.\n")
    reserves = [6.0, 7.0, 9.0, 11.5, 13.5]
    mults = [0.5, 1.0, 2.0]
    hdr = "".join(f"{r:>7.1f}" for r in reserves)
    print(f"  {'preset':<22}{'weights':>8}{'KV':>6}{'R*(x0.5)':>10}{'R*(x1)':>8}{'R*(x2)':>8}"
          f"   verdict at R (x1 KV):{hdr}")
    rows = []
    for name in sorted(mb.PRESETS):
        if name == "over-budget-demo":
            continue  # a teaching example, not a captured design
        p = mb.PRESETS[name]
        w = sum(m[1] for m in p["models"])
        kv = mb.estimate_kv_gb(p["models"], p["ctx"], None)
        rstar = {m: mb.TOTAL_GB - w - kv * m for m in mults}
        verdict = []
        for r in reserves:
            free = mb.TOTAL_GB - w - kv - r
            verdict.append("fit" if free >= 2 else ("tight" if free >= 0 else "over"))
        print(f"  {name:<22}{w:>8.1f}{kv:>6.1f}{rstar[0.5]:>10.1f}{rstar[1.0]:>8.1f}{rstar[2.0]:>8.1f}"
              f"   {'':<21}" + "".join(f"{v:>7}" for v in verdict))
        rows.append({"preset": name, "weights_gb": w, "kv_gb": kv, "ctx": p["ctx"],
                     **{f"rstar_kv_x{m}": round(v, 2) for m, v in rstar.items()},
                     **{f"verdict_R{r}": v for r, v in zip(reserves, verdict)},
                     "over_on_weights_alone": w > mb.TOTAL_GB})
    print("\n  'over' = free < 0; 'tight' = 0 <= free < 2 GB; 'fit' = free >= 2 GB.")
    print("  R = 11.5 is memory_budget.py's defaults with the browser counted "
          "(7 OS + 1.5 workers + 0.5 DB + 2.5 browser);")
    print("  9.0 = the same without the browser; 6-7 = a lean headless host; 13.5 = heavier desktop.")
    out["memory"] = rows
    print()


def section_f(B, rng, out):
    print("=" * 74)
    print("F. CONSENSUS GAP UNCERTAINTY (editor issues #9 and #12)")
    print("=" * 74)
    st = [c for g, c, _ in cs.AXES.values() if g == "structural"]
    pr = [c for g, c, _ in cs.AXES.values() if g == "product"]
    gap = statistics.median(st) - statistics.median(pr)
    gaps = []
    for _ in range(B):
        gaps.append(statistics.median([rng.choice(st) for _ in st])
                    - statistics.median([rng.choice(pr) for _ in pr]))
    lo, hi = percentile(gaps, 0.025), percentile(gaps, 0.975)
    print(f"structural median {statistics.median(st)}/10 (n={len(st)}), "
          f"product median {statistics.median(pr)}/10 (n={len(pr)})")
    print(f"median gap {gap:+.1f}  bootstrap 95% interval [{lo:+.1f}, {hi:+.1f}] "
          f"(axes resampled within group)")
    pooled = st + pr
    obs = statistics.mean(st) - statistics.mean(pr)
    perms, hits = 20000, 0
    for _ in range(perms):
        rng.shuffle(pooled)
        a, b = pooled[:len(st)], pooled[len(st):]
        if statistics.mean(a) - statistics.mean(b) >= obs - 1e-12:
            hits += 1
    p = (hits + 1) / (perms + 1)
    print(f"difference in means {obs:+.2f}; one-sided permutation p = {p:.4f} ({perms} permutations)")
    print("Note: this tests agreement, not correctness. A high modal count says the")
    print("systems chose the same option; it does not say the option is right.")
    out["consensus"] = [{"structural_median": statistics.median(st),
                         "product_median": statistics.median(pr), "gap": gap, "lo": lo, "hi": hi,
                         "mean_diff": round(obs, 3), "perm_p": round(p, 4)}]
    print()


def write_csvs(out, directory):
    directory.mkdir(parents=True, exist_ok=True)
    for key, rows in out.items():
        if not rows:
            continue
        path = directory / f"{key}.csv"
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {path}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--boot", type=int, default=10000, help="bootstrap resamples (default 10000)")
    ap.add_argument("--csv", type=Path, default=None, help="directory to write CSV outputs")
    args = ap.parse_args(argv)

    rng = random.Random(SEED)
    raters, adjudicated, gpt_clean = load_all()
    slugs12 = [s for s in adjudicated if s != ANCHOR]
    out = {}
    section_a(raters, adjudicated, gpt_clean, slugs12, out)
    section_b(adjudicated, slugs12, out)
    section_c(adjudicated, raters, gpt_clean, slugs12, out)
    section_d(raters, adjudicated, slugs12, args.boot, rng, out)
    section_e(out)
    section_f(args.boot, rng, out)
    if args.csv:
        write_csvs(out, args.csv if args.csv.is_absolute() else ROOT / args.csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
