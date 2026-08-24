import { useState } from 'react';
import { AlertTriangle, FileText, Mail, MapPin, Phone } from 'lucide-react';
import { Button, ErrorState, FileUpload, ScoreBar, SectionCard, Spinner } from '../../Components/design-system';
import { parseResume, analyzeResumeQuality, toUserMessage } from '../../lib/api';
import { useAppData } from '../../lib/AppDataContext';

const SUPPORTED_TYPES = '.pdf,.docx';

/**
 * Resume management (spec Phase 12 §8-10). Backend/fastapi_app has no
 * resume storage yet (no ResumeVersion table wired up) — there is
 * nothing to list, rename, or version. This page honestly reflects that:
 * it lets a user parse and inspect ONE resume for the current session
 * (a real, working capability), rather than fabricating a saved list.
 */
export default function ResumesPage() {
  const { activeResume, setActiveResume } = useAppData();
  const [status, setStatus] = useState('idle'); // idle | uploading | error
  const [error, setError] = useState(null);
  const [quality, setQuality] = useState(null);
  const [qualityStatus, setQualityStatus] = useState('idle');

  const handleFile = async (file) => {
    if (!file) return;
    setStatus('uploading');
    setError(null);
    setQuality(null);
    try {
      const parsed = await parseResume(file);
      setActiveResume({ file, parsed });
      setStatus('idle');
      setQualityStatus('uploading');
      try {
        const qualityResult = await analyzeResumeQuality(file);
        setQuality(qualityResult);
      } finally {
        setQualityStatus('idle');
      }
    } catch (err) {
      setError(toUserMessage(err));
      setStatus('error');
    }
  };

  const resume = activeResume?.parsed;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-h1 font-bold text-text-primary">Resumes</h1>
        <p className="mt-1 text-body-lg text-text-secondary">Upload a resume to parse and inspect it.</p>
      </header>

      <SectionCard title="Upload resume">
        <FileUpload
          label="Resume file"
          fileName={activeResume?.file?.name}
          helperText="PDF or DOCX"
          accept={SUPPORTED_TYPES}
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        {status === 'uploading' && <Spinner label="Parsing resume..." className="mt-3" />}
        {status === 'error' && <ErrorState className="mt-3" title="Resume parsing failed" description={error} onRetry={() => setStatus('idle')} />}
      </SectionCard>

      {resume && (
        <>
          <SectionCard title="Contact">
            <div className="flex flex-wrap gap-4 text-body-sm text-text-secondary">
              {resume.contact?.name && <span className="font-semibold text-text-primary">{resume.contact.name}</span>}
              {resume.contact?.email && (
                <span className="flex items-center gap-1.5">
                  <Mail className="h-4 w-4" aria-hidden="true" /> {resume.contact.email}
                </span>
              )}
              {resume.contact?.phone && (
                <span className="flex items-center gap-1.5">
                  <Phone className="h-4 w-4" aria-hidden="true" /> {resume.contact.phone}
                </span>
              )}
              {resume.contact?.location && (
                <span className="flex items-center gap-1.5">
                  <MapPin className="h-4 w-4" aria-hidden="true" /> {resume.contact.location}
                </span>
              )}
            </div>
          </SectionCard>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <SectionCard title="Skills">
              {resume.skills?.length ? (
                <div className="flex flex-wrap gap-1.5">
                  {resume.skills.flatMap((cat) => cat.items).map((item) => (
                    <span key={item} className="rounded-full bg-primary/10 px-2.5 py-1 text-caption font-medium text-primary">
                      {item}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-body-sm text-text-secondary">No skills section detected.</p>
              )}
            </SectionCard>

            <SectionCard title="Document metadata">
              <dl className="grid grid-cols-2 gap-y-2 text-body-sm">
                <dt className="text-text-secondary">File</dt>
                <dd className="text-text-primary">{activeResume.file?.name}</dd>
                <dt className="text-text-secondary">Pages</dt>
                <dd className="text-text-primary">{resume.document?.page_count ?? '—'}</dd>
                <dt className="text-text-secondary">Extraction status</dt>
                <dd className="text-text-primary">{resume.document?.extraction_status}</dd>
                <dt className="text-text-secondary">Sections detected</dt>
                <dd className="text-text-primary">{resume.sections?.length ?? 0}</dd>
              </dl>
            </SectionCard>
          </div>

          <SectionCard title="Experience">
            {resume.experience?.length ? (
              <ul className="space-y-4">
                {resume.experience.map((entry, i) => (
                  <li key={i} className="border-b border-border-subtle pb-4 last:border-none last:pb-0">
                    <p className="text-body font-semibold text-text-primary">
                      {entry.role} {entry.organization && `· ${entry.organization}`}
                    </p>
                    <ul className="mt-1 list-disc space-y-0.5 pl-5 text-body-sm text-text-secondary">
                      {entry.bullets?.map((bullet, j) => (
                        <li key={j}>{bullet}</li>
                      ))}
                    </ul>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-body-sm text-text-secondary">No experience section detected.</p>
            )}
          </SectionCard>

          <SectionCard title="Education">
            {resume.education?.length ? (
              <ul className="space-y-2">
                {resume.education.map((entry, i) => (
                  <li key={i} className="text-body-sm text-text-primary">
                    {entry.degree} {entry.field && `in ${entry.field}`} {entry.institution && `· ${entry.institution}`}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-body-sm text-text-secondary">No education section detected.</p>
            )}
          </SectionCard>

          {resume.warnings?.length > 0 && (
            <SectionCard title="Parser warnings">
              <ul className="space-y-2">
                {resume.warnings.map((warning, i) => (
                  <li key={i} className="flex items-start gap-2 text-body-sm text-warning">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
                    {warning.message}
                  </li>
                ))}
              </ul>
            </SectionCard>
          )}

          <SectionCard title="Resume Quality">
            {qualityStatus === 'uploading' && <Spinner label="Evaluating resume quality..." />}
            {quality && (
              <div className="space-y-3">
                <p className="text-h2 font-bold tabular-nums text-text-primary">{quality.resume_quality}/100</p>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {Object.entries(quality.dimension_scores).map(([dimension, score]) => (
                    <ScoreBar key={dimension} score={Math.round(score * 100)} label={dimension.replace(/_/g, ' ')} />
                  ))}
                </div>
              </div>
            )}
          </SectionCard>
        </>
      )}

      {!resume && status === 'idle' && (
        <div className="flex items-center gap-2 text-body-sm text-text-muted">
          <FileText className="h-4 w-4" aria-hidden="true" />
          Resume storage isn't connected yet — this page parses and shows one resume per session rather than a saved list.
        </div>
      )}
    </div>
  );
}
