import BaseCard from './BaseCard';
import { getScoreState } from '../score/scoreStates';
import { cn } from '../../../lib/cn';

/**
 * A named score with its own explanation (frontendReadme §12, §24) —
 * number-first, not a giant donut: "84 / ATS ALIGNMENT / Strong
 * alignment." ATS Alignment, Resume Quality, and Target Fit share this
 * exact layout so the three stay visually consistent while their
 * description text keeps their meaning distinct.
 */
export default function ScoreCard({ title, description, score, className }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const state = getScoreState(clamped);
  const color = `var(--color-${state.token})`;

  return (
    <BaseCard className={cn('flex flex-col gap-3', className)}>
      <div className="flex items-baseline gap-2.5">
        <span className="font-mono text-score-md font-semibold leading-none tracking-tight text-text-primary">
          {clamped}
        </span>
        <span className="text-caption font-semibold uppercase tracking-wider" style={{ color }}>
          {state.label}
        </span>
      </div>
      <div>
        <p className="text-label font-semibold uppercase tracking-wider text-text-muted">{title}</p>
        {description && <p className="mt-0.5 text-body-sm text-text-secondary">{description}</p>}
      </div>
    </BaseCard>
  );
}
