import { createContext, useContext, useMemo, useState } from 'react';

/**
 * In-memory, single-session working state shared across the app shell's
 * pages (active resume/JD/last analysis). This is deliberately NOT a
 * substitute for backend persistence — Backend/fastapi_app has no
 * resume/JD/analysis storage yet (see Phase 12's final report), so
 * there is nothing to list, rename, or fetch by id. This context only
 * avoids re-uploading the same file across pages within one browser
 * session; it holds zero fake/invented data, only what a real API call
 * actually returned.
 */
const AppDataContext = createContext(null);

export function AppDataProvider({ children }) {
  const [activeResume, setActiveResume] = useState(null); // { file, parsed }
  const [activeJobDescription, setActiveJobDescription] = useState(null); // { file, text, parsed }
  const [lastAnalysis, setLastAnalysis] = useState(null);

  const value = useMemo(
    () => ({ activeResume, setActiveResume, activeJobDescription, setActiveJobDescription, lastAnalysis, setLastAnalysis }),
    [activeResume, activeJobDescription, lastAnalysis]
  );

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}

export function useAppData() {
  const context = useContext(AppDataContext);
  if (!context) throw new Error('useAppData must be used within AppDataProvider');
  return context;
}
