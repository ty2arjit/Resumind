import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, ErrorState, FileUpload, Select, SectionCard, Spinner, Textarea, Toggle } from '../../Components/design-system';
import { listTargetDomains, listTargetPositions, runAnalysis, toUserMessage } from '../../lib/api';
import { useAppData } from '../../lib/AppDataContext';

/**
 * Analysis creation flow (spec Phase 12 §17-18): select resume, select
 * JD, optionally add a target profile, run the real /analysis endpoint.
 * The backend call is a single synchronous request with no intermediate
 * stage events, so this deliberately shows one honest indeterminate
 * loading state rather than fabricating a multi-step progress animation.
 */
export default function AnalysisNewPage() {
  const navigate = useNavigate();
  const { activeResume, setActiveResume, activeJobDescription, lastAnalysis, setLastAnalysis } = useAppData();

  const [jdText, setJdText] = useState(activeJobDescription?.text ?? '');
  const [useTargetProfile, setUseTargetProfile] = useState(false);
  const [positions, setPositions] = useState([]);
  const [domains, setDomains] = useState([]);
  const [position, setPosition] = useState('');
  const [domain, setDomain] = useState('');
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (useTargetProfile) {
      listTargetPositions().then(setPositions).catch(() => setPositions([]));
      listTargetDomains().then(setDomains).catch(() => setDomains([]));
    }
  }, [useTargetProfile]);

  const canRun = activeResume?.file && (jdText.trim() || (useTargetProfile && position));

  const handleRun = async () => {
    setStatus('running');
    setError(null);
    try {
      const result = await runAnalysis({
        resumeFile: activeResume.file,
        jobDescriptionText: jdText.trim() || undefined,
        position: useTargetProfile ? position || undefined : undefined,
        domain: useTargetProfile ? domain || undefined : undefined,
      });
      setLastAnalysis(result);
      setStatus('idle');
      navigate('/analyses/result');
    } catch (err) {
      setError(toUserMessage(err));
      setStatus('error');
    }
  };

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-h1 font-bold text-text-primary">New Analysis</h1>
        <p className="mt-1 text-body-lg text-text-secondary">Analyze your resume against a job description, a target profile, or both.</p>
      </header>

      <SectionCard title="1. Resume">
        {activeResume?.file ? (
          <p className="text-body-sm text-text-primary">Using <span className="font-semibold">{activeResume.file.name}</span> (uploaded earlier).</p>
        ) : (
          <FileUpload label="Resume file" helperText="PDF or DOCX" accept=".pdf,.docx" onChange={(e) => setActiveResume({ file: e.target.files?.[0], parsed: null })} />
        )}
      </SectionCard>

      <SectionCard title="2. Job description">
        <Textarea label="Paste job description text" rows={6} value={jdText} onChange={(e) => setJdText(e.target.value)} placeholder="Paste the job description you want to match against..." />
      </SectionCard>

      <SectionCard title="3. Target profile (optional)">
        <Toggle label="Also evaluate against a Position + Domain target profile" checked={useTargetProfile} onChange={(e) => setUseTargetProfile(e.target.checked)} />
        {useTargetProfile && (
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
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
        )}
      </SectionCard>

      <div className="flex items-center gap-3">
        <Button onClick={handleRun} disabled={!canRun || status === 'running'}>
          Start Analysis
        </Button>
        {lastAnalysis && (
          <Button variant="tertiary" onClick={() => navigate('/analyses/result')}>
            View last result
          </Button>
        )}
      </div>

      {status === 'running' && <Spinner label="Running analysis — parsing, matching, and scoring your resume..." />}
      {status === 'error' && <ErrorState title="Analysis failed" description={error} onRetry={() => setStatus('idle')} />}
    </div>
  );
}
