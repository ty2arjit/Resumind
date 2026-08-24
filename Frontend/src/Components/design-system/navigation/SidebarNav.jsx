import {
  ClipboardList,
  FileText,
  History,
  LayoutDashboard,
  Settings,
  Target,
} from 'lucide-react';
import NavItem from './NavItem';

/**
 * Reusable sidebar shell for the future dashboard (spec §24) — sections
 * only, no page content or routing wired here yet (that belongs to
 * Phase 12).
 */
export const DEFAULT_NAV_SECTIONS = [
  { key: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { key: 'resumes', label: 'My Resumes', icon: FileText },
  { key: 'analyses', label: 'Analyses', icon: ClipboardList },
  { key: 'target-profiles', label: 'Target Profiles', icon: Target },
  { key: 'history', label: 'History', icon: History },
  { key: 'settings', label: 'Settings', icon: Settings },
];

export default function SidebarNav({ activeKey, onSelect, sections = DEFAULT_NAV_SECTIONS }) {
  return (
    <nav aria-label="Primary" className="flex w-60 flex-col gap-1 border-r border-border bg-surface p-4">
      {sections.map((section) => (
        <NavItem
          key={section.key}
          icon={section.icon}
          label={section.label}
          active={section.key === activeKey}
          onClick={() => onSelect?.(section.key)}
        />
      ))}
    </nav>
  );
}
