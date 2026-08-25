/**
 * Smooth (not bucketed) red -> amber -> teal color interpolation for the
 * Gemini-scored result page's "colorimetric" meter. Deliberately
 * separate from design-system/score/scoreStates.js, which uses discrete
 * MatchStrength buckets for the deterministic ATS pipeline — this is a
 * continuous gradient appropriate for a single qualitative 0-100 score.
 */
const STOPS = [
  { at: 0, rgb: [180, 35, 24] }, // error
  { at: 50, rgb: [184, 107, 0] }, // warning
  { at: 75, rgb: [8, 127, 117] }, // teal
  { at: 100, rgb: [6, 107, 98] }, // deep teal
];

function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function colorimetricColor(score) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  let lower = STOPS[0];
  let upper = STOPS[STOPS.length - 1];
  for (let i = 0; i < STOPS.length - 1; i++) {
    if (clamped >= STOPS[i].at && clamped <= STOPS[i + 1].at) {
      lower = STOPS[i];
      upper = STOPS[i + 1];
      break;
    }
  }
  const range = upper.at - lower.at || 1;
  const t = (clamped - lower.at) / range;
  const rgb = lower.rgb.map((c, i) => Math.round(lerp(c, upper.rgb[i], t)));
  return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
}

export function colorimetricLabel(score) {
  const clamped = score ?? 0;
  if (clamped >= 85) return 'Excellent';
  if (clamped >= 70) return 'Strong';
  if (clamped >= 50) return 'Developing';
  if (clamped >= 30) return 'Needs work';
  return 'Early stage';
}
