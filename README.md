# Resumind

Resumind is an ATS (Applicant Tracking System) alignment tool: it parses
a resume and a job description, then produces a deterministic,
explainable score describing how well the resume's demonstrated
evidence matches the job's stated requirements — plus a separate score
for the resume's own structural/ATS-readability quality, and an optional
third score for how well the resume fits a general career target
(Position + Domain) even without a specific job posting.

## 1. Core problem

Resumes get filtered by ATS software before a human ever reads them, but
candidates rarely get to see *why* their resume was or wasn't a good
match. Resumind makes that process transparent: every score traces back
to specific, inspectable evidence, not an opaque black box.

## 2. Key features

- **ATS Alignment** — deterministic 0-100 score for a specific resume + job description pair
- **Resume Quality** — a separate, JD-independent score for parseability, structure, evidence quality, and ATS-readability
- **Target Fit** — Position + Domain alignment when no specific job description exists yet
- **Evidence Explorer** — every match is traceable to the actual resume text that produced it
- **Deterministic recommendations** — traceable, template-based, never fabricated ("if you genuinely have this experience...")
- **No LLM in the scoring path** — every score is reproducible and explainable

## 3. Architecture

```
Resume + JD/Target Profile
        │
        ▼
 Resume/JD Intelligence (parsing)
        │
        ▼
   Normalization (canonical entities)
        │
        ▼
   Hybrid Matching (exact/canonical/keyword/TF-IDF/semantic/context)
        │
        ▼
   Evidence Engine (ranking, deduplication, aggregation)
        │
        ├──► ATS Scoring        (Resume + JD)
        ├──► Resume Quality     (Resume alone)
        └──► Target Fit         (Resume + Position/Domain)
        │
        ▼
   Analysis Engine (strengths, gaps, recommendations)
        │
        ▼
   Product Dashboard (React frontend)
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full
module-by-module breakdown and [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md)
for the frontend's design tokens and component library.

## 4. ATS methodology

The ATS Alignment score is a **deterministic, rule-based calculation** —
not a single AI-generated number. It combines several classical NLP
techniques (see §7 below), fuses them into a per-requirement match
strength (MISSING/WEAK/PARTIAL/STRONG/VERY_STRONG/UNKNOWN), then
aggregates those into weighted category scores and a final 0-100 score.
The same input always produces the same output.

## 5. Deterministic scoring

Every weight and threshold used in scoring lives in one place:
`Backend/fastapi_app/app/modules/scoring/config.py` (and the analogous
config modules for Resume Quality and Target Profile). Nothing in the
scoring path calls an LLM or any non-deterministic service.

## 6. Hybrid matching

A requirement/evidence pair is scored by combining six independent
signals: exact string match, canonical-entity match (e.g. "Postgres" ↔
"PostgreSQL", resolved via a curated alias registry — never substring
guessing), keyword overlap, TF-IDF cosine similarity, semantic embedding
similarity, and evidence-context strength (an experience bullet counts
for more than a bare skills-list mention). Distinct technologies (e.g.
Docker vs. Kubernetes, Java vs. JavaScript) are explicitly guarded
against being conflated even when semantically related.

## 7. Evidence engine

Evidence isn't just "found/not found" — every match is backed by the
actual resume text, ranked by a composite of relevance and context
strength, deduplicated (so a duplicated bullet doesn't inflate a score),
and aggregated with diminishing returns (three identical mentions do not
count as 3× the evidence of one).

## 8. Resume Quality

Nine independently-measured dimensions (parseability, structure, content
completeness, evidence quality, date consistency, contact completeness,
keyword hygiene, section consistency, content density) combine into one
score — completely independent of any job description. The same resume
produces the same Resume Quality score regardless of which job it's
being compared against.

## 9. Target Profiles

For a Position + Domain (e.g. "Backend Engineer" + "FinTech") without a
specific job posting, Resumind uses a curated, versioned knowledge base
(never an LLM-invented profile) to build a Target Fit score, split into
Position Fit and Domain Fit so the two can be inspected independently.

## 10. Technology stack

**Backend (ATS pipeline):** Python, FastAPI, Pydantic, PyMuPDF (PDF
parsing), python-docx, scikit-learn (TF-IDF), sentence-transformers
(embeddings), SQLAlchemy (schema only — see §17 on database status).

**Backend (auth/legacy):** Node.js, Express, Prisma.

**Frontend:** React 19, Vite, Tailwind CSS v4, React Router, lucide-react.

**Database:** PostgreSQL (Neon) — schema defined via Prisma migrations
and mirrored SQLAlchemy models; **not reachable in this development
environment** (see Known Limitations).

## 11. How to run locally

**Backend (FastAPI — the ATS pipeline):**
```bash
cd Backend/fastapi_app
pip install -r requirements.txt   # if present, else see pyproject/venv setup
uvicorn main:app --reload --port 8000
```

**Backend (Node/Express — auth, legacy routes):**
```bash
cd Backend
npm install
npm start
```

**Frontend:**
```bash
cd Frontend
npm install
npm run dev
```

The frontend expects the FastAPI backend at `http://127.0.0.1:8000` by
default (override with `VITE_API_BASE_URL`).

