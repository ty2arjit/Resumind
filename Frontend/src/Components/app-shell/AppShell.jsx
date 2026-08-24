import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, User, X } from 'lucide-react';
import { DEFAULT_NAV_SECTIONS, NavItem, IconButton, Wordmark } from '../design-system';

const ROUTES = {
  dashboard: '/dashboard',
  resumes: '/resumes',
  analyses: '/analyses/new',
  'target-profiles': '/target-profiles',
  history: '/history',
  settings: '/settings',
};

/**
 * Global application shell (frontendReadme §15) — a quiet, premium
 * sidebar (persistent on desktop, a drawer on mobile) and a minimal
 * header. Wraps every authenticated product page.
 */
export default function AppShell({ children }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const activeKey =
    Object.entries(ROUTES).find(([, path]) => location.pathname.startsWith(path.split('/new')[0]))?.[0] ?? 'dashboard';

  const goTo = (key) => {
    navigate(ROUTES[key] ?? '/dashboard');
    setDrawerOpen(false);
  };

  return (
    <div className="flex min-h-screen bg-background">
      <div className="hidden md:block">
        <nav aria-label="Primary" className="flex h-screen w-56 flex-col gap-0.5 border-r border-border bg-surface px-3 py-5">
          <Link to="/dashboard" className="mb-6 px-2">
            <Wordmark />
          </Link>
          {DEFAULT_NAV_SECTIONS.map((section) => (
            <NavItem key={section.key} icon={section.icon} label={section.label} active={section.key === activeKey} onClick={() => goTo(section.key)} />
          ))}
        </nav>
      </div>

      {drawerOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <button
            aria-label="Close navigation"
            className="absolute inset-0 bg-secondary/30 backdrop-blur-[2px]"
            onClick={() => setDrawerOpen(false)}
          />
          <nav aria-label="Primary" className="relative z-50 flex h-full w-64 flex-col gap-0.5 bg-surface p-4 shadow-elevated">
            <div className="mb-6 flex items-center justify-between px-2">
              <Wordmark />
              <IconButton icon={X} label="Close navigation" onClick={() => setDrawerOpen(false)} />
            </div>
            {DEFAULT_NAV_SECTIONS.map((section) => (
              <NavItem key={section.key} icon={section.icon} label={section.label} active={section.key === activeKey} onClick={() => goTo(section.key)} />
            ))}
          </nav>
        </div>
      )}

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-border bg-surface px-4 md:px-8">
          <IconButton icon={Menu} label="Open navigation" className="md:hidden" onClick={() => setDrawerOpen(true)} />
          <div className="md:hidden">
            <Wordmark />
          </div>
          <span className="hidden text-body-sm text-text-secondary md:block" />
          <span className="flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-body-sm text-text-secondary">
            <User className="h-[15px] w-[15px]" strokeWidth={1.75} aria-hidden="true" />
            Account
          </span>
        </header>
        <main className="flex-1 p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}
