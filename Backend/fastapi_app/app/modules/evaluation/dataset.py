"""Versioned evaluation dataset (spec Phase 13 §3-5). A controlled
internal benchmark — NOT a claim of real-world/hiring validation (spec
§4). Every case is a real resume/JD text pair run through the actual
Phase 2-7 pipeline; nothing here is a mock of pipeline output.
"""

from app.modules.evaluation.schemas import EvaluationCase, ExpectedOutcome

DATASET_VERSION = "EVAL_DATASET_V1"

CASES: list[EvaluationCase] = [
    # --- A. Exact match ---
    EvaluationCase(
        case_id="CASE_A1_EXACT_PYTHON",
        category="EXACT_MATCH",
        description="Exact skill name appears in both Skills and a strong experience bullet.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
            "- Built REST APIs using Python and FastAPI, serving 50K daily users.\n\nSKILLS\nPython, FastAPI\n"
        ),
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n",
        expected=ExpectedOutcome(matches=["Experience with Python."]),
    ),
    # --- B. Canonical match (alias, not substring) ---
    EvaluationCase(
        case_id="CASE_B1_CANONICAL_POSTGRES_ALIAS",
        category="CANONICAL_MATCH",
        description="Resume uses the 'Postgres' alias; JD requires 'PostgreSQL'. Must resolve via Phase 4 normalization, not substring matching.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Intern, Acme | Jun 2023 - Aug 2023\n"
            "- Optimized Postgres queries and reduced latency by 35%.\n\nSKILLS\nPostgres, Python\n"
        ),
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with PostgreSQL.\n",
        expected=ExpectedOutcome(matches=["Experience with PostgreSQL."]),
    ),
    # --- C. Semantic match (paraphrased responsibility with real evidence) ---
    EvaluationCase(
        case_id="CASE_C1_SEMANTIC_DB_OPTIMIZATION",
        category="SEMANTIC_MATCH",
        description="JD responsibility text is paraphrased; resume shows concrete matching evidence.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2021 - Jan 2024\n"
            "- Optimized PostgreSQL queries and reduced latency by 35% through indexing.\n\nSKILLS\nPostgreSQL\n"
        ),
        job_description_text="Backend Engineer\n\nRESPONSIBILITIES\n- Optimize database performance.\n",
        expected=ExpectedOutcome(partial=["Optimize database performance."]),
    ),
    # --- D. False semantic match (distinct technology guardrail) ---
    EvaluationCase(
        case_id="CASE_D1_DISTINCT_KUBERNETES_DOCKER",
        category="DISTINCT_TECHNOLOGY",
        description="Resume mentions Docker only; JD requires Kubernetes — must NOT be a strong match.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Intern, Acme | Jun 2023 - Aug 2023\n"
            "- Deployed services using Docker.\n\nSKILLS\nDocker\n"
        ),
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n",
        expected=ExpectedOutcome(missing=["Experience with Kubernetes."]),
    ),
    EvaluationCase(
        case_id="CASE_D2_DISTINCT_AWS_AZURE",
        category="DISTINCT_TECHNOLOGY",
        description="Resume mentions Azure only; JD requires AWS — must NOT be a strong match.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEXPERIENCE\nCloud Engineer, Acme | Jan 2022 - Jan 2024\n"
            "- Deployed services on Azure using Azure Functions.\n\nSKILLS\nAzure\n"
        ),
        job_description_text="Cloud Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with AWS.\n",
        expected=ExpectedOutcome(missing=["Experience with AWS."]),
    ),
    EvaluationCase(
        case_id="CASE_D3_DISTINCT_JAVA_JAVASCRIPT",
        category="DISTINCT_TECHNOLOGY",
        description="Resume mentions JavaScript only; JD requires Java — must NOT be a strong match.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEXPERIENCE\nFrontend Engineer, Acme | Jan 2022 - Jan 2024\n"
            "- Built web interfaces using JavaScript and React.\n\nSKILLS\nJavaScript, React\n"
        ),
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Java.\n",
        expected=ExpectedOutcome(missing=["Experience with Java."]),
    ),
    EvaluationCase(
        case_id="CASE_D4_DISTINCT_REACT_REACT_NATIVE",
        category="DISTINCT_TECHNOLOGY",
        description="Resume mentions React Native only; JD requires React (web) — not automatically equivalent.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEXPERIENCE\nMobile Engineer, Acme | Jan 2022 - Jan 2024\n"
            "- Built mobile apps using React Native.\n\nSKILLS\nReact Native\n"
        ),
        job_description_text="Frontend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with React.\n",
        expected=ExpectedOutcome(missing=["Experience with React."]),
    ),
    # --- E. Missing skill ---
    EvaluationCase(
        case_id="CASE_E1_MISSING_NO_MENTION",
        category="MISSING_SKILL",
        description="Skill never mentioned anywhere in the resume.",
        resume_text="Jane Doe\njane@example.com\n\nSKILLS\nMarketing, Sales\n",
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n",
        expected=ExpectedOutcome(missing=["Experience with Kubernetes."]),
    ),
    # --- F. Partial requirement ---
    EvaluationCase(
        case_id="CASE_F1_PARTIAL_SKILL_MENTION",
        category="PARTIAL_REQUIREMENT",
        description="Skill appears in Skills section without dedicated experience evidence.",
        resume_text="Jane Doe\njane@example.com\n\nEXPERIENCE\nAnalyst, Acme | Jan 2022 - Jan 2024\n- Analyzed sales data.\n\nSKILLS\nPython, SQL\n",
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Python.\n",
        expected=ExpectedOutcome(partial=["Experience with Python."]),
    ),
    # --- I. Critical requirement ---
    EvaluationCase(
        case_id="CASE_I1_CRITICAL_MISSING",
        category="CRITICAL_REQUIREMENT",
        description="A critical requirement is missing entirely.",
        resume_text="Jane Doe\njane@example.com\n\nSKILLS\nPython, Django\n",
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Experience with Kubernetes.\n",
        expected=ExpectedOutcome(missing=["Experience with Kubernetes."], critical_gaps=["Experience with Kubernetes."]),
    ),
    # --- J. Experience requirements ---
    EvaluationCase(
        case_id="CASE_J1_EXPERIENCE_UNKNOWN_NO_DATES",
        category="EXPERIENCE_REQUIREMENT",
        description="No experience/date information at all -> UNKNOWN, not MISSING.",
        resume_text="Jane Doe\njane@example.com\n\nSKILLS\nPython, Django\n",
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- 3+ years of experience with Python.\n",
        expected=ExpectedOutcome(unknown=["3+ years of experience with Python."]),
    ),
    EvaluationCase(
        case_id="CASE_J2_EXPERIENCE_VERY_STRONG",
        category="EXPERIENCE_REQUIREMENT",
        description="Resume shows 3+ years of clearly dated, relevant experience.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEXPERIENCE\nBackend Engineer, Acme | Jan 2020 - Jan 2024\n"
            "- Built backend systems using Python.\n\nSKILLS\nPython\n"
        ),
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- 3+ years of experience with Python.\n",
        expected=ExpectedOutcome(matches=["3+ years of experience with Python."]),
    ),
    # --- K. Qualification requirements ---
    EvaluationCase(
        case_id="CASE_K1_QUALIFICATION_MATCHING_DEGREE",
        category="QUALIFICATION_REQUIREMENT",
        description="Resume degree/field matches the required qualification.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEDUCATION\nB.Tech in Computer Science, XYZ University | 2017 - 2021\n\nSKILLS\nPython\n"
        ),
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Bachelor's degree in Computer Science.\n",
        expected=ExpectedOutcome(matches=["Bachelor's degree in Computer Science."]),
    ),
    EvaluationCase(
        case_id="CASE_K2_QUALIFICATION_UNRELATED_DEGREE",
        category="QUALIFICATION_REQUIREMENT",
        description="Resume degree/field is unrelated to the required qualification.",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEDUCATION\nB.Tech in Biotechnology, XYZ University | 2017 - 2021\n\nSKILLS\nPython\n"
        ),
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- Bachelor's degree in Computer Science.\n",
        expected=ExpectedOutcome(missing=["Bachelor's degree in Computer Science."]),
    ),
    # --- N. Keyword stuffing (handled separately as a behavioral test, see tests/evaluation) ---
    # --- Q. Unknown evidence ---
    EvaluationCase(
        case_id="CASE_Q1_CONFIDENT_ABSENCE_VS_UNKNOWN",
        category="UNKNOWN_EVIDENCE",
        description="Resume has dated experience but in an unrelated field -> confidently MISSING, contrasted with CASE_J1 (no experience info at all -> UNKNOWN).",
        resume_text=(
            "Jane Doe\njane@example.com\n\nEXPERIENCE\nMarketing Analyst, Acme | Jan 2020 - Jan 2024\n"
            "- Ran marketing campaigns.\n\nSKILLS\nExcel\n"
        ),
        job_description_text="Backend Engineer\n\nREQUIRED QUALIFICATIONS\n- 2+ years of experience with Python.\n",
        expected=ExpectedOutcome(missing=["2+ years of experience with Python."]),
    ),
]
