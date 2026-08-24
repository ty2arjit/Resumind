import { Check, CircleDashed, CircleSlash, TriangleAlert } from 'lucide-react';
import { getMatchStrengthDisplay } from '../score/scoreStates';
import { cn } from '../../../lib/cn';

const STATUS_ICON = {
  'match-very-strong': Check,
  'match-strong': Check,
  'match-partial': TriangleAlert,
  'match-weak': TriangleAlert,
  'match-missing': CircleSlash,
  'match-unknown': CircleDashed,
};

/**
 * A single row of Requirement Coverage (frontendReadme §20) — compact,
 * scannable, symbol-led (✓ / ⚠ / ×) rather than a heavy card, so a full
 * requirement list reads as one continuous table rather than 30 stacked
 * cards.
 */
export default function RequirementCard({ text, category, importance, critical, status, score, className }) {
  const display = getMatchStrengthDisplay(status);
  const color = `var(--color-${display.token})`;
  const Icon = STATUS_ICON[display.token] ?? CircleDashed;

  return (
    <div className={cn('flex items-center gap-3 border-b border-border-subtle py-2.5 last:border-none', className)}>
      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full" style={{ backgroundColor: `var(--color-${display.token}-surface)`, color }}>
        <Icon className="h-3 w-3" strokeWidth={2.25} aria-hidden="true" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-body-sm text-text-primary">{text}</p>
        {category && <p className="text-caption text-text-muted">{category}</p>}
      </div>
      {typeof score === 'number' && (
        <span className="hidden shrink-0 font-mono text-body-sm text-text-muted sm:block">{Math.round(score * 100)}</span>
      )}
      {(critical || importance) && (
        <span className="shrink-0 text-caption font-medium uppercase tracking-wide text-text-muted">
          {critical ? 'Critical' : importance?.toLowerCase()}
        </span>
      )}
      <span className="shrink-0 text-caption font-semibold uppercase tracking-wider" style={{ color }}>
        {display.label}
      </span>
    </div>
  );
}
