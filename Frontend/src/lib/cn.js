/** Tiny classnames joiner — no external dependency needed for this. */
export function cn(...values) {
  return values.flat().filter(Boolean).join(' ');
}
