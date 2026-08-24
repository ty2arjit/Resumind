/**
 * Restrained Resumind brand mark (frontendReadme §34) — a simple
 * typographic wordmark with an abstract "R" glyph. Deliberately not a
 * robot/sparkle/brain icon; the mark connects to documents and
 * precision rather than "generic AI."
 */
export default function Wordmark({ className = '' }) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <span
        className="flex h-6 w-6 items-center justify-center rounded-[6px] font-mono text-[13px] font-semibold text-text-inverse"
        style={{ backgroundColor: 'var(--color-primary)' }}
        aria-hidden="true"
      >
        R
      </span>
      <span className="font-display text-body-lg font-semibold tracking-tight text-text-primary">Resumind</span>
    </span>
  );
}
