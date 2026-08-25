import { useEffect, useRef } from 'react';

const EASE_OUT_EXPO = (t) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t));

/**
 * Counts up to `value` when it first mounts/changes — used for score
 * reveals (ScoreHero, ScoreCard, ColorimetricMeter) so a result feels
 * calculated rather than just appearing. Respects prefers-reduced-motion.
 *
 * A plain requestAnimationFrame tween, not framer-motion's imperative
 * animate() — that call reliably produced zero onUpdate events in this
 * app's installed framer-motion version (verified directly: neither the
 * animate(from, to, opts) numeric overload nor animate(motionValue,
 * target, opts) + .on('change') ever fired), so this avoids that
 * dependency entirely rather than trying to work around it.
 */
export default function AnimatedNumber({ value, className, duration = 1.1 }) {
  const spanRef = useRef(null);

  useEffect(() => {
    if (!spanRef.current) return;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reducedMotion) {
      spanRef.current.textContent = value;
      return;
    }

    let frame;
    const start = performance.now();
    const durationMs = duration * 1000;

    const tick = (now) => {
      const elapsed = now - start;
      const t = Math.min(1, elapsed / durationMs);
      const current = Math.round(value * EASE_OUT_EXPO(t));
      if (spanRef.current) spanRef.current.textContent = current;
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return <span ref={spanRef} className={className} />;
}