## 12. Environment variables

See [`Backend/.env.example`](Backend/.env.example) for the full list
with placeholder values. Copy it to `Backend/.env` and fill in real
values — never commit `.env`.

## 13. API overview

All ATS-pipeline endpoints are served by FastAPI and documented via its
auto-generated OpenAPI schema (`/docs` when the server is running). Key
routes:

| Route | Purpose |
|---|---|
| `POST /resumes/parse` | Parse a resume into structured data |
| `POST /jobs/parse` | Parse a job description (file or pasted text) |
| `POST /resume-quality` | Resume Quality analysis (no JD needed) |
| `GET /target-profiles/positions` / `/domains` | List the curated registry |
| `POST /target-profiles/preview` | Build an effective Position+Domain profile |
| `POST /target-profiles/analyze` | Target Fit analysis |
| `POST /analysis` | Full analysis (JD, Target Profile, or combined mode) |

Every endpoint is currently **stateless** — see §17.

## 14. Testing

```bash
cd Backend/fastapi_app
pytest -q
```

457 tests as of Phase 13/14 (unit, integration, and evaluation), all
passing. See §16 below for the evaluation-specific suite.

## 15. Evaluation

A dedicated evaluation framework (`app/modules/evaluation/`) runs a
15-case labeled benchmark through the real pipeline and reports
precision/recall/F1, error analysis, adversarial-resistance tests
(keyword stuffing, duplicate content), monotonicity, and determinism.
Full results: [`docs/EVALUATION_REPORT.md`](docs/EVALUATION_REPORT.md).
This is a controlled internal benchmark — not a claim of real-world or
hiring-outcome validation.

## 16. Limitations

- **No database persistence is active in this environment.** The Neon
  Postgres instance referenced in configuration is unreachable from this
  sandbox (connection attempts time out). Every API endpoint is a
  stateless compute-only request: nothing is saved, and there is no
  resume/JD/analysis history, no target-profile save, and no per-user
  data isolation enforced at the database level. The SQLAlchemy schema
  and Prisma migrations exist and are ready to wire up once a reachable
  database is configured.
- **Authentication is not a real security boundary right now.**
  `Backend/Models/db.js` and `Backend/Models/user.js` (the Node auth
  backend's data layer) are absent from the working tree, so
  register/login cannot actually issue verified sessions in this
  environment. The frontend's route guard is a UX convenience only.
- The legacy Gemini-based `/analyze` endpoint (`Backend/fastapi_app/main.py`)
  remains in the codebase, fully isolated from the deterministic ATS
  pipeline (zero imports from `app/` into the Gemini modules). It is not
  part of, and does not influence, any ATS/Quality/Target Fit score.
- The curated Target Profile registry covers 12 positions × 6 domains —
  real-world coverage will need to grow over time.
- Evaluation metrics (§15) describe a 15-case controlled benchmark only,
  not statistically validated real-world accuracy.
