import { cn } from '../../../lib/cn';

const PRIORITY_COLOR = {
  CRITICAL: 'var(--color-error)',
  HIGH: 'var(--color-warning)',
  MEDIUM: 'var(--color-primary)',
  LOW: 'var(--color-text-muted)',
};

/**
 * A single priority-ranked recommendation (frontendReadme §22) — reads
 * like expert product guidance ("01 · HIGH — Strengthen X"), not an AI
 * chat bubble. `index` is the 1-based rank within the recommendation list.
 */
export default function RecommendationCard({ index, priority = 'MEDIUM', type, message, relatedRequirement, className }) {
  const color = PRIORITY_COLOR[priority] ?? PRIORITY_COLOR.MEDIUM;

  return (
    <div className={cn('flex gap-4 border-b border-border-subtle py-4 last:border-none', className)}>
      <span className="font-mono text-body-sm font-medium text-text-muted">{String(index ?? 1).padStart(2, '0')}</span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="text-caption font-semibold uppercase tracking-wider" style={{ color }}>
            {priority}
          </span>
          {type && <span className="text-caption text-text-muted">· {type}</span>}
        </div>
        <p className="mt-1 text-body-sm text-text-primary">{message}</p>
        {relatedRequirement && <p className="mt-1 text-caption text-text-muted">Related to {relatedRequirement}</p>}
      </div>
    </div>
  );
}
