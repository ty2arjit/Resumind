import { useNavigate } from 'react-router-dom';
import {
  Button,
  EmptyState,
  EvidenceCard,
  InsightCard,
  RecommendationCard,
  RequirementCard,
  ScoreBreakdownRow,
  ScoreHero,
} from '../../Components/design-system';
import { getScoreState } from '../../Components/design-system/score/scoreStates';
import { useAppData } from '../../lib/AppDataContext';

const PRIORITY_ORDER = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

// Frontend presentation text for Phase 8 finding codes (spec Phase 12
// §12: never expose internal message keys directly).
const QUALITY_FINDING_LABELS = {
  NO_STRUCTURED_EVIDENCE: 'No structured evidence bullets detected',
  FEW_MEASURABLE_RESULTS: 'Few bullets include measurable outcomes',
  FEW_ACTION_VERBS: 'Few bullets begin with a clear action verb',
  UNPARSEABLE_DATE: 'A date could not be reliably read',
  INVALID_DATE_ORDER: 'A date range appears out of order',
  MISSING_CORE_CONTACT_INFO: 'Core contact information is incomplete',
  EXCESSIVE_REPEATED_CONTENT: 'Some content appears to be repeated',
  NO_EXPERIENCE_OR_PROJECTS: 'No experience or projects section detected',
  FEW_SECTIONS_DETECTED: 'Few resume sections were detected',
  NO_BULLET_CONTENT: 'No bullet content detected',
  BULLETS_TOO_SHORT: 'Several bullets are very short',
  BULLETS_TOO_LONG: 'Several bullets are very long',
  SPARSE_CONTENT: 'Resume content is sparse for its length',
  LOW_EXTRACTED_TEXT: 'Very little text could be extracted',
  POSSIBLE_SCANNED_PDF: 'This may be a scanned (image) PDF',
  EMPTY_DOCUMENT: 'The document appears to be empty',
  AMBIGUOUS_SECTION: 'A section heading was ambiguous',
  MALFORMED_DATE: 'A date could not be parsed',
  UNSUPPORTED_LAYOUT: 'The document layout may affect parsing',
  DUPLICATE_CONTENT_REMOVED: 'Duplicate content was found and removed',
  MISSING_EXPECTED_SECTION: 'An expected resume section was not found',
  AMBIGUOUS_EXPERIENCE_HEADER: 'An experience entry header was ambiguous',
  AMBIGUOUS_EDUCATION_ENTRY: 'An education entry was ambiguous',
  MULTIPLE_SECTIONS_MERGED: 'Two sections may have been merged during parsing',
};

function humanizeCode(code) {
  return QUALITY_FINDING_LABELS[code] ?? code.replace(/_/g, ' ').toLowerCase();
}

const SCORE_STATUS_SENTENCE = {
  'Very Strong': 'Your resume demonstrates very strong alignment with the requirements of this role.',
  Strong: 'Your resume demonstrates strong alignment with the requirements of this role.',
  Partial: 'Your resume shows partial alignment — several requirements need stronger evidence.',
  Weak: 'Your resume shows weak alignment with the requirements of this role.',
  Low: 'Your resume currently shows low alignment with the requirements of this role.',
};

const INSIGHT_TITLES = {
  STRONG_REQUIREMENT: 'Strong requirement match',
  STRONG_CATEGORY_COVERAGE: 'Strong category coverage',
  STRONG_POSITION_FIT: 'Strong position alignment',
  STRONG_DOMAIN_FIT: 'Strong domain evidence',
  HIGH_QUALITY_DIMENSION: 'Resume quality strength',
};

/**
 * Analysis result — Resumind's most important screen (frontendReadme
 * §16-27). Structure: job context → primary score → score breakdown →
 * strengths → priority gaps → requirement coverage → evidence →
 * recommendations. Renders the real Analysis object from /analysis,
 * including the additive `categories`/`requirements`/`evidence_text`
 * pass-through fields (documented in this session's final reports) —
 * nothing here is computed on the frontend.
 */
