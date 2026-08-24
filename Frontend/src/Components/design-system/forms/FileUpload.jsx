import { UploadCloud } from 'lucide-react';
import { cn } from '../../../lib/cn';

/** Drop-zone-styled file input (spec §19) — used for resume/JD uploads. */
export default function FileUpload({ label, helperText, error, fileName, id, className, ...props }) {
  const inputId = id ?? props.name;
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-label font-semibold text-text-secondary">
          {label}
        </label>
      )}
      <label
        htmlFor={inputId}
        className={cn(
          'flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-6 py-8 text-center transition-colors',
          error ? 'border-error bg-error-surface' : 'border-border-strong bg-surface-muted hover:border-primary hover:bg-primary/5',
          className
        )}
        style={{ transitionDuration: 'var(--motion-fast)' }}
      >
        <UploadCloud className="h-6 w-6 text-text-muted" aria-hidden="true" />
        <span className="text-body-sm font-medium text-text-primary">{fileName || 'Click to upload or drag and drop'}</span>
        <input id={inputId} type="file" className="sr-only" {...props} />
      </label>
      {(helperText || error) && <p className={cn('text-caption', error ? 'text-error' : 'text-text-muted')}>{error || helperText}</p>}
    </div>
  );
}
