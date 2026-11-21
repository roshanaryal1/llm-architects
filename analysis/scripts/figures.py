#!/usr/bin/env python3
"""Draw the manuscript's summary figures as SVG (stdlib only).

Reads the CSVs that `sensitivity.py --csv analysis/sensitivity` writes, plus the
axis counts in consensus_split.py, and writes four SVG files:

  fig1-dimension-agreement.svg  per-dimension Cohen's kappa, canonical pair, 95% bootstrap interval
  fig2-response-totals.svg      adjudicated total per response with the range across raters
  fig3-consensus-split.svg      modal agreement per decision axis, structural vs product
  fig4-memory-breakeven.svg     break-even non-model reserve per captured design

Usage:
    python3 analysis/scripts/sensitivity.py --csv analysis/sensitivity
    python3 analysis/scripts/figures.py [--in analysis/sensitivity] [--out paper/figures]

PNG export is a separate, optional step (see `make figures-png`), because it
needs a browser to rasterise the SVG.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

import agreement as ag
import consensus_split as cs

# Reference palette (light mode): surface, ink, and the first two categorical
# slots, which validate as a pair under all-pairs CVD checks.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"
S1 = "#2a78d6"  # blue
S2 = "#eb6834"  # orange
FONT = "Helvetica, Arial, sans-serif"


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [
            (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
             f'viewBox="0 0 {w} {h}" font-family="{FONT}">'),
            f"<title>{escape(title)}</title>",
            f'<rect width="{w}" height="{h}" fill="{SURFACE}"/>',
        ]

    def text(self, x, y, s, size=14, fill=INK, anchor="start", weight="normal"):
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{escape(str(s))}</text>')

    def line(self, x1, y1, x2, y2, stroke=GRID, width=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}/>')

    def circle(self, x, y, r, fill, ring=SURFACE):
        self.parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
            f'stroke="{ring}" stroke-width="2"/>')

    def save(self, path):
        path.write_text("\n".join(self.parts + ["</svg>"]) + "\n")
        print(f"wrote {path}")


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def x_axis(svg, x0, x1, y_top, y_bot, lo, hi, ticks, fmt, label):
    def sx(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    for t in ticks:
        svg.line(sx(t), y_top, sx(t), y_bot)
        svg.text(sx(t), y_bot + 20, fmt(t), 13, INK2, "middle")
    svg.text((x0 + x1) / 2, y_bot + 44, label, 14, INK2, "middle")
    return sx


def fig1(rows, out):
    dims = [r for r in rows if r["statistic"].startswith("kappa D")]
    W, L, R, T, row_h = 900, 250, 40, 80, 40
    B = T + row_h * len(dims)
    svg = Svg(W, B + 70, "Per-dimension agreement, canonical rater pair")
    svg.text(24, 32, "Per-dimension agreement between the canonical rater pair", 18, INK, weight="bold")
    svg.text(24, 54, "Cohen's kappa (unweighted), 13 responses; bar = 95% bootstrap interval "
             "(10,000 resamples of responses)", 13, INK2)
    sx = x_axis(svg, L, W - R, T - 6, B, -0.4, 1.0, [-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0],
                lambda v: f"{v:+.1f}" if v else "0", "Cohen's kappa")
    svg.line(sx(0), T - 6, sx(0), B, INK2, 1)
    for i, r in enumerate(dims):
        d = r["statistic"].split()[1]
        y = T + row_h * i + row_h / 2
        svg.text(L - 12, y + 5, f"{d} {ag.DIM_NAMES[d]}", 14, INK, "end")
        lo, hi, pt = float(r["lo"]), float(r["hi"]), float(r["point"])
        svg.line(sx(lo), y, sx(hi), y, S1, 2)
        svg.circle(sx(pt), y, 6, S1)
        svg.text(sx(pt), y - 11, f"{pt:+.2f}", 12, INK2, "middle")
    svg.save(out / "fig1-dimension-agreement.svg")


def fig2(rows, out):
    W, L, R, T, row_h = 900, 250, 40, 92, 34
    B = T + row_h * len(rows)
    svg = Svg(W, B + 70, "Adjudicated rubric total per response with rater range")
    svg.text(24, 32, "Rubric total per response (out of 18), non-anchor captures", 18, INK, weight="bold")
    svg.text(24, 54, "Dot = adjudicated total; bar = lowest to highest total from the four raters before "
             "adjudication.", 13, INK2)
    svg.text(24, 72, "Dashed lines separate rank-based thirds.", 13, INK2)
    sx = x_axis(svg, L, W - R, T - 6, B, 4, 18, list(range(4, 19, 2)), str, "Rubric total (0 to 18)")
    prev = None
    for i, r in enumerate(rows):
        y = T + row_h * i + row_h / 2
        if prev and r["third"] != prev:
            svg.line(20, T + row_h * i, W - R, T + row_h * i, INK2, 1, "4 4")
            svg.text(24, T + row_h * i + 14, f"{r['third']} third", 12, INK2)
        elif prev is None:
            svg.text(24, T + 14, f"{r['third']} third", 12, INK2)
        prev = r["third"]
        svg.text(L - 12, y + 5, r["slug"], 14, INK, "end")
        lo, hi, pt = int(r["rater_min"]), int(r["rater_max"]), int(r["adjudicated"])
        svg.line(sx(lo), y, sx(hi), y, S1, 2)
        svg.circle(sx(pt), y, 6, S1)
    svg.save(out / "fig2-response-totals.svg")


def fig3(out):
    W, L, R, T, row_h = 900, 200, 40, 80, 190
    groups = [("structural", S1, "Structural (24 axes)"), ("product", S2, "Product (9 axes)")]
    B = T + row_h * len(groups)
    svg = Svg(W, B + 70, "Modal agreement per decision axis")
    svg.text(24, 32, "Agreement per decision axis across the 10 non-anchor systems", 18, INK, weight="bold")
    svg.text(24, 54, "Each dot is one axis: how many systems chose the most common option. "
             "Black tick = group median. Agreement is not correctness.", 13, INK2)
    sx = x_axis(svg, L, W - R, T - 6, B, 3.5, 10.5, list(range(4, 11)), str,
                "Systems choosing the modal option (of 10)")
    for gi, (g, color, label) in enumerate(groups):
        base = T + row_h * (gi + 1) - 30
        svg.text(L - 12, base + 5, label, 14, INK, "end")
        counts = sorted(c for gg, c, _ in cs.AXES.values() if gg == g)
        seen = {}
        for c in counts:
            k = seen.get(c, 0)
            seen[c] = k + 1
            svg.circle(sx(c), base - 9 * k, 4, color)  # equal values stack upward
        med = statistics.median(counts)
        svg.line(sx(med) - 14, base + 14, sx(med) + 14, base + 14, INK, 3)
        svg.text(sx(med) - 18, base + 18, f"median {med:g}", 12, INK2, "end")
    svg.save(out / "fig3-consensus-split.svg")


# Presets that are not the response's stated design but an alternative reading of it
# (flagged by sensitivity.py in the memory.csv `stated_design` column).
ALT = {"deepseek-instant": "deepseek-instant (both loaded)*",
       "deepseek-expert-all": "deepseek-expert (all 3 loaded)*",
       "mistral-two-resident": "mistral (both loaded)*"}


def fig4(rows, out):
    rows = sorted(rows, key=lambda r: -float(r["rstar_kv_x1.0"]))
    W, L, R, T, row_h = 900, 250, 40, 120, 32
    B = T + row_h * len(rows)
    svg = Svg(W, B + 70, "Break-even non-model memory reserve per captured design")
    svg.text(24, 32, "Memory left for everything except the models, per stated co-resident set",
             18, INK, weight="bold")
    svg.text(24, 54, "Dot = 32 GB minus weights minus KV cache at the estimator's default rate; "
             "bar = KV rate doubled to halved.", 13, INK2)
    svg.text(24, 72, "A design fits on a host whose non-model reserve lies left of its dot. "
             "* = an alternative reading, not the stated design.", 13, INK2)
    sx = x_axis(svg, L, W - R, T - 6, B, -14, 12, list(range(-14, 13, 2)), str,
                "Break-even reserve (GB); below 0 = over 32 GB before any OS or application memory")
    svg.line(sx(0), T - 6, sx(0), B, INK2, 1)
    for ref in (7, 11.5):
        svg.line(sx(ref), T - 6, sx(ref), B, INK, 1, "5 4")
    for i, r in enumerate(rows):
        y = T + row_h * i + row_h / 2
        svg.text(L - 12, y + 5, ALT.get(r["preset"], r["preset"]), 13, INK, "end")
        lo, hi, pt = float(r["rstar_kv_x2.0"]), float(r["rstar_kv_x0.5"]), float(r["rstar_kv_x1.0"])
        svg.line(sx(lo), y, sx(hi), y, S1, 2)
        svg.circle(sx(pt), y, 5, S1)
    svg.text(sx(7) - 4, T - 10, "lean host, 7 GB", 11, INK2, "end")
    svg.text(sx(11.5) - 4, T - 26, "estimator default with browser, 11.5 GB", 11, INK2, "end")
    svg.save(out / "fig4-memory-breakeven.svg")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="src", type=Path, default=ROOT / "analysis" / "sensitivity")
    ap.add_argument("--out", type=Path, default=ROOT / "paper" / "figures")
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    fig1(read(args.src / "bootstrap.csv"), args.out)
    fig2(read(args.src / "thirds.csv"), args.out)
    fig3(args.out)
    fig4(read(args.src / "memory.csv"), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
