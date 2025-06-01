import { useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/navbar';
import Home from './Pages/Home';
import Contact from './Pages/ContactPage';
import Help from './Pages/HelpPage';
import Auth from './Pages/Auth';
function App() {
  const [isAuthenticated,setAuthenticated] = useState(false);
  return (
    <Router> {/* ✅ Correctly using BrowserRouter */}
      <div className="min-h-screen bg-gray-100 dark:bg-gray-800">
        <Navbar isAuthenticated={isAuthenticated} setAuthenticated={setAuthenticated}/>
        <Routes>
          <Route path='/' element={<Home />} />
          {<Route path='/contact' element={<Contact />} />}
          {<Route path='/help' element={<Help />} />}
          <Route path='/auth' element={<Auth setAuthenticated={setAuthenticated}/>} />
          {/* Future Routes */}
          {/* <Route path='/profile' element={<Profile />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
