import BaseCard from './BaseCard';
import { cn } from '../../../lib/cn';

/** A single labeled metric/stat (spec §17) — for dashboard summary tiles. */
export default function MetricCard({ label, value, trend, icon: Icon, className }) {
  return (
    <BaseCard className={cn('flex items-start justify-between', className)}>
      <div>
        <p className="text-body-sm font-medium text-text-secondary">{label}</p>
        <p className="mt-1 text-h2 font-bold tabular-nums text-text-primary">{value}</p>
        {trend && (
          <p className={cn('mt-1 text-caption font-semibold', trend.direction === 'up' ? 'text-success' : trend.direction === 'down' ? 'text-error' : 'text-text-muted')}>
            {trend.label}
          </p>
        )}
      </div>
      {Icon && (
        <span className="rounded-md bg-primary/10 p-2 text-primary">
          <Icon className="h-5 w-5" aria-hidden="true" />
        </span>
      )}
    </BaseCard>
  );
}
