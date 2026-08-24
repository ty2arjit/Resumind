import { cn } from '../../../lib/cn';

/** A single sidebar navigation entry (frontendReadme §15) — quiet and
 * neutral by default; the active state is a soft brand tint plus a thin
 * accent rule, not a large colorful block. Icon + label always paired. */
export default function NavItem({ icon: Icon, label, active = false, badge, className, ...props }) {
  return (
    <button
      type="button"
      aria-current={active ? 'page' : undefined}
      className={cn(
        'relative flex w-full items-center gap-2.5 rounded-md px-3 py-2 text-body-sm font-display font-medium transition-colors',
        active ? 'text-primary' : 'text-text-secondary hover:bg-surface-muted hover:text-text-primary',
        className
      )}
      style={{ transitionDuration: 'var(--motion-fast)', backgroundColor: active ? 'var(--color-soft-brand)' : undefined }}
      {...props}
    >
      {active && <span className="absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full bg-primary" aria-hidden="true" />}
      {Icon && <Icon className="h-[18px] w-[18px] shrink-0" strokeWidth={1.75} aria-hidden="true" />}
      <span className="flex-1 text-left">{label}</span>
      {badge != null && (
        <span className="rounded-full bg-primary/15 px-1.5 py-0.5 font-mono text-caption font-medium text-primary">{badge}</span>
      )}
    </button>
  );
}
