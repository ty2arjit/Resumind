import { Search } from 'lucide-react';
import { cn } from '../../../lib/cn';

export default function SearchInput({ className, ...props }) {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" aria-hidden="true" />
      <input
        type="search"
        className={cn(
          'h-10 w-full rounded-md border border-border bg-surface pl-9 pr-3 text-body text-text-primary placeholder:text-text-muted',
          'transition-colors focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/40',
          className
        )}
        style={{ transitionDuration: 'var(--motion-fast)' }}
        {...props}
      />
    </div>
  );
}
