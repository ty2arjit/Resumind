# Resumind ATS Evaluation Report (Phase 13)

**Controlled internal benchmark evaluation.** This report describes how
the Resumind ATS pipeline behaves against a small, hand-labeled dataset
run through the real Phase 2-7 pipeline. It is **not** a claim of
scientific validation, hiring-outcome prediction, or parity with
commercial ATS systems (Workday, Greenhouse, Lever, Taleo, iCIMS, etc.).
No such comparison is made anywhere in this report.

- `evaluation_version`: `EVAL_V1`
- `dataset_version`: `EVAL_DATASET_V1`
- `scoring_config_version`: `SCORING_CONFIG_V1`
- Machine-readable snapshot: [`docs/evaluation/EVAL_REPORT_V1.json`](evaluation/EVAL_REPORT_V1.json)
- Framework code: `Backend/fastapi_app/app/modules/evaluation/`
- Regression/adversarial/golden tests: `Backend/fastapi_app/tests/evaluation/`

## 1. Architecture

```
EvaluationCase dataset (dataset.py)
        ↓
run_evaluation() — runs the REAL Phase 2/3/7 pipeline per case
        ↓
CaseResult (expected vs actual per requirement)
        ↓
matching_metrics / error_analysis / score_statistics / performance
        ↓
EvaluationReport
```

The evaluation module is entirely read-only with respect to production
code — it imports `ScoringService`, the resume/JD parsers, and reuses
`tests/fixtures/builders.build_pdf()` for real PDF text extraction. It
never reimplements matching or scoring, and nothing in this phase
persists to a database (Postgres is unreachable in this environment —
consistent with every prior phase in this session).

## 2. Dataset

15 hand-written cases across 10 of spec §5's categories: exact match,
canonical match, semantic match, distinct-technology (4 adversarial
cases), missing skill, partial requirement, critical requirement,
experience requirement (×2), qualification requirement (×2), and
unknown-vs-confidently-absent. Keyword stuffing, duplicate content, and
massive-skills-section are covered separately in
`tests/evaluation/test_adversarial.py` as comparative (not
single-case-labeled) tests, since they compare *two resumes'* scores
rather than asserting one requirement's status.

## 3. Matching Metrics (binary: "is this requirement satisfied")

| Metric | Value |
|---|---|
| Precision | 0.75 |
| Recall | 0.75 |
| F1 | 0.75 |
| True Positive / False Positive / True Negative / False Negative | 3 / 1 / 10 / 1 |
| Exact 4-way bucket accuracy (matches/partial/missing/unknown) | 0.80 (12/15) |

These numbers describe performance on this 15-case controlled benchmark
only. They are not statistically meaningful at this sample size — no
confidence interval is claimed, and the dataset should grow before these
numbers are treated as anything beyond "the framework works and can
find real bugs" (see §5).

## 4. Score Distribution

- Count: 15, Min: 0, Max: 100, Mean: 34
- Scores ≤10: 9 cases (mostly the deliberately-negative distinct-technology and missing-skill cases)
- Scores ≥90: 0 cases
- No cases clustered artificially near 100; no unexpected jumps observed across the dataset.

The distribution skews low because the dataset intentionally contains
many adversarial/negative cases (guardrail testing) rather than being a
representative sample of "typical" resume/JD pairs — this is expected
and by design, not a system defect.

## 5. Error Analysis

### FALSE POSITIVE

**Case:** `CASE_F1_PARTIAL_SKILL_MENTION`
**Requirement:** "Experience with Python." — resume has "Python, SQL" in
Skills plus one unrelated bullet ("Analyzed sales data.")
**Expected:** PARTIAL. **Actual:** STRONG (0.86).
**Likely cause:** with only a bare skills-section mention and no
technology-tagged bullet, the fused signal (exact + canonical entity
match against the SKILLS_SECTION evidence item) alone is enough to clear
the STRONG threshold (0.85) — the "confirmed-identity floor" in
`matching/fusion.py` (exact/canonical == 1.0 → floor at the PARTIAL
threshold) combines with generally-high keyword/context signal for a
short exact-phrase skill mention to land at 0.85-0.88, indistinguishable
from a resume with genuine demonstrated experience.
**Relevant module:** `app/modules/matching/fusion.py`,
`app/modules/scoring/config.py` (`SignalFusionWeights`).
**Potential fix (not applied):** lower the per-item ceiling a bare
`SKILLS_SECTION`-only match can reach absent any `EXPERIENCE_BULLET`/
`PROJECT_BULLET` evidence for the same technology — e.g. cap fused score
at the WEAK/PARTIAL boundary when the only supporting evidence context
is `SKILLS`. This directly targets spec Phase 10 §10's stated goal
("skill mention" vs "demonstrated experience") without touching the
general fusion formula.

