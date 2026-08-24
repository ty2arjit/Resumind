import { cn } from '../../../lib/cn';

const SHADOWS = {
  none: 'shadow-none',
  subtle: 'shadow-subtle',
  medium: 'shadow-medium',
  elevated: 'shadow-elevated',
};

/**
 * BaseCard (spec §17) — the single foundation every other card variant
 * builds on, so padding/border/radius/typography/hover stay consistent
 * everywhere. Do not create one-off card styles; extend this instead.
 */
export default function BaseCard({ as: Component = 'div', shadow = 'subtle', hoverable = false, className, children, ...props }) {
  return (
    <Component
      className={cn(
        'rounded-lg border border-border bg-surface p-6',
        SHADOWS[shadow],
        hoverable && 'transition-shadow hover:shadow-medium',
        className
      )}
      style={hoverable ? { transitionDuration: 'var(--motion-base)' } : undefined}
      {...props}
    >
      {children}
    </Component>
  );
}
