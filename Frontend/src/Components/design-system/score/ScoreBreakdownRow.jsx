import { motion } from 'framer-motion';
import { getScoreState } from './scoreStates';
import AnimatedNumber from '../motion/AnimatedNumber';

/**
 * A single category/dimension row — label, mono score number, and a
 * compact horizontal bar on one line (frontendReadme §12's example:
 * "Required Skills   91  ███████████░"). Used for score breakdowns
 * instead of a grid of separate ring charts. The bar fills and the
 * number counts up when it scrolls into view.
 */
export default function ScoreBreakdownRow({ label, score, weight }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const state = getScoreState(clamped);
  const color = `var(--color-${state.token})`;

  return (
    <div className="flex items-center gap-4">
      <span className="w-40 shrink-0 truncate text-body-sm text-text-secondary">{label}</span>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-muted">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          whileInView={{ width: `${clamped}%` }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
      <AnimatedNumber value={clamped} className="w-9 shrink-0 text-right font-mono text-body-sm font-medium text-text-primary" />
      {weight != null && <span className="w-12 shrink-0 text-right font-mono text-caption text-text-muted">{weight}%</span>}
    </div>
  );
}
