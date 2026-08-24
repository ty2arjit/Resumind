import { SectionCard } from '../../Components/design-system';

/**
 * Settings (spec Phase 12 §34) — only sections the existing backend
 * actually supports. There is no preferences/theme/data-export API yet,
 * so only the real account info already stored in localStorage by the
 * existing auth flow (Pages/Auth.jsx) is shown, rather than fake toggles.
 */
export default function SettingsPage() {
  const user = JSON.parse(localStorage.getItem('resumindUser') || 'null');

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-h1 font-bold text-text-primary">Settings</h1>
        <p className="mt-1 text-body-lg text-text-secondary">Account information.</p>
      </header>

      <SectionCard title="Profile">
        {user ? (
          <dl className="grid grid-cols-2 gap-y-2 text-body-sm">
            <dt className="text-text-secondary">Name</dt>
            <dd className="text-text-primary">{user.name ?? '—'}</dd>
            <dt className="text-text-secondary">Email</dt>
            <dd className="text-text-primary">{user.email ?? '—'}</dd>
          </dl>
        ) : (
          <p className="text-body-sm text-text-secondary">No account information available.</p>
        )}
      </SectionCard>
    </div>
  );
}
