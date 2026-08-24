import { ChevronDown } from 'lucide-react';
import { cn } from '../../../lib/cn';

export default function Select({ label, helperText, error, id, className, children, ...props }) {
  const inputId = id ?? props.name;
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-label font-semibold text-text-secondary">
          {label}
        </label>
      )}
      <div className="relative">
        <select
          id={inputId}
          aria-invalid={Boolean(error)}
          className={cn(
            'h-10 w-full appearance-none rounded-md border bg-surface px-3 pr-9 text-body text-text-primary',
            'transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40',
            error ? 'border-error' : 'border-border focus:border-primary',
            'disabled:cursor-not-allowed disabled:bg-surface-muted disabled:text-text-muted',
            className
          )}
          style={{ transitionDuration: 'var(--motion-fast)' }}
          {...props}
        >
          {children}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" aria-hidden="true" />
      </div>
      {(helperText || error) && <p className={cn('text-caption', error ? 'text-error' : 'text-text-muted')}>{error || helperText}</p>}
    </div>
  );
}
