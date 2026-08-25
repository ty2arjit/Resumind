import { motion } from 'framer-motion';

/**
 * Consistent scroll-triggered reveal (fast, subtle, purposeful —
 * frontendReadme §29) used across pages instead of a single blanket
 * page-load fade. `delay` staggers sibling reveals.
 */
export default function Reveal({ children, delay = 0, y = 16, className, as = 'div' }) {
  const Component = motion[as] ?? motion.div;
  return (
    <Component
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </Component>
  );
}