### FALSE NEGATIVES

**Case:** `CASE_B1_CANONICAL_POSTGRES_ALIAS`
**Requirement:** "Experience with PostgreSQL." — resume says "Optimized
Postgres queries..." (canonical alias, real evidence).
**Expected:** matches (STRONG/VERY_STRONG). **Actual:** PARTIAL (0.59).
**Likely cause:** the canonical-alias resolution itself is correct
(Phase 4 normalization resolves Postgres→PostgreSQL), but the fused
score lands at 0.59 — just under the 0.60 PARTIAL threshold's ceiling
and short of STRONG (0.85). This is the same "confirmed-identity floor"
mechanism from Phase 5 (§21): it guarantees at least PARTIAL for a
confirmed canonical match, but does not push a single-evidence-item case
any higher than that floor.
**Relevant module:** `app/modules/matching/fusion.py`'s
`fuse_signals()`, specifically the floor's target threshold
(`thresholds.partial`, currently 0.60).
**Potential fix (not applied) — calibration proposal:**

| | Current | Proposed | Reason | Evidence |
|---|---|---|---|---|
| Confirmed-identity floor target | `match_strength_thresholds.partial` (0.60) | consider a dedicated, slightly higher floor (e.g. 0.70) specifically for canonical (not just exact) matches with a supporting EXPERIENCE/PROJECT bullet | A canonical alias with genuine bullet evidence (not just a bare mention) should reliably clear PARTIAL into STRONG range | This case: relevance 0.59, evidence is a real dated bullet with a metric ("reduced latency by 35%"), yet capped near the PARTIAL floor |

This proposal is **not applied** — one case is not sufficient evidence
to retune a shared threshold used across the whole scoring engine. It is
recorded here for a future evaluation cycle with a larger dataset.

**Case:** `CASE_C1_SEMANTIC_DB_OPTIMIZATION`
**Requirement:** "Optimize database performance." (a `RESPONSIBILITY`
type requirement with no associated `technologies`) — resume: "Optimized
PostgreSQL queries and reduced latency by 35% through indexing."
**Expected:** partial (WEAK/PARTIAL). **Actual:** MISSING (0.06).
**Likely cause:** confirmed via direct signal inspection — the top
evidence item has `semantic_similarity=0.61` (a meaningfully high
topical match) but `lexical_relevance=0.0` and
`canonical_entity_match=0.0` (no shared technology term to anchor
exact/canonical matching, since this requirement carries no
`technologies` list). With exact/canonical excluded from the fusion
average (both `None`), the remaining signals still produce a relevance
of only 0.28 — just under the WEAK threshold (0.30) — so no floor
applies and it defaults to MISSING's near-zero anchor score.
**Relevant module:** `app/modules/matching/fusion.py` (signal
redistribution when `exact`/`canonical` are `None`),
`app/modules/scoring/config.py` (`SignalFusionWeights`,
`MatchStrengthThresholds.weak`).
**Potential fix (not applied) — calibration proposal:**

| | Current | Proposed | Reason | Evidence |
|---|---|---|---|---|
| `MatchStrengthThresholds.weak` | 0.30 | consider 0.25, **only** for technology-less `RESPONSIBILITY`/experience-description requirements | 0.61 semantic similarity is a real, meaningful topical match that the current 0.30 floor discards entirely, producing a MISSING label for evidence a human reviewer would likely call "reasonably relevant" | This case: relevance 0.28 vs threshold 0.30 — a 0.02 gap flips VERY_STRONG-adjacent semantic similarity into the harshest possible label |

Also **not applied** for the same reason (insufficient sample size) —
flagged for the next evaluation cycle.

## 6. Sensitivity Analysis

