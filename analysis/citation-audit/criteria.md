# Citation-quality decision criteria

Written 2026-11-21 in response to Cureus editorial issue #10 ("manual determination of
whether citations support associated claims ... lacks detailed operational criteria").

## Status of the original pass (read first)

The Table 5 figures and the "59 of 99" Meta count come from a single-coder manual pass made
on 2026-08-31/09-01 and recorded only as summary notes in the capture's `## Reviewer notes`
(`data/responses/meta-llama-4.md`: "~60% junk URLs", "~10-15% supporting fabricated tools").
**A per-URL record of that pass was not kept**, so the 59/99 count cannot be regenerated from
the released files. `meta-llama-4-urls.csv` in this folder lists all 99 references with blank
verdict columns so the count can be re-derived against the rules below and released.

## Unit and inputs

One unit = one numbered reference in a response's citation apparatus, together with every
inline claim that cites it (`inline_uses` in the CSV). A reference cited for several claims is
judged against each claim; its `supports` verdict is the weakest of those judgements.

Snapshot rule: judge the page as of the capture window (31 August 2026). If the live page has
changed or vanished, use an archived copy dated on or before that day; if none exists, record
`resolves = unknown-at-capture` and say so in `notes`. Never infer the August state from the
current page alone.

## Axis 1: resolves

| verdict | rule |
|---|---|
| `yes` | The URL returns the document it claims to be (HTTP 200 after redirects, and the page is the cited item, not a homepage, search page or error page). |
| `wrong-target` | The URL loads, but the document is not the one the reference names (different title, different repository, different paper). Example from the corpus: reference [38] gives a real arXiv URL under a different paper's title. |
| `no` | 404 or 410, DNS failure, a repository or commit that does not exist, or a search-results URL standing in for a source. |
| `unknown-at-capture` | No way to establish the capture-window state (see snapshot rule). |

## Axis 2: supports (judged only when resolves = `yes`)

Read the cited page and each inline claim attached to it.

| verdict | rule |
|---|---|
| `full` | The page states the claim, or states facts from which it follows directly, including any number, version or attribute the claim gives. |
| `partial` | The page supports the general point but not the specific number, version, date or comparison the claim makes. A benchmark claim cited to a page with no benchmark is `partial` at best. |
| `none` | The page is about something else, or only mentions the named tool without supporting what is said about it. A commit, pull request or `SKILL.md` file cited for a performance or capability claim is `none` unless that file itself contains the evidence. |

## Axis 3: source tier

| tier | rule |
|---|---|
| `primary` | Written by the party that owns the fact: the project's own repository or docs, the vendor's release notes or model card, the paper that reports the result. |
| `secondary` | Reports a primary source with attribution: news coverage, a benchmark write-up that states its method. |
| `tertiary` | Aggregates without attribution: curated lists, "awesome" lists, comparison blogs. |
| `irrelevant` | Unrelated to the claim, or a personal repository unrelated to the cited tool. |

## Derived count

`non-supporting or unresolvable` = resolves in {`no`, `wrong-target`} **or** supports = `none`.
`partial` counts as supporting for this total and is reported separately. `unknown-at-capture`
is reported separately and excluded from the denominator.

## Coding procedure for the re-derivation

1. Fill `resolves`, `supports`, `source_tier` and a one-line `notes` per row, citing the archive
   URL used.
2. A second coder repeats a random 20 of the 99 rows blind to the first coder's verdicts;
   report the agreement on those 20 rows.
3. Report the derived count with a Wilson 95% interval and replace "59 of 99" in the
   manuscript with the re-derived figure, whatever it is.

## Addendum 2026-11-23: evidence for GitHub and dated pages (written before coding)

Only 23 of the 99 references have a Wayback capture on or before 31 August 2026. 80 point at
GitHub, whose objects carry their own dates, so their capture-day state is rebuilt with the
GitHub API (`github_evidence.py`) instead of an archive: a commit is immutable and dated; an
issue or pull request has a creation date; a repository's README and a file are read at the last
commit on or before the cutoff. A dated publication (for example a blog post with a publication
date before the cutoff) is read from its live copy, noted in `notes`. A reference that is gone
today and has no archived copy stays `unknown-at-capture`, because it may have been deleted
after the capture day.

The tally is reported two ways: strict (unknown rows left out of the denominator) and inclusive
(unknown rows counted as unresolvable). Whether a repository is a fork, and of what, is recorded
in `notes` because it bears on the source tier.

## Coding record

First pass: 2026-11-23, by an AI assistant working from the evidence files and
`claim_match.py`, with every row judged by hand against the rules above; each verdict has a
one-line reason in `notes`. Second pass: the 20 rows in `second-coder-sheet.csv`, coded blind by
the author.
