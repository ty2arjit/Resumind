import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../../lib/cn';

/** A single expandable row — the section-by-section resume analysis is
 * long-form paragraph text per section, so an accordion keeps the page
 * scannable instead of reading as one continuous wall of text. */
export function AccordionItem({ badge, badgeColor, title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-border-subtle last:border-none">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-3 py-4 text-left"
        aria-expanded={open}
      >
        {badge && (
          <span
            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full font-mono text-caption font-semibold"
            style={{ backgroundColor: `${badgeColor}1a`, color: badgeColor }}
          >
            {badge}
          </span>
        )}
        <span className="flex-1 text-body-sm font-medium text-text-primary">{title}</span>
        <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown className="h-4 w-4 text-text-muted" strokeWidth={2} />
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <p className="pb-4 pl-10 pr-2 text-body-sm text-text-secondary">{children}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function Accordion({ className, children }) {
  return <div className={cn('', className)}>{children}</div>;
}
