# Response to the editor's comments (deferral of 21 November 2026)

<!-- DRAFT. Text in [square brackets] needs the author's decision before this is sent:
     Issue 2 (human raters), Issue 10 (re-code the Meta URLs or not), Issue 15 (archive DOI). -->

Article: "Large Language Models as Systems Architects: A Controlled Study of Consensus,
Fabrication, and Constraint Reasoning on One Hard Design Task"

Thank you for the detailed comments. I have answered each one below and revised the
manuscript within the existing online document. All new analyses are in one released,
seeded, standard-library script, so every number below can be regenerated from the released
score files. Working through the comments also turned up errors in the previous version,
including one in a released script; they are corrected and listed at the end of this letter.

## Issue 1 (Methods, extraction and rubric scoring): instrument validation

I agree that the instruments were not validated, and the revision now says so plainly. A new
paragraph in "Extraction and rubric scoring" describes how they were developed: both were
written and committed before data collection finished (the repository's first commit, which
holds four of the thirteen captures), each axis is a decision the prompt requires every
response to make, each rubric dimension targets one research question or one requested
deliverable, and each level has a written anchor. It also lists the two versioned revisions.
It then states that no expert-panel review, pilot study or psychometric validation was carried
out, and describes the limited evidence that is available: the factual dimensions are tied to
external checks, agreement is reported per dimension with intervals, and the coding is
released for audit. The paper no longer rests any conclusion on a fine-grained ranking (see
Issues 6 and 7), and the limitation is restated in "Limitations".

## Issue 2 (Methods, rater procedure): no independent human expert raters

[DECISION: keep this answer if no human raters are added; replace it if they are.]
I have taken the editor's second option and discussed explicitly how conclusions may differ
under human evaluation. The Methods now state that no independent human expert rated the
responses. A new paragraph in the Discussion separates the results by how much they depend on
raters. The fabrication result does not depend on any rater's scores: it rests on web
verification of the 19 flagged names against dated public records, which a reader can repeat
from the register. The consensus map is a coding of what each response recommends, not a
quality judgement. The rubric totals are what could change: totals for one response differ by
up to eight points across the four raters (new Figure 1), and only a few responses at the
extremes keep their third of the ranking, so the paper now says the ranking should not be
relied on beyond upper-third membership for Perplexity and Mistral Large 3 and lower-third
membership for the Zhipu, DeepSeek Expert and DeepSeek Instant-plus-DeepThink captures.

## Issue 3 (Methods, rater procedure): circularity with the author-derived rater

The Methods now give the order of work from the repository history: the rubric on 31 August
2026; the verification register on 1 September at 09:55; all four raters' scores at 12:05; the
first manuscript draft at 12:14. Scoring therefore preceded the conclusions, but the
author-derived scores were derived from reviewer notes after those notes had been corrected
against the register, so that rater was not blind to verification, and the paper says so. The
adjudication rule is now stated, with the observation that cell-wise adjudication puts three
DeepSeek totals below every rater's total.

As requested, every ranking result is now also reported without the author-derived rater (new
"Sensitivity analyses" subsection and Table 9). Using the canonical LLM rater alone, rank
correlation with the adjudicated totals is 0.80 and six of twelve responses change third;
using the mean of the three LLM raters, it is 0.85 and four change third; with every rater's
D3 and D4 taken from the clean pass, it is 0.92 and two change third. In all three, Perplexity
and Mistral Large 3 stay at the top and z-ai, DeepSeek Expert and DeepSeek Instant-plus-DeepThink
stay at the bottom; single LLM raters reorder even these, and the paper says so. Krippendorff's
alpha across the three LLM raters alone is 0.45, against 0.46 with all four. The analysis also
showed that the per-dimension reliability ordering holds only for the canonical pair, which
includes the author-derived rater; between LLM raters, agreement on the "reliable" dimensions
is much lower. The text now says this instead of describing those dimensions as reliable in
general.

## Issue 4 (Results and Discussion, architectural consensus): generalisability

The study is now framed as a single-task case study in the Abstract, Introduction,
Limitations and Conclusion. The Discussion says that because the study uses one hardware
specification, consensus forced by the 32 GB ceiling cannot be separated from consensus that
would hold on any host, and it separates the constraint-shaped agreements from the ones that
are standard distributed-systems practice.

## Issue 5 (Results and Discussion, apparent fabrication): demonstration, not prevalence

