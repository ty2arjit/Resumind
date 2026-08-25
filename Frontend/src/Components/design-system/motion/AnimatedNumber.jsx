import { useEffect, useRef } from 'react';
import { animate, useMotionValue, useTransform, motion } from 'framer-motion';

/**
 * Counts up to `value` when it first mounts/changes — used for score
 * reveals (ScoreHero, ScoreCard) so a result feels calculated rather
 * than just appearing. Respects prefers-reduced-motion.
 */
export default function AnimatedNumber({ value, className, duration = 1.1 }) {
  const motionValue = useMotionValue(0);
  const rounded = useTransform(motionValue, (v) => Math.round(v));
  const spanRef = useRef(null);
  const reducedMotion = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  useEffect(() => {
    if (reducedMotion) {
      motionValue.set(value);
      return;
    }
    const controls = animate(motionValue, value, { duration, ease: [0.16, 1, 0.3, 1] });
    return controls.stop;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  useEffect(() => rounded.on('change', (v) => {
    if (spanRef.current) spanRef.current.textContent = v;
  }), [rounded]);

  return (
    <motion.span ref={spanRef} className={className}>
      {reducedMotion ? value : 0}
    </motion.span>
  );
}
