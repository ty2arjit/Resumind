"""Resume Quality service (spec §31). Independent of any JD — analyzes a
resume's intrinsic quality/machine-readability only (spec §1, §38)."""

from app.modules.resume.schemas import StructuredResume
from app.modules.resume_quality.config import ALGORITHM_VERSION, ResumeQualityConfig, get_resume_quality_config
from app.modules.resume_quality.contact_completeness import score_contact_completeness
from app.modules.resume_quality.content_completeness import score_content_completeness
from app.modules.resume_quality.content_density import score_content_density
from app.modules.resume_quality.date_consistency import score_date_consistency
from app.modules.resume_quality.evidence_quality import score_evidence_quality
from app.modules.resume_quality.keyword_hygiene import score_keyword_hygiene
from app.modules.resume_quality.parseability import score_parseability
from app.modules.resume_quality.schemas import QualityDimensionScores, QualityFinding, ResumeQualityResult
from app.modules.resume_quality.section_consistency import score_section_consistency
from app.modules.resume_quality.structure import score_structure


class ResumeQualityService:
    def __init__(self, config: ResumeQualityConfig | None = None):
        self._config = config or get_resume_quality_config()

    def calculate_dimension_scores(
        self, resume: StructuredResume
    ) -> tuple[QualityDimensionScores, list[QualityFinding]]:
        config = self._config
        findings: list[QualityFinding] = []

        parseability, f = score_parseability(resume, config.parseability)
        findings += f
        structure, f = score_structure(resume, config.structure)
        findings += f
        content_completeness, f = score_content_completeness(resume, config.content_completeness)
        findings += f
        evidence_quality, f = score_evidence_quality(resume, config.evidence_quality)
        findings += f
        date_consistency, f = score_date_consistency(resume, config.date_consistency)
        findings += f
        contact_completeness, f = score_contact_completeness(resume, config.contact_completeness)
        findings += f
        keyword_hygiene, f = score_keyword_hygiene(resume, config.keyword_hygiene)
        findings += f
        section_consistency, f = score_section_consistency(resume, config.section_consistency)
        findings += f
        content_density, f = score_content_density(resume, config.content_density)
        findings += f

        dimension_scores = QualityDimensionScores(
            parseability=parseability,
            structure=structure,
            content_completeness=content_completeness,
            evidence_quality=evidence_quality,
            date_consistency=date_consistency,
            contact_completeness=contact_completeness,
            keyword_hygiene=keyword_hygiene,
            section_consistency=section_consistency,
            content_density=content_density,
        )
        return dimension_scores, findings

    def calculate_quality_score(self, dimension_scores: QualityDimensionScores) -> int:
        weights = self._config.dimension_weights
        total = (
            dimension_scores.parseability * weights.parseability
            + dimension_scores.structure * weights.structure
            + dimension_scores.content_completeness * weights.content_completeness
            + dimension_scores.evidence_quality * weights.evidence_quality
            + dimension_scores.date_consistency * weights.date_consistency
            + dimension_scores.contact_completeness * weights.contact_completeness
            + dimension_scores.keyword_hygiene * weights.keyword_hygiene
            + dimension_scores.section_consistency * weights.section_consistency
            + dimension_scores.content_density * weights.content_density
        )
        return max(0, min(100, round(total * 100)))

    def generate_quality_findings(self, resume: StructuredResume) -> list[QualityFinding]:
        _, findings = self.calculate_dimension_scores(resume)
        return findings

    def analyze(self, resume: StructuredResume) -> ResumeQualityResult:
        dimension_scores, findings = self.calculate_dimension_scores(resume)
        return ResumeQualityResult(
            resume_quality=self.calculate_quality_score(dimension_scores),
            dimension_scores=dimension_scores,
            findings=findings,
            resume_quality_algorithm_version=ALGORITHM_VERSION,
            resume_quality_config_version=self._config.version,
        )
