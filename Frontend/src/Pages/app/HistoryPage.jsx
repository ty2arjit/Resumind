import { useNavigate } from 'react-router-dom';
import { History } from 'lucide-react';
import { Button, EmptyState, SectionCard } from '../../Components/design-system';
import { useAppData } from '../../lib/AppDataContext';

/**
 * Analysis history (spec Phase 12 §31). Backend/fastapi_app does not yet
 * persist Analysis rows (Postgres is unreachable in this environment —
 * see Phase 9/10's final reports), so there is no real history to list.
 * Per spec §1/§42's "do not create fake data" rule, this shows an honest
 * empty state rather than inventing rows — the current session's most
 * recent analysis (if any) is offered as the one real thing available.
 */
export default function HistoryPage() {
  const navigate = useNavigate();
  const { lastAnalysis } = useAppData();

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-h1 font-bold text-text-primary">History</h1>
        <p className="mt-1 text-body-lg text-text-secondary">Previous analyses.</p>
      </header>

      {lastAnalysis ? (
        <SectionCard title="This session's analysis">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-body font-semibold text-text-primary">{lastAnalysis.summary.score_type.replace(/_/g, ' ')}</p>
              <p className="text-body-sm text-text-secondary">Score: {lastAnalysis.summary.primary_score}/100</p>
            </div>
            <Button variant="secondary" onClick={() => navigate('/analyses/result')}>
              View
            </Button>
          </div>
        </SectionCard>
      ) : (
        <EmptyState
          icon={History}
          title="No analysis history yet"
          description="Analysis history requires backend persistence, which isn't connected in this environment yet. Run an analysis to see it here for this session."
          action={<Button onClick={() => navigate('/analyses/new')}>Start Analysis</Button>}
        />
      )}
    </div>
  );
}
