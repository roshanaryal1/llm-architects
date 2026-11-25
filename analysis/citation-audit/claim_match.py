#!/usr/bin/env python3
"""Coding aid for the Meta citation audit: claim segments and token matches.

For each reference, takes every sentence fragment in the capture that cites it,
extracts its checkable tokens (numbers, percentages, multipliers, and names
containing a capital letter or a digit), and reports which of them appear in
the reference's capture-day text (Wayback snapshot or GitHub state, as written
by fetch_evidence.py and github_evidence.py).

This is an aid, not a verdict: a coder reads the segments and the evidence and
records resolves / supports / source_tier by the rules in criteria.md. A token
hit can be coincidental and a miss can come from paraphrase, so every row is
judged by hand.

    python3 analysis/citation-audit/claim_match.py --text-dir /tmp/meta-evidence [--refs 1 2 3]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAPTURE = HERE.parent.parent / "data" / "responses" / "meta-llama-4.md"

STOP = {"The", "This", "For", "Use", "Run", "MLX", "Apple", "Silicon", "Mac", "GB", "API",
        "CLI", "MCP", "LLM", "AI", "OpenAI", "GitHub", "Python", "SQLite", "Docker"}


def segments(n, body):
    """The text each [n] marker is attached to: from the previous citation marker
    or sentence/cell boundary up to the marker itself."""
    out = []
    for line in body.splitlines():
        if f"[[{n}]]" not in line:
            continue
        line = re.sub(r"\[\[(\d+)\]\]\([^)]*\)", r"[\1]", line)
        line = re.sub(r"\*\*|`", "", line)
        for m in re.finditer(rf"\[{n}\]", line):
            head = line[:m.start()]
            cut = max([head.rfind(b) for b in ("] ", "]", ". ", "; ", " | ", ": ")] + [0])
            seg = head[cut:].lstrip("]|.;: ").strip()
            if seg:
                out.append(seg[-400:])
    return out


def tokens(seg, n):
    seg = re.sub(r"\[\d+\]", " ", seg)
    nums = re.findall(r"\d+(?:[.,]\d+)?\s?(?:%|×|x\b|GB|ms|s\b|k\b|B\b)?", seg)
    nums = [x.strip() for x in nums if not re.fullmatch(r"20\d\d", x.strip())]
    names = re.findall(r"\b[\w.\-/]*[A-Z0-9][\w.\-/]*\b", seg)
    names = [x for x in names if len(x) > 2 and x not in STOP and not x.isdigit()]
    seen, out = set(), []
    for t in nums + names:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out


def evidence_text(d):
    g = d.get("github") or {}
    return " ".join([d.get("snapshot_title", ""), d.get("snapshot_text", ""), g.get("text", "")])


def hit(tok, text):
    t = tok.lower().replace("×", "x").replace(",", "")
    t = re.sub(r"\s+", "", t)
    tx = re.sub(r"\s+", "", text.lower().replace("×", "x").replace(",", ""))
    if t in tx:
        return True
    base = re.sub(r"(%|x|gb|ms|s|k|b)$", "", t)
    return len(base) >= 2 and base in tx


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text-dir", type=Path, required=True)
    ap.add_argument("--refs", type=int, nargs="*")
    ap.add_argument("--json", type=Path, help="write a machine-readable summary here")
    a = ap.parse_args(argv)
    body = CAPTURE.read_text()
    summary = {}
    for f in sorted(a.text_dir.glob("ref-*.json")):
        d = json.loads(f.read_text())
        n = d["ref"]
        if a.refs and n not in a.refs:
            continue
        text = evidence_text(d)
        segs = segments(n, body)
        toks = []
        for s in segs:
            toks += [t for t in tokens(s, n) if t not in toks]
        hits = [t for t in toks if hit(t, text)]
        miss = [t for t in toks if t not in hits]
        summary[n] = {"segments": segs, "tokens": len(toks), "hits": hits, "missing": miss,
                      "evidence_chars": len(text.strip())}
        print(f"[{n:2d}] evidence {len(text.strip()):>6} chars | tokens {len(hits)}/{len(toks)} found"
              f" | missing: {', '.join(miss[:12])}")
    if a.json:
        a.json.write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