The conclusions now present the rater failure as a demonstration. The Abstract and Conclusion
say the study shows that this failure occurs and does not estimate how often it occurs across
tasks. The Introduction says the judge "can emit" false-positive flags instead of
"systematically emits", and a Discussion paragraph lists what the result does not show:
frequency, magnitude on other tasks, and whether other raters share it. The counts are also
corrected (see the corrections below): the rater flagged 19 names, grouped as 14 entries in
Table 3, of which 15 are real and four unresolved.

## Issue 6 (Statistical analysis): weakly reliable dimensions

New dimension sensitivity analyses (Methods and "Sensitivity analyses", Table 9). Leaving out
any single dimension gives totals that rank-correlate 0.96 to 1.00 with the full totals and
moves at most one response between thirds. Dropping both of the weakest dimensions (D1 and D9)
moves three responses (rho 0.96); keeping only the four more reliable dimensions also moves
three (rho 0.87). Perplexity, z-ai, DeepSeek Expert and DeepSeek Instant-plus-DeepThink keep
their position in every set. The per-dimension kappa values now carry bootstrap intervals
(Figure 4); the intervals for D1 and D9 include zero.

## Issue 7 (Statistical analysis): the Strong, Good, Mixed and Weak bands

I agree the boundaries were not justified; the boundary between the two upper bands rested on
a one-point gap. The named bands are removed. Table 8 now reports continuous adjudicated
totals, each response's range across raters, and a rank-based third (the upper, middle and
lower four of twelve by rank, with a tie group placed in an outer third only if all its tied
positions fall inside it). That rule has no tuned threshold, and the sensitivity analyses
report which responses change third under every alternative.

## Issue 8 (Methods, memory-budget estimation): assumptions

The memory analysis now reports, for each design, the break-even reserve: how much memory the
stated co-resident models and key-value cache leave for everything else. It is computed with
the key-value rate halved, as set and doubled, and compared with the estimator's 11.5 GB
desktop default, a 9 GB browser-free reserve and a 7 GB lean-host bound (new Figure 2). No
stated design fits under the 11.5 GB default; most single-large-model designs need a reserve
between 7.1 and 8.7 GB, so whether they
fit depends on the assumption more than on the design, and the text now says so. Only one
design, DeepSeek Instant-plus-DeepThink, exceeds 32 GB before any operating-system memory at
every key-value rate tested. Where a response's stated model sizes are known to be wrong
(Zhipu), the text now separates the response's own arithmetic from the verified sizes.

## Issue 9 (Results and Discussion, architectural consensus): consensus is not validity

The sentence claiming that the split "separates robust architectural principles from
fast-moving product preference" is removed. The Abstract, the consensus results, the new
Discussion and the Conclusion now say that agreement is not evidence that the shared choices
are correct, that a shared training diet or a shared reading of the prompt could produce
agreement on a poor choice, and that the consensus map shows where the systems diverge without
certifying the choices they share. The structural-versus-product gap now carries a bootstrap
interval for the median difference (two to six points) and a permutation test of the mean
difference (p < 0.001), with its exchangeability assumption stated; both are described as tests
of agreement, not of correctness.

## Issue 10 (Results and Discussion, citation quality): operational criteria

The Methods now give the decision rules for the three citation axes (resolves, supports,
source tier), including how archived copies are used for pages that have changed since the
capture window. The full rules, with examples, are released with the data. In preparing this
I found that the classification of the Meta capture's 99 references was a single-coder pass
recorded only as summary notes, without a per-URL record. Because that count cannot be
reproduced, the manuscript now reports the Meta assessment qualitatively, without the earlier
"59 of 99" figure, and the 99 references are released as an audit sheet against the published
rules.
[DECISION: if the 99 references are re-coded before resubmission, replace the last two
sentences with the re-derived count, its interval, and the agreement on the double-coded
sample.]

## Issue 11 (Minor, organisation): results and interpretation interwoven

The journal's article type combines Results and Discussion, so I kept the single section but
restructured it: the first nine subsections now report observations only, and interpretation
is collected in a new "Discussion" subsection (consensus versus validity, what the fabrication
result does and does not show, and the effect of having no human raters).

## Issue 12 (Minor, tables): uncertainty measures

Agreement statistics, rank correlations and rater means now carry 95% bootstrap intervals
(10,000 resamples of responses), and counts out of ten carry Wilson intervals. Table 7 gains an
interval column; Tables 2 to 6 gain notes on uncertainty or on what each row represents; Table
8 is replaced with continuous totals and rater ranges; Table 9 is new.

