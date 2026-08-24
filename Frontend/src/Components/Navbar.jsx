import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, User, X } from 'lucide-react';
import Wordmark from './design-system/navigation/Wordmark';
import { Button, IconButton } from './design-system';

const NAV_ITEMS = [
  { name: 'Home', href: '/' },
  { name: 'Contact Us', href: '/contact' },
  { name: 'Help', href: '/help' },
];

/** Public marketing navbar — same quiet, editorial visual language as
 * the authenticated app shell (Components/app-shell/AppShell.jsx), just
 * as a top bar instead of a sidebar. */
function Navbar({ isAuthenticated, setAuthenticated }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  const handleLogout = () => {
    setAuthenticated(false);
    localStorage.removeItem('resumindToken');
    localStorage.removeItem('resumindUser');
  };

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-surface/95 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 md:px-8">
        <Link to="/">
          <Wordmark />
        </Link>

        <ul className="hidden items-center gap-1 md:flex">
          {NAV_ITEMS.map((item) => (
            <li key={item.href}>
              <Link
                to={item.href}
                className={`rounded-md px-3 py-2 text-body-sm font-medium transition-colors ${
                  location.pathname === item.href ? 'text-primary' : 'text-text-secondary hover:text-text-primary'
                }`}
                style={{ transitionDuration: 'var(--motion-fast)' }}
              >
                {item.name}
              </Link>
            </li>
          ))}
        </ul>

        <div className="hidden items-center gap-2 md:flex">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="rounded-md p-2 text-text-secondary hover:text-text-primary" aria-label="Dashboard">
                <User className="h-[18px] w-[18px]" strokeWidth={1.75} />
              </Link>
              <Button variant="tertiary" size="sm" onClick={handleLogout}>
                Log out
              </Button>
            </>
          ) : (
            <Link to="/auth">
              <Button size="sm">Log in</Button>
            </Link>
          )}
        </div>

        <IconButton icon={menuOpen ? X : Menu} label="Toggle menu" className="md:hidden" onClick={() => setMenuOpen((v) => !v)} />
      </nav>

      {menuOpen && (
        <div className="border-t border-border bg-surface px-4 py-3 md:hidden">
          <ul className="flex flex-col gap-1">
            {NAV_ITEMS.map((item) => (
              <li key={item.href}>
                <Link
                  to={item.href}
                  onClick={() => setMenuOpen(false)}
                  className="block rounded-md px-3 py-2 text-body-sm font-medium text-text-secondary hover:bg-surface-muted hover:text-text-primary"
                >
                  {item.name}
                </Link>
              </li>
            ))}
          </ul>
          <div className="mt-2 border-t border-border-subtle pt-2">
            {isAuthenticated ? (
              <Button variant="tertiary" size="sm" onClick={handleLogout} className="w-full justify-start">
                Log out
              </Button>
            ) : (
              <Link to="/auth" onClick={() => setMenuOpen(false)}>
                <Button size="sm" className="w-full">
                  Log in
                </Button>
              </Link>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

export default Navbar;
