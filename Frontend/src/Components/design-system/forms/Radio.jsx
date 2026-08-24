import { cn } from '../../../lib/cn';

export default function Radio({ label, id, className, ...props }) {
  const inputId = id ?? `${props.name}-${props.value}`;
  return (
    <label htmlFor={inputId} className={cn('inline-flex cursor-pointer items-center gap-2 text-body-sm text-text-primary', className)}>
      <span className="relative inline-flex h-4 w-4 items-center justify-center">
        <input id={inputId} type="radio" className="peer absolute inset-0 h-4 w-4 cursor-pointer opacity-0" {...props} />
        <span className="pointer-events-none absolute inset-0 rounded-full border border-border-strong bg-surface peer-checked:border-primary peer-focus-visible:ring-2 peer-focus-visible:ring-primary/40" />
        <span className="pointer-events-none relative h-2 w-2 scale-0 rounded-full bg-primary transition-transform peer-checked:scale-100" />
      </span>
      {label}
    </label>
  );
}
