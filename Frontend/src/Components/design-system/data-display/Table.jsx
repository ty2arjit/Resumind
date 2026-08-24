import { cn } from '../../../lib/cn';
import EmptyState from '../feedback/EmptyState';
import Skeleton from '../feedback/Skeleton';

/**
 * Reusable table primitives (spec §27): header, row, hover, selected,
 * empty, loading, pagination. Prepared for future analysis history /
 * requirement lists / target profile / resume version tables — no
 * complete table is built in this phase.
 */
export function Table({ className, children }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className={cn('w-full border-collapse text-body-sm', className)}>{children}</table>
    </div>
  );
}

export function TableHead({ children }) {
  return <thead className="border-b border-border bg-surface-muted">{children}</thead>;
}

export function TableHeaderCell({ children, className }) {
  return (
    <th className={cn('px-4 py-3 text-left text-caption font-semibold uppercase tracking-wide text-text-muted', className)}>
      {children}
    </th>
  );
}

export function TableBody({ children }) {
  return <tbody className="divide-y divide-border">{children}</tbody>;
}

export function TableRow({ selected = false, className, children, ...props }) {
  return (
    <tr
      className={cn('transition-colors hover:bg-surface-muted', selected && 'bg-primary/5', className)}
      style={{ transitionDuration: 'var(--motion-fast)' }}
      {...props}
    >
      {children}
    </tr>
  );
}

export function TableCell({ children, className }) {
  return <td className={cn('px-4 py-3 text-text-primary', className)}>{children}</td>;
}

export function TableEmpty({ colSpan, title = 'No data yet', description }) {
  return (
    <tr>
      <td colSpan={colSpan} className="p-0">
        <EmptyState title={title} description={description} className="border-none" />
      </td>
    </tr>
  );
}

export function TableLoading({ colSpan, rows = 3 }) {
  return Array.from({ length: rows }).map((_, i) => (
    <tr key={i}>
      <td colSpan={colSpan} className="px-4 py-3">
        <Skeleton className="h-4 w-full" />
      </td>
    </tr>
  ));
}

export function TablePagination({ page, pageCount, onPageChange }) {
  return (
    <div className="flex items-center justify-between border-t border-border px-4 py-3 text-body-sm text-text-secondary">
      <span>
        Page {page} of {pageCount}
      </span>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => onPageChange?.(page - 1)}
          className="rounded-md px-2 py-1 hover:bg-surface-muted disabled:cursor-not-allowed disabled:opacity-40"
        >
          Previous
        </button>
        <button
          type="button"
          disabled={page >= pageCount}
          onClick={() => onPageChange?.(page + 1)}
          className="rounded-md px-2 py-1 hover:bg-surface-muted disabled:cursor-not-allowed disabled:opacity-40"
        >
          Next
        </button>
      </div>
    </div>
  );
}
