import { cn } from '../../../lib/cn';

/** Text input (spec §19) with label, helper text, and error state. */
export default function Input({ label, helperText, error, id, className, ...props }) {
  const inputId = id ?? props.name;
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-label font-semibold text-text-secondary">
          {label}
        </label>
      )}
      <input
        id={inputId}
        aria-invalid={Boolean(error)}
        aria-describedby={helperText || error ? `${inputId}-helper` : undefined}
        className={cn(
          'h-10 rounded-md border bg-surface px-3 text-body text-text-primary placeholder:text-text-muted',
          'transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40',
          error ? 'border-error' : 'border-border focus:border-primary',
          'disabled:cursor-not-allowed disabled:bg-surface-muted disabled:text-text-muted',
          className
        )}
        style={{ transitionDuration: 'var(--motion-fast)' }}
        {...props}
      />
      {(helperText || error) && (
        <p id={`${inputId}-helper`} className={cn('text-caption', error ? 'text-error' : 'text-text-muted')}>
          {error || helperText}
        </p>
      )}
    </div>
  );
}
