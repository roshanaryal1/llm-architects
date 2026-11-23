#!/usr/bin/env python3
"""Tally the Meta citation audit and check second-coder agreement. Stdlib only.

  python3 analysis/citation-audit/tally.py                 # first-coder result
  python3 analysis/citation-audit/tally.py --make-sample   # write the blind 20-row sheet
  python3 analysis/citation-audit/tally.py --second second-coder.csv

Derived count (criteria.md): non-supporting or unresolvable = resolves in
{no, wrong-target} or supports = none. `unknown-at-capture` rows are reported
separately and left out of the denominator.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import agreement as ag

sys.path.insert(0, str(HERE))
import claim_match as cm

SHEET = HERE / "meta-llama-4-urls.csv"
EVIDENCE = HERE / "evidence.csv"
SAMPLE = HERE / "second-coder-sheet.csv"
SEED = 20261123
RESOLVES = {"yes", "wrong-target", "no", "unknown-at-capture"}
SUPPORTS = {"full", "partial", "none", ""}


def wilson(k, n, z=1.959964):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def load(path):
    with open(path, newline="") as fh:
        return {int(r["ref"]): r for r in csv.DictReader(fh)}


def failing(r):
    return r["resolves"] in ("no", "wrong-target") or r["supports"] == "none"


def check(rows, label):
    bad = [n for n, r in rows.items()
           if r["resolves"] not in RESOLVES or r["supports"] not in SUPPORTS
           or (r["resolves"] == "yes" and not r["supports"])]
    if bad:
        raise SystemExit(f"{label}: rows not fully coded or invalid values: {bad}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--make-sample", action="store_true")
    ap.add_argument("--second", type=Path)
    a = ap.parse_args(argv)

    rows = load(SHEET)
    if a.make_sample:
        ev = load(EVIDENCE)
        gh = load(HERE / "github-evidence.csv") if (HERE / "github-evidence.csv").exists() else {}
        refs = sorted(random.Random(SEED).sample(sorted(rows), 20))

        def capture_day_link(n):
            if ev[n]["snapshot_url"]:
                return ev[n]["snapshot_url"]
            g = gh.get(n)
            if g and g["state_sha"] and g["kind"] in ("repo", "file"):
                base = "/".join(rows[n]["url"].split("/")[:5])
                return f"{base}/tree/{g['state_sha']}"
            return rows[n]["url"] if g and g["created"] else ""

        with open(SAMPLE, "w", newline="") as fh:
            w = csv.writer(fh)
            body = cm.CAPTURE.read_text()
            w.writerow(["ref", "url", "capture_day_link", "claims_citing_it",
                        "resolves", "supports", "source_tier", "notes"])
            for n in refs:
                claims = " || ".join(cm.segments(n, body))
                w.writerow([n, rows[n]["url"], capture_day_link(n), claims, "", "", "", ""])
        print(f"wrote {SAMPLE} ({len(refs)} rows: {refs})")
        return 0

    check(rows, "first coder")
    unknown = [n for n, r in rows.items() if r["resolves"] == "unknown-at-capture"]
    judged = {n: r for n, r in rows.items() if n not in unknown}
    k = sum(failing(r) for r in judged.values())
    n = len(judged)
    lo, hi = wilson(k, n)
    count = lambda col, v: sum(1 for r in judged.values() if r[col] == v)
    print(f"references: {len(rows)}; unknown at capture: {len(unknown)} {unknown}")
    print(f"non-supporting or unresolvable: {k} of {n} = {k / n:.1%} "
          f"(Wilson 95% {lo:.1%} to {hi:.1%})")
    print("resolves:", {v: count('resolves', v) for v in ('yes', 'wrong-target', 'no')})
    print("supports (resolving rows):", {v: count('supports', v) for v in ('full', 'partial', 'none')})
    print("source tier:", {v: count('source_tier', v)
                           for v in ('primary', 'secondary', 'tertiary', 'irrelevant')})

    if a.second:
        sec = load(a.second)
        check(sec, "second coder")
        common = sorted(set(sec) & set(rows))
        pairs = [(int(failing(rows[i])), int(failing(sec[i]))) for i in common]
        agree = sum(x == y for x, y in pairs)
        print(f"\nsecond coder: {len(common)} rows; agreement on the derived verdict "
              f"{agree}/{len(common)}; Cohen kappa {ag.cohen_kappa(pairs):+.2f}")
        for i in common:
            if failing(rows[i]) != failing(sec[i]):
                print(f"  disagree ref {i}: first {rows[i]['resolves']}/{rows[i]['supports']}"
                      f"  second {sec[i]['resolves']}/{sec[i]['supports']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
