import { getScoreState } from './scoreStates';

const SIZES = {
  sm: { box: 72, stroke: 6, textClass: 'text-score-sm' },
  md: { box: 104, stroke: 8, textClass: 'text-score-md' },
  lg: { box: 144, stroke: 10, textClass: 'text-score-lg' },
};

/**
 * Radial score visualization (spec Phase 11 §14). Reused everywhere a
 * 0-100 score is shown (ATS Alignment, Resume Quality, Target Fit,
 * Position Fit, Domain Fit) — the same score always looks the same.
 */
export default function ScoreRing({ score, label, size = 'md', showState = true }) {
  const { box, stroke, textClass } = SIZES[size] ?? SIZES.md;
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const state = getScoreState(clamped);
  const radius = (box - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - clamped / 100);
  const color = `var(--color-${state.token})`;

  return (
    <div className="inline-flex flex-col items-center gap-2" role="img" aria-label={`${label ?? 'Score'}: ${clamped} out of 100, ${state.label}`}>
      <div className="relative" style={{ width: box, height: box }}>
        <svg width={box} height={box} viewBox={`0 0 ${box} ${box}`} className="-rotate-90">
          <circle cx={box / 2} cy={box / 2} r={radius} fill="none" stroke="var(--color-border)" strokeWidth={stroke} />
          <circle
            cx={box / 2}
            cy={box / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: `stroke-dashoffset var(--motion-slow) var(--motion-ease)` }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`${textClass} font-mono font-semibold text-text-primary`}>{clamped}</span>
        </div>
      </div>
      {label && <span className="text-body-sm font-medium text-text-secondary">{label}</span>}
      {showState && (
        <span className="text-caption font-semibold uppercase tracking-wide" style={{ color }}>
          {state.label}
        </span>
      )}
    </div>
  );
}
