import { getMatchStrengthDisplay } from '../score/scoreStates';
import { cn } from '../../../lib/cn';

/**
 * Requirement → Evidence → Source → Match (frontendReadme §21 — a
 * signature Resumind feature). Deliberately not another heavy bordered
 * card: a subtle left accent rule carries the match-strength color, kept
 * light so a list of these reads as one continuous, scannable block.
 */
export default function EvidenceCard({ requirement, evidenceText, source, status, technologies = [], className }) {
  const display = getMatchStrengthDisplay(status);
  const color = `var(--color-${display.token})`;

  return (
    <div
      className={cn('flex flex-col gap-2 rounded-md border border-border-subtle bg-surface py-3 pl-4 pr-4', className)}
      style={{ borderLeft: `2.5px solid ${color}` }}
    >
      {requirement && (
        <div className="flex items-center justify-between gap-3">
          <p className="text-body-sm font-medium text-text-primary">{requirement}</p>
          {status && (
            <span className="shrink-0 text-caption font-semibold uppercase tracking-wider" style={{ color }}>
              {display.label}
            </span>
          )}
        </div>
      )}
      <p className="text-body-sm italic text-text-secondary">&ldquo;{evidenceText}&rdquo;</p>
      <div className="flex flex-wrap items-center justify-between gap-2">
        {source && <p className="text-caption text-text-muted">{source}</p>}
        {technologies.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {technologies.map((tech) => (
              <span key={tech} className="rounded-full bg-soft-brand px-2 py-0.5 font-mono text-caption font-medium text-primary">
                {tech}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
