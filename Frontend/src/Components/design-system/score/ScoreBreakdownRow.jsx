import { getScoreState } from './scoreStates';

/**
 * A single category/dimension row — label, mono score number, and a
 * compact horizontal bar on one line (frontendReadme §12's example:
 * "Required Skills   91  ███████████░"). Used for score breakdowns
 * instead of a grid of separate ring charts.
 */
export default function ScoreBreakdownRow({ label, score, weight }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const state = getScoreState(clamped);
  const color = `var(--color-${state.token})`;

  return (
    <div className="flex items-center gap-4">
      <span className="w-40 shrink-0 truncate text-body-sm text-text-secondary">{label}</span>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-muted">
        <div
          className="h-full rounded-full"
          style={{ width: `${clamped}%`, backgroundColor: color, transition: 'width var(--motion-slow) var(--motion-ease)' }}
        />
      </div>
      <span className="w-9 shrink-0 text-right font-mono text-body-sm font-medium text-text-primary">{clamped}</span>
      {weight != null && <span className="w-12 shrink-0 text-right font-mono text-caption text-text-muted">{weight}%</span>}
    </div>
  );
}