## Issue 13 (Minor, introduction): architecture-generation literature

The final Introduction paragraph now discusses LLM work at the architecture level: an empirical
study of LLM-generated architecture decision records [14] and a multivocal review of generative
AI for software architecture [15], and positions this study against them (both judge a
decision against a human reference; whole-system design under a fixed resource envelope has no
reference design). Both references were checked against their publisher records.

## Issue 14 (Minor, figures): no figures

Four figures are added, each drawn by a released script from the released data: rubric totals
with the range across raters (Figure 1), break-even memory reserves (Figure 2), agreement per
decision axis (Figure 3) and per-dimension agreement with intervals (Figure 4).

## Issue 15 (Minor, references): dynamic online sources

[DECISION: requires the archived release to exist before sending.]
The corpus, verification register, score files, analysis outputs and scripts are fixed in an
archived release of the repository, cited in "Limitations" with its DOI. Each capture is a
dated snapshot, and the citation rules require archived copies for pages that have changed
since the capture window.

## Corrections found during this revision

1. **Krippendorff's alpha.** The released agreement script gave identical ratings a non-zero
   ordinal distance, which understated alpha (perfect agreement scored 0.5). Corrected and
   cross-checked against the `krippendorff` package: 0.60 for the canonical pair (previously
   reported as 0.20) and 0.46 for all four raters (previously 0.12). The earlier explanation of
   the gap between alpha and weighted kappa as a prevalence effect was written for the wrong
   values and is removed.
2. **Fabrication counts.** The previous text said the rater flagged 14 names, of which at least
   twelve were real and four unresolved, which cannot all be true. Table 3 lists 19 names in 14
   entries: 15 real (twelve at the first verification pass, three on a follow-up) and four
   unresolved. The text now uses those counts and describes the real projects as many released
   or renamed after the rater's cutoff, rather than asserting a count of post-cutoff releases.
3. **Clean re-scoring counts.** The previous text said the clean pass changed two cells
   attributable to the leak and that the canonical rater reproduced its scores on 11 of 13
   responses. The score files show three changed cells, so 10 of 13. The text now gives those
   counts and says the comparison cannot separate the leak from new verification evidence.
4. **Memory description and verdicts.** The previous Methods text described a reserve breakdown
   (about 5, 1.5, 2 and 1 GB plus a 2 GB floor) and an 8-bit key-value cache that did not match
   the released estimator (7, 1.5, 0.5 and 2.5 GB, a 2 GB headroom test, a per-token key-value
   rate). It also said the Zhipu design exceeds 32 GB on model weights alone; on its own stated
   sizes it does not, but those sizes are wrong, and on the verified sizes the primary model
   alone needs about 40 GB. Both are corrected. DeepSeek Instant's stated design (one large
   model at a time, with a 9B summarizer alongside) now has its own estimate; the earlier preset
   loaded both large models.
5. **DeepSeek modes.** The previous text said the three modes spanned three rubric tiers with
   weights held fixed. Their adjudicated totals are 9, 8 and 6, all in the lower third, and two
   captures record the model version as not shown. The text now reports the observed
   differences (six of nine dimensions) and describes the comparison as one of chat modes, not
   a controlled same-weights experiment.
6. **Reliable dimensions.** The previous text described recency, tool factuality and benchmark
   factuality as reliable. That holds for the canonical rater pair only and is now stated that
   way.
7. **Kendall's tau-b.** The released script counted pairs tied in both variables toward both
   tie terms. Corrected to match the standard definition; the mean over rater pairs moves from
   0.276 to 0.284 and the reported 0.28 is unchanged.
8. **Prompt sensitivity.** The previous text said every one of the 15 paraphrase-study captures
   kept its architecture and that GPT-5 and Perplexity held their model identity. Zhipu's base
   capture differs from its variants on model residency and the Perplexity ablation capture is
   incomplete; the GPT-5 base capture was the free-tier GPT-5.6 Luna and its variants the
   paid-tier GPT-5.6 Sol, and Perplexity does not disclose its model. The text now reports these
   exceptions and treats the comparison as one of product sessions, not fixed models.
9. **References.** References [1] and [4] have seven and six authors and are now listed in full,
   per the journal's rule; they had been cut to "et al.".

Two release-file fixes were also made that do not change any reported number: labels in the
estimator's presets that still called two verified models fabricated were corrected, and the
preset that loads both of DeepSeek Instant's large models is now marked as an alternative
reading.
