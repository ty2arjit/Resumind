import { useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button, ErrorState, FileUpload, RequirementCard, SectionCard, Spinner, Textarea } from '../../Components/design-system';
import { parseJobDescription, toUserMessage } from '../../lib/api';
import { useAppData } from '../../lib/AppDataContext';

/**
 * Job Description management (spec Phase 12 §13-16). Like Resumes, no
 * backend storage exists yet — this parses and inspects one JD per
 * session via the real /jobs/parse endpoint.
 */
export default function JobDescriptionsPage() {
  const { activeJobDescription, setActiveJobDescription } = useAppData();
  const [mode, setMode] = useState('paste'); // 'paste' | 'upload'
  const [text, setText] = useState('');
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  const submitText = async () => {
    if (!text.trim()) return;
    setStatus('loading');
    setError(null);
    try {
      const parsed = await parseJobDescription({ text });
      setActiveJobDescription({ text, parsed });
      setStatus('idle');
    } catch (err) {
      setError(toUserMessage(err));
      setStatus('error');
    }
  };

  const submitFile = async (file) => {
    if (!file) return;
    setStatus('loading');
    setError(null);
    try {
      const parsed = await parseJobDescription({ file });
      setActiveJobDescription({ file, parsed });
      setStatus('idle');
    } catch (err) {
      setError(toUserMessage(err));
      setStatus('error');
    }
  };

  const jd = activeJobDescription?.parsed;
  const requirementsByCategory = jd?.requirements?.reduce((acc, req) => {
    (acc[req.type] ??= []).push(req);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-h1 font-bold text-text-primary">Job Descriptions</h1>
        <p className="mt-1 text-body-lg text-text-secondary">Upload or paste a job description to see its parsed requirements.</p>
      </header>

      <SectionCard title="Add a job description">
        <div className="mb-4 inline-flex rounded-md border border-border p-1">
          <Button variant={mode === 'paste' ? 'primary' : 'tertiary'} size="sm" onClick={() => setMode('paste')}>
            Paste text
          </Button>
          <Button variant={mode === 'upload' ? 'primary' : 'tertiary'} size="sm" onClick={() => setMode('upload')}>
            Upload file
          </Button>
        </div>

        {mode === 'paste' ? (
          <div className="space-y-3">
            <Textarea label="Job description text" rows={8} value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste the full job description here..." />
            <Button onClick={submitText} disabled={!text.trim() || status === 'loading'}>
              Parse job description
            </Button>
          </div>
        ) : (
          <FileUpload label="Job description file" helperText="PDF or DOCX" accept=".pdf,.docx" fileName={activeJobDescription?.file?.name} onChange={(e) => submitFile(e.target.files?.[0])} />
        )}

        {status === 'loading' && <Spinner label="Understanding job description..." className="mt-3" />}
        {status === 'error' && <ErrorState className="mt-3" title="Job description parsing failed" description={error} onRetry={() => setStatus('idle')} />}
      </SectionCard>

      {jd && (
        <>
          <SectionCard title="Overview">
            <dl className="grid grid-cols-2 gap-y-2 text-body-sm sm:grid-cols-4">
              <dt className="text-text-secondary">Title</dt>
              <dd className="text-text-primary">{jd.metadata?.title ?? '—'}</dd>
              <dt className="text-text-secondary">Company</dt>
              <dd className="text-text-primary">{jd.metadata?.company ?? '—'}</dd>
              <dt className="text-text-secondary">Location</dt>
              <dd className="text-text-primary">{jd.metadata?.location ?? '—'}</dd>
              <dt className="text-text-secondary">Employment type</dt>
              <dd className="text-text-primary">{jd.metadata?.employment_type ?? '—'}</dd>
            </dl>
          </SectionCard>

          {Object.entries(requirementsByCategory ?? {}).map(([category, requirements]) => (
            <SectionCard key={category} title={category.replace(/_/g, ' ')}>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {requirements.map((req) => (
                  <RequirementCard key={req.id} text={req.text} importance={req.importance} critical={req.critical} category={undefined} />
                ))}
              </div>
            </SectionCard>
          ))}

          {jd.warnings?.length > 0 && (
            <SectionCard title="Parser warnings">
              <ul className="space-y-2">
                {jd.warnings.map((warning, i) => (
                  <li key={i} className="flex items-start gap-2 text-body-sm text-warning">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
                    {warning.message}
                  </li>
                ))}
              </ul>
            </SectionCard>
          )}
        </>
      )}
    </div>
  );
}
