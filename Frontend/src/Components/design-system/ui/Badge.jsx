import { AlertTriangle, Check, CircleDashed, CircleSlash, Minus, TriangleAlert } from 'lucide-react';
import { getMatchStrengthDisplay } from '../score/scoreStates';
import { cn } from '../../../lib/cn';

const IMPORTANCE_VARIANTS = {
  REQUIRED: { label: 'Required', className: 'bg-error-surface text-error' },
  PREFERRED: { label: 'Preferred', className: 'bg-info-surface text-info' },
  OPTIONAL: { label: 'Optional', className: 'bg-surface-muted text-text-secondary' },
  CRITICAL: { label: 'Critical', className: 'bg-error-surface text-error' },
};

const MATCH_ICONS = {
  'match-very-strong': Check,
  'match-strong': Check,
  'match-partial': TriangleAlert,
  'match-weak': AlertTriangle,
  'match-missing': CircleSlash,
  'match-unknown': CircleDashed,
};

/**
 * Status badges (spec §20). Never color-only — always icon + text +
 * color, so status is legible without relying on color perception
 * (spec §32 accessibility).
 */
export function Badge({ children, className }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full bg-surface-muted px-2.5 py-1 text-caption font-semibold text-text-secondary',
        className
      )}
    >
      {children}
    </span>
  );
}

export function ImportanceBadge({ importance }) {
  const config = IMPORTANCE_VARIANTS[importance] ?? IMPORTANCE_VARIANTS.OPTIONAL;
  return <Badge className={config.className}>{config.label}</Badge>;
}

export function MatchStatusBadge({ status }) {
  const display = getMatchStrengthDisplay(status);
  const Icon = MATCH_ICONS[display.token] ?? Minus;
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-caption font-semibold"
      style={{ backgroundColor: `var(--color-${display.token}-surface)`, color: `var(--color-${display.token})` }}
    >
      <Icon className="h-3 w-3" aria-hidden="true" />
      {display.label}
    </span>
  );
}