Using the monotonicity fixture (§8) as the sensitivity probe: moving a
required skill from "in Skills only" to "in Skills + one dated
experience bullet with a metric" changed the requirement's status from
STRONG (0.85) to VERY_STRONG-adjacent territory is not observed here
(both land STRONG-ish), but changed the overall ATS Alignment
meaningfully (see §8). Adding a single unrelated critical requirement
(`CASE_I1`) drops ATS Alignment to near-zero (score 2/100) — consistent
with expected proportional behavior for a JD with only one, unmet,
required item. A fuller sensitivity sweep (one skill at a time,
preferred vs required, critical flag on/off) is already covered by
existing Phase 7 unit tests (`tests/unit/scoring/test_requirement_scoring.py`)
and was not duplicated here.

## 7. Adversarial Testing (`tests/evaluation/test_adversarial.py`)

- **Keyword stuffing** ("Python" ×20 in Skills vs. one genuine mention +
  strong bullet): scores land within 1 point of each other (85 vs 85) —
  stuffing does **not** provide a meaningful advantage, and does not
  scale with repetition count (Phase 6's deduplication collapses the 20
  repeated mentions to one evidence item before scoring).
- **Duplicate experience/project entries**: duplicating an identical
  bullet across Experience and Projects does not multiply the score
  (bounded well under a 1.5× increase in the test).
