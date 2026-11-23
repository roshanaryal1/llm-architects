#!/usr/bin/env python3
"""Reconstruct the capture-day state of GitHub references via the GitHub API.

Companion to fetch_evidence.py (criteria.md, addendum of 2026-11-23). Most Meta
references point at GitHub and have no Wayback snapshot. GitHub objects carry
their own dates, so their 31 Aug 2026 state can be rebuilt:

  commit   /commit/<sha>     immutable; commit date and message
  PR/issue /pull|issues/<n>  created_at, title, body, and when the body was last edited
                             (an edit after the cutoff means the body is not capture-day text)
  repo     /<owner>/<repo>   created_at, description, and the README at the last
                             commit on or before the cutoff
  file     /blob|tree/<ref>/<path>  the file at the last commit on or before the cutoff

Uses the authenticated `gh api` CLI (the unauthenticated rate limit is too low).
Adds per-reference JSON next to fetch_evidence.py's output and writes
github-evidence.csv (dates and SHAs only, no page text).

    python3 analysis/citation-audit/github_evidence.py --text-dir /tmp/meta-evidence
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHEET = HERE / "meta-llama-4-urls.csv"
CUTOFF = "2026-08-31T23:59:59Z"


def gh(path):
    p = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github+json", path],
                       capture_output=True, text=True, check=False)
    if p.returncode != 0:
        msg = (p.stdout + p.stderr).strip().splitlines()
        return None, (msg[-1] if msg else f"exit {p.returncode}")[:200]
    try:
        return json.loads(p.stdout), ""
    except json.JSONDecodeError:
        return None, "bad json"


EDITED_Q = ("query($o:String!,$n:String!,$num:Int!){repository(owner:$o,name:$n){"
            "issueOrPullRequest(number:$num){... on Issue{lastEditedAt} ... on PullRequest{lastEditedAt}}}}")


def body_last_edited(owner, repo, num):
    p = subprocess.run(["gh", "api", "graphql", "-F", f"o={owner}", "-F", f"n={repo}",
                        "-F", f"num={num}", "-f", f"query={EDITED_Q}"],
                       capture_output=True, text=True, check=False)
    try:
        node = json.loads(p.stdout)["data"]["repository"]["issueOrPullRequest"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return "unknown"
    return (node or {}).get("lastEditedAt") or "never"


def sha_at_cutoff(owner, repo, path=None):
    q = f"repos/{owner}/{repo}/commits?until={CUTOFF}&per_page=1"
    if path:
        q += f"&path={path}"
    data, err = gh(q)
    if not data:
        return None, None, err or "no commit before cutoff"
    return data[0]["sha"], data[0]["commit"]["committer"]["date"], ""


def file_at(owner, repo, path, sha):
    data, err = gh(f"repos/{owner}/{repo}/contents/{path}?ref={sha}")
    if not data or isinstance(data, list):
        return "", err or "path is a directory"
    try:
        return base64.b64decode(data.get("content", "")).decode("utf-8", "replace"), ""
    except Exception as e:  # noqa: BLE001 - malformed content is recorded, not raised
        return "", str(e)


def collect(url):
    m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)(/.*)?$", url)
    if not m:
        return None
    owner, repo, rest = m.group(1), m.group(2), (m.group(3) or "").rstrip("/")
    out = {"kind": "", "created": "", "state_sha": "", "state_date": "", "body_last_edited": "",
           "error": "", "text": ""}
    if mm := re.match(r"/commit/([0-9a-f]{7,40})", rest):
        out["kind"] = "commit"
        d, err = gh(f"repos/{owner}/{repo}/commits/{mm.group(1)}")
        if d:
            out["created"] = d["commit"]["committer"]["date"]
            out["state_sha"] = d["sha"]
            files = ", ".join(f["filename"] for f in d.get("files", [])[:40])
            out["text"] = f"COMMIT MESSAGE: {d['commit']['message']}\nFILES: {files}"
        out["error"] = err
    elif mm := re.match(r"/(pull|issues)/(\d+)", rest):
        out["kind"] = mm.group(1)
        d, err = gh(f"repos/{owner}/{repo}/issues/{mm.group(2)}")
        if d:
            out["created"] = d["created_at"]
            out["body_last_edited"] = body_last_edited(owner, repo, int(mm.group(2)))
            out["text"] = f"TITLE: {d['title']}\nBODY: {(d.get('body') or '')[:20000]}"
        out["error"] = err
    elif mm := re.match(r"/(blob|tree)/([^/]+)/(.+)", rest):
        out["kind"] = "file"
        path = mm.group(3)
        sha, date, err = sha_at_cutoff(owner, repo, path)
        out["state_sha"], out["state_date"] = sha or "", date or ""
        if sha:
            txt, err2 = file_at(owner, repo, path, sha)
            out["text"] = txt[:40000]
            err = err2
        out["error"] = err
    else:
        out["kind"] = "repo"
        d, err = gh(f"repos/{owner}/{repo}")
        if d:
            out["created"] = d["created_at"]
            sha, date, err2 = sha_at_cutoff(d["owner"]["login"], d["name"])
            out["state_sha"], out["state_date"] = sha or "", date or ""
            readme = ""
            if sha:
                r, _ = gh(f"repos/{d['owner']['login']}/{d['name']}/readme?ref={sha}")
                if r and r.get("content"):
                    readme = base64.b64decode(r["content"]).decode("utf-8", "replace")
            out["text"] = f"DESCRIPTION (today, not capture-day): {d.get('description') or ''}\nREADME AT CUTOFF:\n{readme[:40000]}"
            err = err2
        out["error"] = err
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    with open(SHEET, newline="") as fh:
        refs = list(csv.DictReader(fh))
    rows = []
    for r in refs:
        n = int(r["ref"])
        g = collect(r["url"])
        if g is None:
            continue
        jp = a.text_dir / f"ref-{n:02d}.json"
        data = json.loads(jp.read_text()) if jp.exists() else {"ref": n, "url": r["url"]}
        data["github"] = g
        jp.write_text(json.dumps(data, indent=1))
        rows.append({"ref": n, "kind": g["kind"], "created": g["created"],
                     "state_sha": g["state_sha"], "state_date": g["state_date"],
                     "body_last_edited": g["body_last_edited"],
                     "error": g["error"]})
        print(f"[{n:2d}] {g['kind']:<6} created={g['created'][:10]:<10} "
              f"state={g['state_date'][:10]:<10} {g['error'][:60]}", flush=True)
    with open(HERE / "github-evidence.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("wrote github-evidence.csv")


if __name__ == "__main__":
    main()
