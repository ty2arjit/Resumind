import { useEffect, useState } from 'react';
import {
  Button,
  ErrorState,
  ImportanceBadge,
  MatchStatusBadge,
  ScoreCard,
  SectionCard,
  Select,
  Spinner,
  Textarea,
} from '../../Components/design-system';
import { analyzeTargetFit, listTargetDomains, listTargetPositions, previewTargetProfile, toUserMessage } from '../../lib/api';
import { useAppData } from '../../lib/AppDataContext';

const CATEGORY_LABELS = {
  core_skills: 'Core Skills',
  technologies: 'Technologies',
  responsibilities: 'Responsibilities',
  domain_knowledge: 'Domain Knowledge',
  experience_expectations: 'Experience',
  preferred_skills: 'Preferred Skills',
};

function parseCsv(value) {
  return value
    .split(',')
    .map((v) => v.trim())
    .filter(Boolean);
}

/**
 * Target Profile flow (spec Phase 12 §28-30): Position + Domain -> Base
 * Target Profile -> review expectations -> optional custom requirements
 * -> preview effective profile -> analyze against the active resume.
 * Every list below comes from the real /target-profiles endpoints.
 */
export default function TargetProfilesPage() {
  const { activeResume } = useAppData();
  const [positions, setPositions] = useState([]);
  const [domains, setDomains] = useState([]);
  const [position, setPosition] = useState('');
  const [domain, setDomain] = useState('');
  const [customText, setCustomText] = useState({});
  const [profile, setProfile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  useEffect(() => {
    listTargetPositions().then(setPositions).catch(() => setPositions([]));
    listTargetDomains().then(setDomains).catch(() => setDomains([]));
  }, []);

  const customRequirements = Object.fromEntries(
    Object.entries(customText).map(([key, value]) => [key, parseCsv(value)])
  );

  const handlePreview = async () => {
    if (!position) return;
    setStatus('loading');
    setError(null);
    setAnalysis(null);
    try {
      const result = await previewTargetProfile({ position, domain: domain || null, customRequirements });
      setProfile(result);
      setStatus('idle');
    } catch (err) {
      setError(toUserMessage(err));
      setStatus('error');
    }
  };

  const handleAnalyze = async () => {
    if (!activeResume?.file || !position) return;
    setStatus('analyzing');
    setError(null);
    try {
      const result = await analyzeTargetFit({ file: activeResume.file, position, domain: domain || null, customRequirements });
      setAnalysis(result);
      setStatus('idle');
    } catch (err) {
      setError(toUserMessage(err));
      setStatus('error');
    }
  };

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-h1 font-bold text-text-primary">Target Profiles</h1>
        <p className="mt-1 text-body-lg text-text-secondary">Define a position and domain to see what's generally expected — with or without a specific job description.</p>
      </header>

      <SectionCard title="Position and domain">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Select label="Position" value={position} onChange={(e) => setPosition(e.target.value)}>
            <option value="">Select a position</option>
            {positions.map((p) => (
              <option key={p} value={p}>
                {p.replace(/_/g, ' ')}
              </option>
            ))}
          </Select>
          <Select label="Domain (optional)" value={domain} onChange={(e) => setDomain(e.target.value)}>
            <option value="">No domain</option>
            {domains.map((d) => (
              <option key={d} value={d}>
                {d.replace(/_/g, ' ')}
              </option>
            ))}
          </Select>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
            <Textarea
              key={key}
              label={`Custom ${label} (comma-separated)`}
              rows={2}
              value={customText[key] ?? ''}
              onChange={(e) => setCustomText((prev) => ({ ...prev, [key]: e.target.value }))}
            />
          ))}
        </div>

        <div className="mt-4 flex flex-wrap gap-3">
          <Button onClick={handlePreview} disabled={!position || status === 'loading'}>
            Preview profile
          </Button>
          <Button variant="secondary" onClick={handleAnalyze} disabled={!position || !activeResume?.file || status === 'analyzing'}>
            Analyze my resume against this profile
          </Button>
        </div>
        {!activeResume?.file && <p className="mt-2 text-caption text-text-muted">Upload a resume on the Resumes page first to run an analysis.</p>}

        {status === 'loading' && <Spinner label="Loading profile..." className="mt-3" />}
        {status === 'analyzing' && <Spinner label="Analyzing target fit..." className="mt-3" />}
        {status === 'error' && <ErrorState className="mt-3" title="Target profile request failed" description={error} onRetry={() => setStatus('idle')} />}
      </SectionCard>

      {profile && (
        <SectionCard title="Effective target profile">
          <div className="space-y-4">
            {Object.entries(CATEGORY_LABELS).map(([key, label]) => {
              const items = profile.effective?.[key] ?? [];
              if (!items.length) return null;
              return (
                <div key={key}>
                  <p className="text-label font-semibold uppercase tracking-wide text-text-muted">{label}</p>
                  <div className="mt-1.5 flex flex-wrap gap-1.5">
                    {items.map((item) => (
                      <span key={item} className="rounded-full bg-surface-muted px-2.5 py-1 text-caption font-medium text-text-secondary">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </SectionCard>
      )}

      {analysis && (
        <SectionCard title="Target fit results">
          <div className="flex flex-wrap gap-4">
            <ScoreCard title="Target Fit" description="Overall alignment with this profile" score={analysis.scores.target_fit} />
            <ScoreCard title="Position Fit" description="Core skills, technologies, responsibilities" score={analysis.scores.position_fit} />
            <ScoreCard title="Domain Fit" description="Domain-specific evidence" score={analysis.scores.domain_fit} />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {analysis.requirements?.map((req) => (
              <div key={req.requirement_id} className="flex items-center justify-between gap-3 rounded-md border border-border px-3 py-2">
                <span className="text-body-sm text-text-primary">{req.text}</span>
                <div className="flex items-center gap-2">
                  <ImportanceBadge importance={req.importance} />
                  <MatchStatusBadge status={req.status} />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      )}
    </div>
  );
}
