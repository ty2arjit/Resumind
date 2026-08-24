import { Check, Loader2 } from 'lucide-react';
import { cn } from '../../../lib/cn';

/**
 * Multi-step progress indicator (spec §29) — e.g. "Parsing resume...",
 * "Understanding job description...", "Matching requirements...". Only
 * the component/state system; the full animated analysis flow is a
 * later phase.
 */
export default function ProgressState({ steps, currentIndex = 0 }) {
  return (
    <ol className="flex flex-col gap-3">
      {steps.map((step, index) => {
        const isDone = index < currentIndex;
        const isCurrent = index === currentIndex;
        return (
          <li key={step} className="flex items-center gap-3">
            <span
              className={cn(
                'flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-caption font-semibold',
                isDone && 'bg-success text-text-inverse',
                isCurrent && 'bg-primary text-text-inverse',
                !isDone && !isCurrent && 'bg-surface-muted text-text-muted'
              )}
            >
              {isDone ? <Check className="h-3.5 w-3.5" aria-hidden="true" /> : isCurrent ? <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" /> : index + 1}
            </span>
            <span className={cn('text-body-sm', isCurrent ? 'font-semibold text-text-primary' : 'text-text-secondary')}>{step}</span>
          </li>
        );
      })}
    </ol>
  );
}
