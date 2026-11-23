#!/usr/bin/env python3
"""Archive the web evidence behind the verification register. Stdlib only.

The verdicts in tool-model-register.md rest on live repositories, model cards and
product pages that can change or disappear. This script gives each of them an
immutable Internet Archive (Wayback Machine) snapshot, so a reader can later see
what the page said when it was checked.

URLs archived:
  * every http(s) URL in tool-model-register.md;
  * every bare host/path in it (github.com/..., huggingface.co/..., getcloak.dev,
    ...), normalised to https://; file names such as README.md are not URLs and
    are skipped, as are model ids such as google/gemma-4-26B-A4B-it;
  * the extra URLs checked during the 2026-11-23 revision (REVISION_URLS).

For each URL:
  1. the Wayback CDX API gives the latest capture on or before 31 Aug 2026 (the
     corpus capture window), if one exists;
  2. Save Page Now (anonymous GET https://web.archive.org/save/<url>) requests a
     fresh capture, and the snapshot URL is read from the redirect Location or
     Content-Location header.

Requests to the Archive start at least 15 seconds apart. On HTTP 429, HTTP 5xx or
a network error the script waits 90 seconds and retries, at most twice.

Writes archived-evidence.csv (next to this script unless --out is given), one row
per URL: url, source (register | revision-2026-11-23), capture_before_cutoff,
saved_snapshot, saved_at_utc (ISO-8601, from the snapshot timestamp), status
(saved | failed:<reason>). Rows are written as they finish, so an interrupted run
keeps what it saved.

Usage:
    python3 analysis/verification/archive_evidence.py --dry-run     # list URLs only
    python3 analysis/verification/archive_evidence.py --only 2 --out /tmp/test.csv
    python3 analysis/verification/archive_evidence.py               # full run (~25 min)
    python3 analysis/verification/archive_evidence.py --resume      # only URLs not yet saved
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTER = HERE / "tool-model-register.md"
DEFAULT_OUT = HERE / "archived-evidence.csv"

CUTOFF = "20260831235959"
UA = "evidence-archiver/1.0 (research reproducibility)"
PAUSE = 15.0  # minimum seconds between the starts of two Archive requests
RETRY_WAIT = 90.0
MAX_RETRIES = 2
CDX_TIMEOUT = 60
SAVE_TIMEOUT = 180

REVISION_SOURCE = "revision-2026-11-23"
REVISION_URLS = [
    "https://github.com/navikt/cplt",
    "https://github.com/alanrbtx/DiffResearch",
    "https://github.com/visualops-ai/agent-policy-engine",
    "https://huggingface.co/Qwen/Qwen3.5-35B-A3B",
    "https://github.com/sunholo-data/ailang/commit/87202a157a461db20b0f057c30c662edb0d50fc4",
]

FIELDS = [
    "url",
    "source",
    "capture_before_cutoff",
    "saved_snapshot",
    "saved_at_utc",
    "status",
]

# Full URLs. Stops at whitespace, backticks, quotes, brackets and table pipes.
HTTP_RE = re.compile(r"https?://[^\s`<>\"'()\[\]|]+")
# Bare host[/path]. The host is lower-case and ends in a web TLD, so file names
# (README.md, matrix.csv) and model tags (Qwen3.5-35B, GLM-5.2) do not match. The
# lookbehind skips hosts inside full URLs, file paths and e-mail addresses.
BARE_RE = re.compile(
    r"(?<![\w./@:-])"
    r"((?:[a-z0-9][a-z0-9-]*\.)+(?:com|org|net|io|ai|dev|co|app|sh)(?![\w-])"
    r"(?:/[^\s`<>\"'()\[\]|,;]*)?)"
)
TRAILING = ".,;:!?*'\")]`"
SKIP_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "example.com", "web.archive.org"}
SNAPSHOT_RE = re.compile(r"/web/(\d{14})/")


def normalise(token: str) -> str | None:
    """Return a canonical https URL for a token, or None if it is not a web page."""
    token = token.strip().rstrip(TRAILING)
    if " " in token or not token:
        return None
    if not token.lower().startswith(("http://", "https://")):
        token = "https://" + token
    parts = urllib.parse.urlsplit(token)
    host = (parts.hostname or "").lower()
    if parts.scheme not in ("http", "https") or "." not in host or host in SKIP_HOSTS:
        return None
    path = parts.path.rstrip("/")
    return urllib.parse.urlunsplit((parts.scheme, host, path, parts.query, ""))


def register_urls(text: str) -> list[str]:
    """URLs and bare host/paths in the register, in order of first appearance."""
    found = []
    for m in sorted(
        [*HTTP_RE.finditer(text), *BARE_RE.finditer(text)], key=lambda m: m.start()
    ):
        url = normalise(m.group(0))
        if url:
            found.append(url)
    return found


def collect() -> list[tuple[str, str]]:
    """(url, source) pairs, deduplicated; the first source seen wins."""
    seen: dict[str, str] = {}
    for url in register_urls(REGISTER.read_text(encoding="utf-8")):
        seen.setdefault(url.lower(), url)
    rows = [(url, "register") for url in seen.values()]
    for raw in REVISION_URLS:
        url = normalise(raw)
        if url and url.lower() not in seen:
            seen[url.lower()] = url
            rows.append((url, REVISION_SOURCE))
    return rows


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Surface Save Page Now's redirect instead of downloading the snapshot."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)
_last_request = 0.0


def request(url: str, timeout: int) -> tuple[int | str, dict, bytes]:
    """One paced GET. Returns (status or 'error:<Name>', headers, body prefix)."""
    global _last_request
    wait = PAUSE - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with _OPENER.open(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read(200_000)
    except urllib.error.HTTPError as e:  # includes the 3xx we refused to follow
        body = e.read(200_000) if e.fp else b""
        return e.code, dict(e.headers or {}), body
    except Exception as e:  # noqa: BLE001 - any network failure is recorded, not raised
        return f"error:{type(e).__name__}", {}, b""


def request_with_retry(url: str, timeout: int) -> tuple[int | str, dict, bytes]:
    for attempt in range(MAX_RETRIES + 1):
        status, headers, body = request(url, timeout)
        retryable = isinstance(status, str) or status == 429 or status >= 500
        if not retryable or attempt == MAX_RETRIES:
            return status, headers, body
        print(
            f"    {status}; waiting {RETRY_WAIT:.0f}s before retry {attempt + 1}",
            flush=True,
        )
        time.sleep(RETRY_WAIT)
    raise AssertionError("unreachable")


def capture_before_cutoff(url: str) -> str:
    """Latest Wayback capture at or before CUTOFF (any status), or '' if none."""
    q = urllib.parse.urlencode(
        {"url": url, "to": CUTOFF, "output": "json", "limit": "-1"}
    )
    status, _, body = request_with_retry(
        f"https://web.archive.org/cdx/search/cdx?{q}", CDX_TIMEOUT
    )
    if status != 200:
        print(
            f"    WARNING: CDX query failed ({status}); pre-cutoff capture unknown",
            flush=True,
        )
        return ""
    try:
        rows = json.loads(body) if body.strip() else []
    except json.JSONDecodeError:
        print(
            "    WARNING: CDX reply was not JSON; pre-cutoff capture unknown",
            flush=True,
        )
        return ""
    if len(rows) < 2:
        return ""
    _, ts, original, _, code, *_ = rows[-1]
    print(f"    pre-cutoff capture {ts} (HTTP {code})", flush=True)
    return f"https://web.archive.org/web/{ts}/{original}"


def iso(ts: str) -> str:
    return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z"


def reason_from_body(body: bytes) -> str:
    """A short slug from a Save Page Now error page, for the status column."""
    text = html.unescape(
        re.sub(
            r"(?s)<(script|style)[^>]*>.*?</\1>|<[^>]+>",
            " ",
            body.decode("utf-8", "replace"),
        )
    )
    m = re.search(
        r"(?i)\b(sorry[^.]{0,80}|[^.]{0,40}\b(?:error|excluded|blocked|failed)[^.]{0,40})",
        text,
    )
    if not m:
        return "no-snapshot-url"
    return (
        re.sub(r"[^a-z0-9]+", "-", m.group(1).lower()).strip("-")[:60]
        or "no-snapshot-url"
    )


def save(url: str) -> tuple[str, str, str]:
    """Ask Save Page Now for a capture. Returns (snapshot_url, saved_at_utc, status)."""
    status, headers, body = request_with_retry(
        f"https://web.archive.org/save/{url}", SAVE_TIMEOUT
    )
    if isinstance(status, str):
        return "", "", f"failed:{status.removeprefix('error:')}"
    lower = {k.lower(): v for k, v in headers.items()}
    for key in ("location", "content-location"):
        loc = lower.get(key, "")
        m = SNAPSHOT_RE.search(loc)
        if m and 200 <= status < 400:
            snapshot = urllib.parse.urljoin("https://web.archive.org/", loc)
            return snapshot, iso(m.group(1)), "saved"
    if status >= 400:
        return "", "", f"failed:http-{status}"
    return "", "", f"failed:{reason_from_body(body)}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--dry-run", action="store_true", help="list the URLs and exit; no network"
    )
    ap.add_argument(
        "--only", type=int, metavar="N", help="process only the first N URLs"
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"CSV path (default {DEFAULT_OUT.name})",
    )
    ap.add_argument(
        "--resume",
        action="store_true",
        help="keep rows already 'saved' in --out and archive only the other URLs",
    )
    args = ap.parse_args()

    done: dict[str, dict] = {}
    if args.resume and args.out.exists():
        with args.out.open(newline="", encoding="utf-8") as fh:
            done = {r["url"]: r for r in csv.DictReader(fh) if r["status"] == "saved"}

    urls = collect()
    if args.only is not None:
        if args.only < 1:
            ap.error("--only must be at least 1")
        urls = urls[: args.only]

    if args.dry_run:
        for url, source in urls:
            print(f"{source:<20} {url}")
        print(f"{len(urls)} URLs", file=sys.stderr)
        return 0

    counts = {"saved": 0, "failed": 0, "pre_cutoff": 0}
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for i, (url, source) in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url}", flush=True)
            if url in done:
                row = {**done[url], "source": source}
                print(f"    kept {row['saved_snapshot']}", flush=True)
            else:
                before = capture_before_cutoff(url)
                snapshot, saved_at, status = save(url)
                print(f"    {status} {snapshot}", flush=True)
                row = {
                    "url": url,
                    "source": source,
                    "capture_before_cutoff": before,
                    "saved_snapshot": snapshot,
                    "saved_at_utc": saved_at,
                    "status": status,
                }
            writer.writerow(row)
            status, before = row["status"], row["capture_before_cutoff"]
            fh.flush()
            counts["saved" if status == "saved" else "failed"] += 1
            counts["pre_cutoff"] += bool(before)

    print(
        f"done: {len(urls)} URLs, {counts['saved']} saved, {counts['failed']} failed, "
        f"{counts['pre_cutoff']} with a capture on or before 31 Aug 2026 -> {args.out}",
        flush=True,
    )
    return 0 if counts["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
