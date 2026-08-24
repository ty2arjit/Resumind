import { Loader2 } from 'lucide-react';
import { cn } from '../../../lib/cn';

export default function Spinner({ size = 'md', label, className }) {
  const boxSize = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-8 w-8' : 'h-6 w-6';
  return (
    <div className={cn('inline-flex items-center gap-2 text-text-secondary', className)} role="status">
      <Loader2 className={cn('animate-spin', boxSize)} aria-hidden="true" />
      {label && <span className="text-body-sm">{label}</span>}
      {!label && <span className="sr-only">Loading</span>}
    </div>
  );
}
