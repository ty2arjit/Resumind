import { Navigate } from 'react-router-dom';

/**
 * Route guard using the app's existing client-side auth flag
 * (App.jsx's isAuthenticated, set by Pages/Auth.jsx on login). Falls
 * back to checking the stored JWT so a page reload doesn't immediately
 * bounce an already-logged-in user — this is a minimal reload-survival
 * fix, not a new auth system.
 *
 * IMPORTANT: this is a UX convenience only, not a security boundary.
 * The real security boundary must be backend authorization on every
 * API call (spec Phase 12 §44) — see this phase's final report for why
 * that isn't fully wired yet (Backend/Models/db.js and user.js are
 * absent from the working tree, so the Node auth backend cannot
 * currently issue/verify real sessions in this environment).
 */
export default function RequireAuth({ isAuthenticated, children }) {
  const hasStoredToken = Boolean(localStorage.getItem('resumindToken'));
  if (!isAuthenticated && !hasStoredToken) {
    return <Navigate to="/auth" replace />;
  }
  return children;
}
