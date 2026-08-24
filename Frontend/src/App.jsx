import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './Components/Navbar';
import Home from './Pages/Home';
import Contact from './Pages/ContactPage';
import Help from './Pages/HelpPage';
import Auth from './Pages/Auth';
import Footer from './Components/Footer';
import MainPage from './Pages/AnalysisPage';
import ResultPage from './Pages/Result';
import DesignSystemPage from './Pages/DesignSystemPage';
import DashboardPage from './Pages/app/DashboardPage';
import ResumesPage from './Pages/app/ResumesPage';
import JobDescriptionsPage from './Pages/app/JobDescriptionsPage';
import TargetProfilesPage from './Pages/app/TargetProfilesPage';
import AnalysisNewPage from './Pages/app/AnalysisNewPage';
import AnalysisResultPage from './Pages/app/AnalysisResultPage';
import HistoryPage from './Pages/app/HistoryPage';
import SettingsPage from './Pages/app/SettingsPage';
import AppShell from './Components/app-shell/AppShell';
import RequireAuth from './Components/app-shell/RequireAuth';
import { AppDataProvider } from './lib/AppDataContext';

const APP_ROUTE_PREFIXES = ['/dashboard', '/resumes', '/job-descriptions', '/target-profiles', '/analyses', '/history', '/settings'];

function isAppRoute(pathname) {
  return APP_ROUTE_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

function AppPage({ isAuthenticated, children }) {
  return (
    <RequireAuth isAuthenticated={isAuthenticated}>
      <AppShell>{children}</AppShell>
    </RequireAuth>
  );
}

function AppRoutes({ isAuthenticated, setAuthenticated }) {
  const location = useLocation();
  const showMarketingChrome = !isAppRoute(location.pathname);

  return (
    <div>
      {showMarketingChrome && <Navbar isAuthenticated={isAuthenticated} setAuthenticated={setAuthenticated} />}
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/contact' element={<Contact />} />
        <Route path='/help' element={<Help />} />
        <Route path='/auth' element={<Auth setAuthenticated={setAuthenticated} />} />
        <Route path='/analyse' element={<MainPage />} />
        <Route path="/result" element={<ResultPage />} />
        <Route path='/design-system' element={<DesignSystemPage />} />

        <Route path='/dashboard' element={<AppPage isAuthenticated={isAuthenticated}><DashboardPage /></AppPage>} />
        <Route path='/resumes' element={<AppPage isAuthenticated={isAuthenticated}><ResumesPage /></AppPage>} />
        <Route path='/job-descriptions' element={<AppPage isAuthenticated={isAuthenticated}><JobDescriptionsPage /></AppPage>} />
        <Route path='/target-profiles' element={<AppPage isAuthenticated={isAuthenticated}><TargetProfilesPage /></AppPage>} />
        <Route path='/analyses/new' element={<AppPage isAuthenticated={isAuthenticated}><AnalysisNewPage /></AppPage>} />
        <Route path='/analyses/result' element={<AppPage isAuthenticated={isAuthenticated}><AnalysisResultPage /></AppPage>} />
        <Route path='/history' element={<AppPage isAuthenticated={isAuthenticated}><HistoryPage /></AppPage>} />
        <Route path='/settings' element={<AppPage isAuthenticated={isAuthenticated}><SettingsPage /></AppPage>} />
      </Routes>
      {showMarketingChrome && <Footer />}
    </div>
  );
}

function App() {
  const [isAuthenticated, setAuthenticated] = useState(false);
  return (
    <Router>
      <AppDataProvider>
        <AppRoutes isAuthenticated={isAuthenticated} setAuthenticated={setAuthenticated} />
      </AppDataProvider>
    </Router>
  );
}

export default App;
