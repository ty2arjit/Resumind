import { cn } from '../../../lib/cn';

/** Reusable empty state (spec §28): icon + title + short explanation +
 * optional CTA. Used for "no resumes", "no analyses", "no evidence", etc. */
export default function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div className={cn('flex flex-col items-center gap-3 rounded-lg border border-dashed border-border px-6 py-12 text-center', className)}>
      {Icon && (
        <span className="rounded-full bg-surface-muted p-3 text-text-muted">
          <Icon className="h-6 w-6" aria-hidden="true" />
        </span>
      )}
      <div>
        <p className="text-body font-semibold text-text-primary">{title}</p>
        {description && <p className="mt-1 max-w-sm text-body-sm text-text-secondary">{description}</p>}
      </div>
      {action}
    </div>
  );
}
