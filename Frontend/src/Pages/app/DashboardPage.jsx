import { useNavigate } from 'react-router-dom';
import { ClipboardList, History, Target, Upload } from 'lucide-react';
import { Button, EmptyState, RecommendationCard, ScoreCard, SectionCard } from '../../Components/design-system';
import { useAppData } from '../../lib/AppDataContext';

const PRIORITY_ORDER = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

/**
 * Dashboard home (frontendReadme §14) — answers "what is my current
 * resume status" within a few seconds: current resume, then the three
 * core scores, then priority gaps, then recent analysis and top
 * recommendations, with Quick Actions last rather than first. Every
 * section reflects real, currently-held session data — sections with no
 * backing data show an honest empty state rather than invented numbers.
 */
export default function DashboardPage() {
  const navigate = useNavigate();
  const { activeResume, lastAnalysis } = useAppData();

  const priorityGaps = lastAnalysis
    ? PRIORITY_ORDER.flatMap((p) => lastAnalysis.gaps.filter((g) => g.priority === p)).slice(0, 3)
    : [];

  return (
    <div className="max-w-4xl space-y-10">
      <header>
        <h1 className="text-h1 font-semibold text-text-primary">Dashboard</h1>
        <p className="mt-1 text-body text-text-secondary">
          {activeResume?.file?.name ? (
            <>
              Currently reviewing <span className="font-medium text-text-primary">{activeResume.file.name}</span>
            </>
          ) : (
            'Upload a resume to get started.'
          )}
        </p>
      </header>

      <section>
        <p className="mb-3 text-label font-semibold uppercase tracking-wider text-text-muted">Scores</p>
        {lastAnalysis ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <ScoreCard title="ATS Alignment" description="Match to this job" score={lastAnalysis.scores.ats_alignment ?? 0} />
            <ScoreCard title="Resume Quality" description="Structure & evidence" score={lastAnalysis.scores.resume_quality ?? 0} />
            <ScoreCard title="Target Fit" description="Career target alignment" score={lastAnalysis.scores.target_fit ?? 0} />
          </div>
        ) : (
          <EmptyState
            icon={ClipboardList}
            title="No analyses yet"
            description="Analyze your resume against a job description to see your ATS alignment."
            action={
              <Button size="sm" onClick={() => navigate('/analyses/new')}>
                Start Analysis
              </Button>
            }
          />
        )}
      </section>

      {priorityGaps.length > 0 && (
        <section>
          <p className="mb-3 text-label font-semibold uppercase tracking-wider text-text-muted">Priority gaps</p>
          <SectionCard className="!p-0">
            <div className="px-5">
              {priorityGaps.map((gap) => (
                <div key={gap.id} className="flex items-center justify-between gap-3 border-b border-border-subtle py-3 last:border-none">
                  <p className="text-body-sm text-text-primary">{gap.text}</p>
                  <span
                    className="text-caption font-semibold uppercase tracking-wider"
                    style={{ color: gap.priority === 'CRITICAL' ? 'var(--color-error)' : gap.priority === 'HIGH' ? 'var(--color-warning)' : 'var(--color-text-muted)' }}
                  >
                    {gap.priority}
                  </span>
                </div>
              ))}
            </div>
          </SectionCard>
        </section>
      )}

      <div className="grid grid-cols-1 gap-10 md:grid-cols-2">
        <section>
          <p className="mb-3 text-label font-semibold uppercase tracking-wider text-text-muted">Recent analysis</p>
          {lastAnalysis ? (
            <SectionCard>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-body-sm font-medium text-text-primary">{lastAnalysis.summary.score_type.replace(/_/g, ' ')}</p>
                  <p className="mt-0.5 font-mono text-h3 font-semibold text-text-primary">{lastAnalysis.summary.primary_score}</p>
                </div>
                <Button variant="tertiary" size="sm" onClick={() => navigate('/analyses/result')}>
                  View
                </Button>
              </div>
            </SectionCard>
          ) : (
            <p className="text-body-sm text-text-secondary">No analyses yet this session.</p>
          )}
        </section>

        <section>
          <p className="mb-3 text-label font-semibold uppercase tracking-wider text-text-muted">Top recommendations</p>
          {lastAnalysis?.recommendations?.length ? (
            <SectionCard className="!p-0">
              <div className="px-5">
                {lastAnalysis.recommendations.slice(0, 2).map((rec, i) => (
                  <RecommendationCard key={rec.id} index={i + 1} priority={rec.priority} message={rec.message} />
                ))}
              </div>
            </SectionCard>
          ) : (
            <p className="text-body-sm text-text-secondary">Recommendations will appear here after your first analysis.</p>
          )}
        </section>
      </div>

      <section className="border-t border-border-subtle pt-6">
        <p className="mb-3 text-label font-semibold uppercase tracking-wider text-text-muted">Quick actions</p>
        <div className="flex flex-wrap gap-2.5">
          <Button variant="tertiary" size="sm" icon={Upload} onClick={() => navigate('/resumes')}>
            Upload Resume
          </Button>
          <Button variant="tertiary" size="sm" icon={ClipboardList} onClick={() => navigate('/analyses/new')}>
            Analyze Against Job
          </Button>
          <Button variant="tertiary" size="sm" icon={Target} onClick={() => navigate('/target-profiles')}>
            Create Target Profile
          </Button>
          <Button variant="tertiary" size="sm" icon={History} onClick={() => navigate('/history')}>
            View Previous Analysis
          </Button>
        </div>
      </section>
    </div>
  );
}
