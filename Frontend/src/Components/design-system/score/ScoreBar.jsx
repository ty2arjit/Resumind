import { getScoreState } from './scoreStates';

/** Horizontal score visualization — used for category/dimension
 * breakdowns (spec §14, §26) where several scores are compared at once. */
export default function ScoreBar({ score, label, showValue = true }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const state = getScoreState(clamped);
  const color = `var(--color-${state.token})`;

  return (
    <div className="w-full">
      <div className="mb-1.5 flex items-center justify-between">
        {label && <span className="text-body-sm font-medium text-text-secondary">{label}</span>}
        {showValue && (
          <span className="font-mono text-body-sm font-medium text-text-primary">{clamped}</span>
        )}
      </div>
      <div
        className="h-2 w-full overflow-hidden rounded-full bg-surface-muted"
        role="progressbar"
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label}
      >
        <div
          className="h-full rounded-full"
          style={{ width: `${clamped}%`, backgroundColor: color, transition: 'width var(--motion-slow) var(--motion-ease)' }}
        />
      </div>
    </div>
  );
}
