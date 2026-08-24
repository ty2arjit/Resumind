/**
 * Presentation-only score-state buckets (spec Phase 11 §15). These
 * thresholds describe how a 0-100 score is *displayed* — they are a
 * distinct, frontend-only concept from the backend's actual scoring
 * algorithm/config (Backend/fastapi_app/app/modules/scoring/config.py).
 * Never let these values leak back into scoring logic.
 */
export const SCORE_STATES = [
  { min: 90, max: 100, label: 'Very Strong', shortLabel: 'Very Strong', token: 'match-very-strong' },
  { min: 75, max: 89, label: 'Strong', shortLabel: 'Strong', token: 'match-strong' },
  { min: 60, max: 74, label: 'Partial', shortLabel: 'Partial', token: 'match-partial' },
  { min: 40, max: 59, label: 'Weak', shortLabel: 'Weak', token: 'match-weak' },
  { min: 0, max: 39, label: 'Low', shortLabel: 'Low', token: 'match-missing' },
];

export function getScoreState(score) {
  const clamped = Math.max(0, Math.min(100, Math.round(score ?? 0)));
  return SCORE_STATES.find((state) => clamped >= state.min && clamped <= state.max) ?? SCORE_STATES[SCORE_STATES.length - 1];
}

/** Maps a backend MatchStrength value directly to its display token —
 * distinct from the numeric score-state buckets above, since a single
 * requirement's status (e.g. "PARTIAL") is a discrete label, not a
 * percentage to bucket. */
export const MATCH_STRENGTH_TOKENS = {
  VERY_STRONG: { label: 'Very Strong', token: 'match-very-strong' },
  STRONG: { label: 'Strong', token: 'match-strong' },
  PARTIAL: { label: 'Partial', token: 'match-partial' },
  WEAK: { label: 'Weak', token: 'match-weak' },
  MISSING: { label: 'Missing', token: 'match-missing' },
  UNKNOWN: { label: 'Unknown', token: 'match-unknown' },
};

export function getMatchStrengthDisplay(status) {
  return MATCH_STRENGTH_TOKENS[status] ?? MATCH_STRENGTH_TOKENS.UNKNOWN;
}