export default function AnalysisResultPage() {
  const navigate = useNavigate();
  const { lastAnalysis, activeResume } = useAppData();

  if (!lastAnalysis) {
    return (
      <EmptyState
        title="No analysis to show"
        description="Run an analysis first to see your results here."
        action={<Button onClick={() => navigate('/analyses/new')}>Start Analysis</Button>}
      />
    );
  }

  const { context, scores, summary, strengths, gaps, recommendations, categories, requirements } = lastAnalysis;
  const primaryScoreState = getScoreState(summary.primary_score);
  const gapsByPriority = PRIORITY_ORDER.map((priority) => ({ priority, items: gaps.filter((g) => g.priority === priority) })).filter(
    (group) => group.items.length > 0
  );
  // Only show evidence for requirements that actually matched — the
  // matcher's "top candidate" for a MISSING requirement is just the
  // least-unrelated resume text, not real supporting evidence, so
  // surfacing it here would read as a contradiction next to the
  // "no reliable evidence found" gap message above.
  const evidenceRequirements = (requirements ?? []).filter(
    (r) => r.evidence_text && !['MISSING', 'UNKNOWN'].includes(r.status)
  );

  return (
    <div className="max-w-3xl space-y-10">
      {/* Job context */}
      <header className="flex flex-wrap items-center gap-x-4 gap-y-1.5 border-b border-border-subtle pb-5">
        {context.target_profile_position && (
          <h1 className="text-h2 font-semibold text-text-primary">{context.target_profile_position.replace(/_/g, ' ')}</h1>
        )}
        {!context.target_profile_position && <h1 className="text-h2 font-semibold text-text-primary">Job Description</h1>}
        {context.target_profile_domain && <span className="text-body-sm text-text-secondary">{context.target_profile_domain.replace(/_/g, ' ')}</span>}
        {activeResume?.file?.name && <span className="text-body-sm text-text-muted">Resume · {activeResume.file.name}</span>}
        <span className="ml-auto rounded-full border border-border px-2.5 py-0.5 text-caption font-medium text-text-muted">{context.mode}</span>
      </header>

      {/* Primary score */}
      <section>
        <ScoreHero score={summary.primary_score} label={summary.score_type.replace(/_/g, ' ')} />
        <p className="mt-3 max-w-lg text-body text-text-secondary">
          {SCORE_STATUS_SENTENCE[primaryScoreState.label] ?? SCORE_STATUS_SENTENCE.Partial}
        </p>
        {(scores.resume_quality != null || scores.target_fit != null) && (
          <div className="mt-5 flex flex-wrap gap-x-8 gap-y-2 border-t border-border-subtle pt-4">
            {scores.ats_alignment != null && summary.score_type !== 'ATS_ALIGNMENT' && (
              <div>
                <p className="text-label font-semibold uppercase tracking-wider text-text-muted">ATS Alignment</p>
                <p className="font-mono text-h3 font-semibold text-text-primary">{scores.ats_alignment}</p>
              </div>
            )}
            {scores.resume_quality != null && (
              <div>
                <p className="text-label font-semibold uppercase tracking-wider text-text-muted">Resume Quality</p>
                <p className="font-mono text-h3 font-semibold text-text-primary">{scores.resume_quality}</p>
              </div>
            )}
            {scores.target_fit != null && summary.score_type !== 'TARGET_FIT' && (
              <div>
                <p className="text-label font-semibold uppercase tracking-wider text-text-muted">Target Fit</p>
                <p className="font-mono text-h3 font-semibold text-text-primary">{scores.target_fit}</p>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Score breakdown */}
      {categories && (
        <section>
          <p className="mb-4 text-label font-semibold uppercase tracking-wider text-text-muted">Score breakdown</p>
          <div className="space-y-3">
            {Object.entries(categories).map(([category, result]) => (
              <ScoreBreakdownRow
                key={category}
                label={category.replace(/_/g, ' ')}
                score={Math.round(result.score * 100)}
                weight={Math.round(result.normalized_weight * 100)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Strengths */}
      <section>
        <p className="mb-4 text-label font-semibold uppercase tracking-wider text-text-muted">Strengths</p>
        {strengths.length ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {strengths.map((strength) => (
              <InsightCard
                key={strength.id}
                tone={strength.source === 'RESUME_QUALITY' ? 'neutral' : 'positive'}
                title={INSIGHT_TITLES[strength.type] ?? 'Strength'}
                description={strength.text}
              />
            ))}
          </div>
        ) : (
          <p className="text-body-sm text-text-secondary">No standout strengths were detected for this analysis yet.</p>
        )}
      </section>

      {/* Priority gaps */}
      <section>
        <p className="mb-4 text-label font-semibold uppercase tracking-wider text-text-muted">Priority gaps</p>
        {gapsByPriority.length ? (
          <div className="space-y-6">
            {gapsByPriority.map((group) => (
              <div key={group.priority}>
                <p
                  className="mb-2 text-caption font-semibold uppercase tracking-wider"
                  style={{
                    color:
                      group.priority === 'CRITICAL'
                        ? 'var(--color-error)'
                        : group.priority === 'HIGH'
                          ? 'var(--color-warning)'
                          : 'var(--color-text-muted)',
                  }}
                >
                  {group.priority}
                </p>
                <div className="space-y-2">
                  {group.items.map((gap) => {
                    const isQualityGap = gap.type === 'RESUME_QUALITY_GAP';
                    return (
                      <div key={gap.id} className="rounded-lg border border-border bg-surface px-4 py-3">
                        <p className="text-body-sm font-medium text-text-primary">{isQualityGap ? humanizeCode(gap.text) : gap.text}</p>
                        {gap.details?.what_is_missing && <p className="mt-0.5 text-caption text-text-secondary">{gap.details.what_is_missing}</p>}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-body-sm text-text-secondary">No gaps detected.</p>
        )}
      </section>

      {/* Requirement coverage */}
      {requirements?.length > 0 && (
        <section>
          <p className="mb-2 text-label font-semibold uppercase tracking-wider text-text-muted">Requirement coverage</p>
          <div className="rounded-lg border border-border bg-surface px-4">
            {requirements.map((req) => (
              <RequirementCard
                key={req.requirement_id}
                text={req.text}
                importance={req.importance}
                critical={req.critical}
                status={req.status}
              />
            ))}
          </div>
        </section>
      )}

      {/* Evidence explorer */}
      {evidenceRequirements.length > 0 && (
        <section>
          <p className="mb-4 text-label font-semibold uppercase tracking-wider text-text-muted">Evidence</p>
          <div className="space-y-3">
            {evidenceRequirements.map((req) => (
              <EvidenceCard
                key={req.requirement_id}
                requirement={req.text}
                evidenceText={req.evidence_text}
                source={req.evidence_source}
                status={req.status}
              />
            ))}
          </div>
        </section>
      )}

      {/* Recommendations */}
      <section>
        <p className="mb-2 text-label font-semibold uppercase tracking-wider text-text-muted">Recommendations</p>
        {recommendations.length ? (
          <div className="rounded-lg border border-border bg-surface px-5">
            {recommendations.map((rec, i) => (
              <RecommendationCard key={rec.id} index={i + 1} priority={rec.priority} type={rec.type.replace(/_/g, ' ')} message={rec.message} />
            ))}
          </div>
        ) : (
          <p className="text-body-sm text-text-secondary">No recommendations right now.</p>
        )}
      </section>
    </div>
  );
}
