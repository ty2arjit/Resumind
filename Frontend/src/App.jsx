import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/navbar';
import Home from './Pages/Home';
import Contact from './Pages/ContactPage';
import Help from './Pages/HelpPage';
import Auth from './Pages/Auth';
import Footer from './components/Footer';
import MainPage from './Pages/AnalysisPage';
import ResultPage from './Pages/Result';
function App() {
  const [isAuthenticated,setAuthenticated] = useState(false);
  return (
    <Router> {/* ✅ Correctly using BrowserRouter */}
      <div>
        <Navbar isAuthenticated={isAuthenticated} setAuthenticated={setAuthenticated}/>
        <Routes>
          <Route path='/' element={<Home />} />
          {<Route path='/contact' element={<Contact />} />}
          {<Route path='/help' element={<Help />} />}
          <Route path='/auth' element={<Auth setAuthenticated={setAuthenticated}/>} />
          {<Route path='/analyse' element={<MainPage />} />}
          {<Route path="/result" element={<ResultPage />} />}
          {/*<Route path='/profile' element={<ProfileDashboard />} /> */}
        </Routes>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
