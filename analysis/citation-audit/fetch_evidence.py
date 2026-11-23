#!/usr/bin/env python3
"""Collect evidence for the Meta citation audit (criteria.md). Stdlib only.

For each of the 99 references in meta-llama-4-urls.csv:
  * the inline claims in the capture that cite it ([[n]] markers);
  * the latest Wayback Machine capture on or before the capture day (31 Aug 2026),
    with its HTTP status, page title and plain text;
  * the live HTTP status today, for information only.

Writes:
  evidence.csv            one row per reference: snapshot timestamp/status/url, title,
                          live status (committed; no page text)
  <out>/ref-NN.json       claims plus up to 40,000 characters of archived page text,
                          for the coder to read (NOT committed: third-party content)

Usage:
    python3 analysis/citation-audit/fetch_evidence.py --text-dir /tmp/meta-evidence
"""
from __future__ import annotations

import argparse
import csv
import gzip
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CAPTURE = ROOT / "data" / "responses" / "meta-llama-4.md"
SHEET = HERE / "meta-llama-4-urls.csv"
CUTOFF = "20260831235959"
UA = "citation-audit/1.0 (research reproducibility check)"
PAUSE = 1.0


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.geturl(), r.read(2_000_000)
    except urllib.error.HTTPError as e:
        return e.code, url, b""
    except Exception as e:  # noqa: BLE001 - any network failure is recorded, not raised
        return f"error:{type(e).__name__}", url, b""


def latest_snapshot(url):
    """Latest Wayback capture at or before CUTOFF, any status. None if never captured."""
    q = urllib.parse.urlencode({"url": url, "to": CUTOFF, "output": "json", "limit": "-1"})
    status, _, body = get(f"https://web.archive.org/cdx/search/cdx?{q}")
    if status != 200 or not body.strip():
        return None
    try:
        rows = json.loads(body)
    except json.JSONDecodeError:
        return None
    if len(rows) < 2:
        return None
    _, ts, original, _, code, *_ = rows[-1]
    return {"timestamp": ts, "status": code, "original": original}


def page_text(raw):
    if raw[:2] == b"\x1f\x8b":  # Wayback id_ responses can be gzip-encoded
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass
    s = raw.decode("utf-8", "replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", s, re.DOTALL | re.IGNORECASE)
    title = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else ""
    s = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    text = re.sub(r"\s+", " ", html.unescape(s)).strip()
    return title, text


def claims_for(n, body):
    out = []
    for line in body.splitlines():
        if f"[[{n}]]" in line:
            clean = re.sub(r"\[\[(\d+)\]\]\([^)]*\)", r"[\1]", line).strip()
            out.append(clean[:600])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text-dir", type=Path, required=True,
                    help="where to write per-reference JSON with archived page text")
    ap.add_argument("--only", type=int, nargs="*", help="limit to these reference numbers")
    args = ap.parse_args(argv)
    args.text_dir.mkdir(parents=True, exist_ok=True)

    body = CAPTURE.read_text()
    with open(SHEET, newline="") as fh:
        refs = list(csv.DictReader(fh))
    rows = []
    for r in refs:
        n = int(r["ref"])
        if args.only and n not in args.only:
            continue
        url = r["url"]
        snap = latest_snapshot(url)
        time.sleep(PAUSE)
        title = text = ""
        snap_url = ""
        if snap:
            snap_url = f"https://web.archive.org/web/{snap['timestamp']}/{snap['original']}"
            if snap["status"] == "200":
                st, _, raw = get(f"https://web.archive.org/web/{snap['timestamp']}id_/{snap['original']}")
                if st == 200 and raw:
                    title, text = page_text(raw)
                time.sleep(PAUSE)
        live_status, live_final, _ = get(url, timeout=20)
        time.sleep(PAUSE)
        rows.append({
            "ref": n, "url": url,
            "snapshot_timestamp": snap["timestamp"] if snap else "",
            "snapshot_status": snap["status"] if snap else "none",
            "snapshot_url": snap_url,
            "snapshot_title": title[:200],
            "live_status_2026_11": live_status,
            "live_final_url": live_final if live_final != url else "",
        })
        (args.text_dir / f"ref-{n:02d}.json").write_text(json.dumps({
            "ref": n, "url": url, "title_as_given": r["title_as_given"],
            "source_label": r["source_label"], "claims": claims_for(n, body),
            "snapshot": snap, "snapshot_title": title, "snapshot_text": text[:40000],
            "live_status": live_status,
        }, indent=1))
        print(f"[{n:2d}] snap={rows[-1]['snapshot_status']:>4} live={live_status} {url[:80]}", flush=True)

    out = HERE / "evidence.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
