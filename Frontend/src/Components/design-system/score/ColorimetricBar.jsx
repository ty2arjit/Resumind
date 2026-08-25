import { motion } from 'framer-motion';
import { colorimetricColor } from '../../../lib/colorimetric';

/** A single "Label   value/max" row with a colorimetric-tinted fill —
 * the section-wise breakdown for the legacy Gemini result page. */
export default function ColorimetricBar({ label, value, max }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  const color = colorimetricColor(pct);

  return (
    <div className="flex items-center gap-4">
      <span className="w-44 shrink-0 truncate text-body-sm text-text-secondary">{label}</span>
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-muted">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          whileInView={{ width: `${pct}%` }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
      <span className="w-14 shrink-0 text-right font-mono text-body-sm font-medium text-text-primary">
        {value}/{max}
      </span>
    </div>
  );
}
