# Resumind Architecture (Phase 14)

## 1. High-level data flow

```
                    USER
                     │
                     ▼
              RESUMIND FRONTEND (React/Vite, Frontend/)
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      Resume Upload         JD text/file, or
      (PDF/DOCX)             Position+Domain
          │                     │
          └──────────┬──────────┘
                     ▼
     FastAPI (Backend/fastapi_app/) — stateless HTTP layer
                     │
        ┌────────────┼────────────────────┐
        ▼            ▼                    ▼
  Resume Intel.   JD Intelligence   Target Profile Registry
  (Phase 2)       (Phase 3)         (Phase 9, curated JSON)
        │            │                    │
        └─────┬──────┘                    │
              ▼                           │
       Normalization (Phase 4)            │
              ▼                           │
       Hybrid Matching (Phase 5)  ◄───────┘ (target reqs feed the same matcher)
              ▼
       Evidence Engine (Phase 6)
              │
   ┌──────────┼──────────────┐
   ▼          ▼              ▼
ATS Scoring  Resume Quality  Target Fit
(Phase 7)    (Phase 8)       (Phase 9)
   │          │              │
   └──────────┼──────────────┘
              ▼
       Analysis Engine (Phase 10)
   (strengths / gaps / recommendations)
              ▼
          API Response
              ▼
       RESUMIND UI (Phase 11 design system, Phase 12 dashboard)
```

This is the architecture the codebase actually implements — every arrow
above corresponds to a real function call, not an aspirational diagram.
`AnalysisService` (Phase 10) is the only module that calls into
`ScoringService`, `ResumeQualityService`, and `TargetProfileService`
together; none of those three call each other, preserving the
"ATS Alignment / Resume Quality / Target Fit stay separate" rule
enforced throughout Phases 7-10.

## 2. Backend components

| Module | Path | Source of truth for |
|---|---|---|
| Resume Intelligence | `app/modules/resume/` | Parsed resume structure |
| JD Intelligence | `app/modules/job/` | Parsed JD structure |
| Normalization | `app/modules/normalization/` | Canonical entity equivalence |
| Embeddings | `app/modules/embeddings/` | Semantic similarity (see §4) |
| Matching | `app/modules/matching/` | Requirement ↔ evidence match strength |
| Evidence | `app/modules/evidence/` | Evidence retrieval/ranking/aggregation |
| Scoring | `app/modules/scoring/` | ATS Alignment |
| Resume Quality | `app/modules/resume_quality/` | Resume Quality score |
| Target Profile | `app/modules/target_profile/` | Target Fit / Position Fit / Domain Fit |
| Analysis | `app/modules/analysis/` | Strengths, gaps, recommendations |
| Evaluation | `app/modules/evaluation/` | Benchmark/regression measurement (read-only, no production side effects) |

