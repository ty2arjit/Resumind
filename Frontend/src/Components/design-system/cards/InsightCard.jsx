import { cn } from '../../../lib/cn';

const TONE_COLOR = {
  positive: 'var(--color-teal)',
  neutral: 'var(--color-primary)',
  attention: 'var(--color-warning)',
};

/**
 * A compact strength/insight (frontendReadme §18) — text-led, a single
 * thin top accent rule for tone rather than an icon badge on every card
 * (spec explicitly warns against overusing checkmark icons).
 */
export default function InsightCard({ tone = 'neutral', title, description, className }) {
  const color = TONE_COLOR[tone] ?? TONE_COLOR.neutral;
  return (
    <div
      className={cn('rounded-lg border border-border bg-surface p-4', className)}
      style={{ borderTop: `2px solid ${color}` }}
    >
      <p className="text-body-sm font-semibold text-text-primary">{title}</p>
      {description && <p className="mt-1 text-body-sm text-text-secondary">{description}</p>}
    </div>
  );
}
