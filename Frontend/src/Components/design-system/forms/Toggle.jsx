import { cn } from '../../../lib/cn';

export default function Toggle({ label, id, className, ...props }) {
  const inputId = id ?? props.name;
  return (
    <label htmlFor={inputId} className={cn('inline-flex cursor-pointer items-center gap-2.5 text-body-sm text-text-primary', className)}>
      <span className="relative inline-flex h-5 w-9 shrink-0 items-center">
        <input id={inputId} type="checkbox" className="peer absolute inset-0 opacity-0" {...props} />
        <span className="pointer-events-none absolute inset-0 rounded-full bg-border-strong transition-colors peer-checked:bg-primary peer-focus-visible:ring-2 peer-focus-visible:ring-primary/40" style={{ transitionDuration: 'var(--motion-base)' }} />
        <span
          className="pointer-events-none relative h-4 w-4 translate-x-0.5 rounded-full bg-surface shadow-subtle transition-transform peer-checked:translate-x-4"
          style={{ transitionDuration: 'var(--motion-base)' }}
        />
      </span>
      {label}
    </label>
  );
}