Each module owns exactly one config file (e.g.
`scoring/config.py`, `resume_quality/config.py`,
`target_profile/config.py`, `analysis/config.py`) — no weight or
threshold is duplicated across modules. `RequirementScoreResult` (Phase
7's schema) is reused verbatim by both `ScoringService` and
`TargetProfileService` rather than each defining its own requirement
result shape.

## 3. Frontend components

`Frontend/src/components/design-system/` (Phase 11) is the single
component library — `Frontend/src/Pages/app/*Page.jsx` (Phase 12)
consume it and never redefine colors/spacing/typography inline. The
frontend performs **zero score calculation** — `AnalysisResultPage.jsx`
only formats and displays fields already present in the `/analysis`
response (`app/lib/api.js` is the only place that talks to the backend).

## 4. Embedding model

- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (pretrained, not
  fine-tuned or trained from scratch — an explicit, preserved
  architectural decision).
- **Dimension:** 384.
- **Similarity metric:** cosine similarity.
- **Where generated:** `app/modules/embeddings/local_model.py`
  (`LocalSentenceTransformerEmbeddingService`), used exclusively via
  `app/modules/matching/semantic.py`'s `SemanticMatcher`.
- **Caching:** an in-process `_embedding_cache` dict keyed by
  `hash(text + model_version)`, so re-embedding identical text within
  one process is free. The model itself loads lazily on first use and
  is held by a `functools.lru_cache`-backed singleton
  (`get_embedding_service()`), so it's loaded once per process, not per
  request.
- **Fallback behavior:** none — if the model can't load, the call fails
  loudly rather than silently degrading to a fabricated similarity
  score.
- **Version tracking:** `EmbeddingService.model_version` is threaded
  through to every `ScoreBreakdown`/`TargetAnalysisResult`, so a stored
  analysis remains interpretable if the model is later upgraded.

## 5. LLM audit

**No LLM is used anywhere in the deterministic ATS pipeline** (Phases
2-10, 13). Verified by direct code search: zero imports of
`google.generativeai`, `openai`, `anthropic`, or any other LLM client
inside `app/` (the FastAPI ATS package). The only LLM-touching code in
the repository is the **legacy Gemini path** — see §6.

## 6. Legacy Gemini path

`Backend/fastapi_app/Internship/*.py` and `Backend/fastapi_app/Placement/*.py`
(32 files) call the Gemini API directly and are wired into a single
legacy endpoint, `POST /analyze` in `Backend/fastapi_app/main.py`. This
predates the deterministic ATS pipeline (Phases 1-13) and was left in
place per the Phase 1 architecture decision documented inline in
`main.py`: *"development fallback only — not part of the new ATS
pipeline."*

**Isolation verified this phase:** `grep -rln "from Internship\|from
Placement" app/` returns zero matches — no module under `app/` (the
real ATS pipeline) imports from these legacy directories. The legacy
`/analyze` route and the Phase 2-13 routes (`/resumes/parse`,
`/jobs/parse`, `/resume-quality`, `/target-profiles/*`, `/analysis`) are
entirely independent code paths sharing only the FastAPI app instance.
**No ATS/Resume Quality/Target Fit score depends on Gemini in any way.**

Decision: **kept, clearly isolated, not removed** — removing 32 working
files outside this phase's stated scope risks losing functionality the
product may still want, and spec §41 explicitly permits isolation as an
alternative to removal.

## 7. Database

PostgreSQL (Neon), with Prisma (`Backend/prisma/schema.prisma`) as the
migration authority and mirrored SQLAlchemy models
(`Backend/fastapi_app/app/models/`) for the FastAPI side to query the
same tables. **The database is unreachable from this development
environment** — a direct `asyncpg` connection attempt times out (tested
in Phases 9, 10, 14). Every Phase 2-13 API endpoint is therefore
stateless: it computes and returns a result without writing to any
table, and the frontend holds only in-memory session state
(`Frontend/src/lib/AppDataContext.jsx`) rather than fetching persisted
history. The schema itself (`app/models/*.py`) is complete and ready —
`Resume`, `ResumeVersion`, `JobDescription`, `TargetProfile`,
`Analysis`, `RequirementMatch`, `ScoreBreakdown`, `Recommendation`,
`EvaluationCase`/`EvaluationResult` all exist with foreign keys and
cascade rules already defined, pending a reachable database.

## 8. Authentication

`Backend/Controller/authController.js` implements register/login against
a Prisma `User` model, but `Backend/Models/db.js` and
`Backend/Models/user.js` are absent from the working tree (a pre-existing
gap, not introduced by any phase in this session — confirmed via `git
log`). The Node auth backend cannot currently issue or verify real
sessions in this environment. The frontend's `RequireAuth` component
(Phase 12) checks a client-side flag plus a stored JWT for reload
survival, but this is explicitly a UX convenience, not the real security
boundary — see this session's Phase 14 final report for the full
security-audit account.

## 9. Determinism guarantee

Every score-producing path (`ScoringService`, `ResumeQualityService`,
`TargetProfileService`, `AnalysisService`) is a pure function of its
inputs plus versioned configuration — no randomness, no wall-clock
dependence, no external non-deterministic API call. Verified by
`tests/evaluation/test_determinism.py` (3 repeated runs, identical
output down to the per-requirement status list) and equivalent
determinism tests in every phase's own test suite (Phases 5-10).
