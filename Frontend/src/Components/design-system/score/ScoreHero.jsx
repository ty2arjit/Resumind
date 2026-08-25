import { getScoreState } from './scoreStates';
import AnimatedNumber from '../motion/AnimatedNumber';

/**
 * The primary, number-first score display (frontendReadme §12):
 *
 *   84
 *   ATS ALIGNMENT
 *   Strong alignment
 *
 * Deliberately not a giant donut — a prominent IBM Plex Mono number
 * carries the hierarchy, with a small semantic status label beneath it.
 */
export default function ScoreHero({ score, label, description }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const state = getScoreState(clamped);
  const color = `var(--color-${state.token})`;

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-baseline gap-3">
        <AnimatedNumber value={clamped} className="font-mono text-score-lg font-semibold leading-none tracking-tight text-text-primary" />
        <span className="text-caption font-semibold uppercase tracking-wider" style={{ color }}>
          {state.label}
        </span>
      </div>
      {label && <p className="text-label font-semibold uppercase tracking-wider text-text-muted">{label}</p>}
      {description && <p className="mt-1 text-body-sm text-text-secondary">{description}</p>}
    </div>
  );
}