- **Copying JD language verbatim with no real evidence** ("Experience
  with Python." pasted into a Summary, with unrelated Skills): does not
  reach VERY_STRONG.
- **Massive irrelevant skills section** (10 unrelated tools): the
  targeted requirement remains MISSING/UNKNOWN — bulk-listing unrelated
  keywords provides no benefit to unrelated requirements.

## 8. Score Monotonicity (`tests/evaluation/test_monotonicity.py`)

**A real bug was found and fixed by this test** (see §9). After the fix:
adding progressively stronger PostgreSQL evidence (none → bare skill
mention → skill mention + a dated, metric-bearing experience bullet)
produces a non-decreasing ATS Alignment score, as required.

## 9. Production Bug Found and Fixed

**This is the most significant outcome of Phase 13.** The monotonicity
test above initially failed: a resume with a bare "PostgreSQL" skill
mention scored **85** (STRONG) while an otherwise-identical resume that
*additionally* had a strong, metric-bearing experience bullet
("Optimized PostgreSQL queries and reduced latency by 35% through
indexing.") scored only **64** (PARTIAL) — richer evidence produced a
*worse* score.

**Root cause** (`app/modules/evidence/service.py`,
`EvidenceService.retrieve_requirement_evidence`): the requirement's
overall `match_result` classification was derived from
`ranked[0].strength` — the raw-relevance `EvidenceStrength` of whichever
evidence item ranked **first** *after* Phase 6's context-aware
reranking (`rank_by_evidence_hierarchy`, weighted 65% relevance / 35%
context strength). That reranking correctly promotes an experience
bullet ahead of a bare skills mention for *display* purposes (richer
context should be shown first) — but the promoted bullet's own raw
relevance (0.81) was lower than the skill mention's raw relevance
(0.88), and using only the promoted item's `EvidenceStrength` for the
classification silently discarded the fact that a *different* candidate
in the same ranked list had stronger raw evidence. `aggregated_evidence_strength`
(which does correctly combine both items) was 1.0 in this case — proof
the underlying evidence was assessed correctly; only the single-item
`match_result` derivation was wrong.

**Fix applied**: `match_result_status` is now derived from the
**strongest** `EvidenceStrength` among *all* ranked evidence items (a
new `_strongest()` helper, `max()` by strength rank), not specifically
`ranked[0]`. This preserves `ranked[0]`'s role in presentation/ordering
and `aggregate_evidence_strength()`'s role in the continuous score blend
— only the discrete classification's source changed.

**Verification**: fixed the monotonicity test — before the fix, v2
(bare skill mention) scored 85 while v3 (skill mention + strong bullet)
scored 64; after the fix both score 85, with v3's underlying
pre-rounding score (0.8538) now correctly at or above v2's (0.8529)
rather than below it. Also
independently fixed `CASE_A1_EXACT_PYTHON` in the dataset (same
underlying pattern — went from an incorrect PARTIAL to the correct
STRONG) without any dataset change. **Full backend suite: 457/457
passed after the fix — zero regressions** in any of Phases 5-12's 435
pre-existing tests.

This is exactly the category of "concrete issue identified by
evaluation" spec §44 permits fixing, with the evidence, cause, and fix
fully documented per §36's required format.

## 10. Determinism

`tests/evaluation/test_determinism.py` runs the full `AnalysisService`
pipeline 3× on the same input and asserts identical ATS score, Resume
Quality score, gap/strength/recommendation counts, and the full
per-requirement status list. All identical — the pipeline is
deterministic end to end, including embedding-based semantic matching
(the embedding cache and TF-IDF refitting are both pure functions of
their input).

## 11. Performance Baseline

| Stage | Mean | Max | Samples |
|---|---|---|---|
| Resume parsing | 3.9 ms | 6.5 ms | 15 |
| JD parsing | 0.14 ms | 0.24 ms | 15 |
| Full scoring (matching + evidence + ATS) | 908 ms | 13,196 ms | 15 |

The 13.2s maximum is the **first** call in the process, which lazily
loads the `sentence-transformers/all-MiniLM-L6-v2` embedding model
(one-time cold start, cached for the rest of the process's lifetime via
`get_embedding_service()`'s `@lru_cache` singleton). Excluding that one
outlier, per-case scoring is well under 1 second. This is a baseline
only — no optimization was performed (spec §33).

## 12. Resource Observations

Not independently profiled beyond the timing above (spec §34 permits
reporting this as a limitation rather than building new instrumentation
this phase). Qualitatively: the embedding cache (`_embedding_cache` dict
in `LocalSentenceTransformerEmbeddingService`) is unbounded — fine at
this dataset's scale (15 cases, a few dozen unique text spans), but
would need an eviction policy before this pipeline processes a
large/production-scale evaluation set.

## 13. Golden Test Cases (`tests/evaluation/test_golden_cases.py`)

8 permanent regression fixtures, one per required category (strong
match, weak match, missing requirement, partial match, semantic
evidence match, false semantic match, keyword stuffing, critical
requirement). All 8 pass against the current pipeline.

## 14. Regression Tests

Every behavior spec §24 explicitly calls out already has a dedicated,
passing test: PostgreSQL alias (`CASE_B1` + `test_golden_cases`),
Java vs JavaScript / Docker vs Kubernetes / AWS vs Azure / React vs
React Native (`test_dataset_evaluation.py`'s
`test_distinct_technology_cases_never_produce_a_strong_match`, and
individually in the dataset), keyword stuffing
(`test_adversarial.py`), critical requirement (`CASE_I1` +
`test_requirement_scoring.py` from Phase 7), UNKNOWN handling
(`test_dataset_evaluation.py`'s
`test_unknown_and_missing_remain_distinguishable`), evidence strength
(`test_evidence_integration.py` from Phase 6), score bounds (Phase 7's
`test_ats_engine.py`).

## 15. Configuration Change Log

No `ScoringConfig` values were changed this phase — `SCORING_CONFIG_V1`
is unchanged. Two calibration proposals are recorded in §5 for future
evaluation cycles, not applied now (insufficient evidence at n=1 per
finding, per spec §26's "do not blindly change weights").

One **code** change was made (§9) — a classification-logic bug fix, not
a configuration/weight change — bumping no config version, since it
corrects behavior the configuration values were never responsible for.

## 16. Frontend Evaluation Page

**Not implemented this phase.** Per spec §41's explicit permission
("If implementing it adds unnecessary complexity, prioritize the
evaluation backend/reporting first"), this phase prioritized the
evaluation framework, the real bug it found and fixed, and this report.
An admin-only evaluation dashboard is a reasonable Phase 14 candidate if
still wanted, now that `run_evaluation()` produces a structured
`EvaluationReport` a future endpoint could serve directly.

## 17. Known Limitations

- **Dataset size (15 cases)** is small; precision/recall/F1 here
  describe this benchmark only, not general system accuracy. Two of the
  two remaining false-negative findings above are single-case
  observations, not statistically grounded proposals.
- Two evaluation-dataset resume fixtures initially tripped the
  already-known "bare single Title-Case word in a SKILLS section
  misread as a heading" parser edge case (documented in Phases 7-8); all
  dataset fixtures now use realistic multi-item skills lists to avoid
  it, consistent with the same workaround applied in every prior phase.
- No real-world/human-labeled data was used or is claimed to have been
  used anywhere in this evaluation.
