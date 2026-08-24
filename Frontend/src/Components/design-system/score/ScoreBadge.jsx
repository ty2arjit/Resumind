import { getScoreState } from './scoreStates';

/** Compact inline score chip — for tables, lists, and dense layouts
 * where a full ScoreRing/ScoreBar would be too heavy. */
export default function ScoreBadge({ score, size = 'md' }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const state = getScoreState(clamped);
  const padding = size === 'sm' ? 'px-2 py-0.5 text-caption' : 'px-2.5 py-1 text-body-sm';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-mono font-medium ${padding}`}
      style={{ backgroundColor: `var(--color-${state.token}-surface)`, color: `var(--color-${state.token})` }}
    >
      {clamped}
      <span className="font-medium opacity-80">{state.shortLabel}</span>
    </span>
  );
}
