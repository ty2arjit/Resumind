import { Loader2 } from 'lucide-react';
import { cn } from '../../../lib/cn';

const VARIANTS = {
  primary: 'bg-primary text-text-inverse hover:bg-primary-hover disabled:bg-primary/50',
  secondary: 'bg-secondary text-text-inverse hover:bg-secondary-hover disabled:bg-secondary/50',
  tertiary: 'bg-transparent text-text-primary hover:bg-surface-muted disabled:text-text-muted',
  destructive: 'bg-error text-text-inverse hover:brightness-90 disabled:bg-error/50',
};

const SIZES = {
  sm: 'h-8 px-3 text-body-sm gap-1.5',
  md: 'h-10 px-4 text-body gap-2',
  lg: 'h-12 px-6 text-body-lg gap-2',
};

/**
 * Button system (spec §18): primary/secondary/tertiary/destructive,
 * consistent height/radius/typography, with default/hover/active/focus/
 * disabled/loading states.
 */
export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon: Icon,
  className,
  children,
  ...props
}) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-md font-display font-medium tracking-tight transition-colors',
        'active:scale-[0.98] disabled:cursor-not-allowed disabled:active:scale-100',
        VARIANTS[variant],
        SIZES[size],
        className
      )}
      disabled={disabled || loading}
      aria-busy={loading}
      style={{ transitionDuration: 'var(--motion-fast)' }}
      {...props}
    >
      {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : Icon ? <Icon className="h-4 w-4" aria-hidden="true" /> : null}
      {children}
    </button>
  );
}
