import { Check } from 'lucide-react';
import { cn } from '../../../lib/cn';

export default function Checkbox({ label, id, className, ...props }) {
  const inputId = id ?? props.name;
  return (
    <label htmlFor={inputId} className={cn('inline-flex cursor-pointer items-center gap-2 text-body-sm text-text-primary', className)}>
      <span className="relative inline-flex h-4 w-4 items-center justify-center">
        <input id={inputId} type="checkbox" className="peer absolute inset-0 h-4 w-4 cursor-pointer opacity-0" {...props} />
        <span className="pointer-events-none absolute inset-0 rounded border border-border-strong bg-surface peer-checked:border-primary peer-checked:bg-primary peer-focus-visible:ring-2 peer-focus-visible:ring-primary/40" />
        <Check className="pointer-events-none relative h-3 w-3 text-text-inverse opacity-0 peer-checked:opacity-100" aria-hidden="true" />
      </span>
      {label}
    </label>
  );
}
