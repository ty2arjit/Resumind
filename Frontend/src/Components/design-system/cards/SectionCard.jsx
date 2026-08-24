import BaseCard from './BaseCard';
import { cn } from '../../../lib/cn';

/** A titled content group with generous whitespace (spec §13, §17) —
 * the standard wrapper for a labeled block of the future dashboard. */
export default function SectionCard({ title, description, action, className, children }) {
  return (
    <BaseCard className={cn('flex flex-col gap-4', className)}>
      {(title || action) && (
        <div className="flex items-start justify-between gap-3">
          <div>
            {title && <h3 className="text-h4 font-semibold text-text-primary">{title}</h3>}
            {description && <p className="mt-0.5 text-body-sm text-text-secondary">{description}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </BaseCard>
  );
}
