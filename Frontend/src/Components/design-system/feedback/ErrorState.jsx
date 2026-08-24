import { AlertTriangle } from 'lucide-react';
import Button from '../ui/Button';
import { cn } from '../../../lib/cn';

/** Reusable error presentation (spec §30) — clear, actionable,
 * non-technical. Never render a raw stack trace here. */
export default function ErrorState({ title = 'Something went wrong', description, onRetry, className }) {
  return (
    <div className={cn('flex flex-col items-center gap-3 rounded-lg border border-error/30 bg-error-surface px-6 py-10 text-center', className)}>
      <span className="rounded-full bg-error/10 p-3 text-error">
        <AlertTriangle className="h-6 w-6" aria-hidden="true" />
      </span>
      <div>
        <p className="text-body font-semibold text-text-primary">{title}</p>
        {description && <p className="mt-1 max-w-sm text-body-sm text-text-secondary">{description}</p>}
      </div>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}
