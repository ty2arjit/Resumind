import { cn } from '../../../lib/cn';

const VARIANTS = {
  primary: 'bg-primary text-text-inverse hover:bg-primary-hover',
  ghost: 'bg-transparent text-text-secondary hover:bg-surface-muted hover:text-text-primary',
};

/** Icon-only button (spec §18). Always requires an accessible label since
 * there is no visible text. */
export default function IconButton({ icon: Icon, label, variant = 'ghost', size = 'md', className, ...props }) {
  const boxSize = size === 'sm' ? 'h-8 w-8' : size === 'lg' ? 'h-12 w-12' : 'h-10 w-10';
  const iconSize = size === 'sm' ? 'h-4 w-4' : 'h-5 w-5';

  return (
    <button
      aria-label={label}
      title={label}
      className={cn(
        'inline-flex items-center justify-center rounded-md transition-colors disabled:cursor-not-allowed disabled:opacity-50',
        boxSize,
        VARIANTS[variant],
        className
      )}
      style={{ transitionDuration: 'var(--motion-fast)' }}
      {...props}
    >
      <Icon className={iconSize} aria-hidden="true" />
    </button>
  );
}
