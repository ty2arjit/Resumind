import { motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';
import { colorimetricColor, colorimetricLabel } from '../../../lib/colorimetric';
import AnimatedNumber from '../motion/AnimatedNumber';

const EASE_OUT_EXPO = (t) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t));

/**
 * A large radial "colorimetric" gauge — the stroke color interpolates
 * smoothly along a red -> amber -> teal gradient rather than snapping
 * between discrete buckets, which reads as more literally "measuring"
 * the score. Used for the legacy Gemini result page, which produces one
 * qualitative 0-100 score rather than the deterministic ATS pipeline's
 * category breakdown.
 *
 * The ring fill is a plain requestAnimationFrame tween (via React
 * state), not framer-motion's imperative animate() — verified directly
 * that call produces zero onUpdate/onComplete/.on('change') events with
 * this app's installed framer-motion version, so this avoids it rather
 * than fighting it (see AnimatedNumber.jsx for the same finding).
 */
export default function ColorimetricMeter({ score, size = 220 }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const color = colorimetricColor(clamped);
  const label = colorimetricLabel(clamped);
  const stroke = size * 0.07;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;

  const [progress, setProgress] = useState(0);
  const [ready, setReady] = useState(false);
  const frameRef = useRef();

  useEffect(() => {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reducedMotion) {
      setProgress(clamped);
      setReady(true);
      return;
    }

    const start = performance.now();
    const durationMs = 1300;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / durationMs);
      setProgress(clamped * EASE_OUT_EXPO(t));
      if (t < 1) {
        frameRef.current = requestAnimationFrame(tick);
      } else {
        setReady(true);
      }
    };
    frameRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clamped]);

  const dashOffset = circumference * (1 - progress / 100);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <motion.div
        className="absolute inset-0 rounded-full blur-2xl"
        style={{ backgroundColor: color, opacity: 0.18 }}
        animate={ready ? { opacity: [0.12, 0.22, 0.12] } : { opacity: 0.18 }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      />
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--color-border)" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <AnimatedNumber value={clamped} duration={1.3} className="font-mono text-score-lg font-semibold leading-none tracking-tight text-text-primary" />
        <span className="mt-2 text-caption font-semibold uppercase tracking-wider" style={{ color }}>
          {label}
        </span>
      </div>
    </div>
  );
}
