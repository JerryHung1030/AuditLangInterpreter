import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';
import ScriptManagement from './components/ManagementPage/ScriptManagement';
import ExecuteScripts from './components/ManagementPage/ExecuteScripts';
import PrototypePage from './components/PrototypePage/PrototypePage';
import 'tailwindcss/tailwind.css';
import 'tw-elements/css/tw-elements.min.css';
import './assets/fonts.css'; // Ensure fonts are imported
import './App.css'; // Import custom styles
import logo from './assets/logo.png'; // Import image

const App = () => {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-gray-900 text-white" style={{ fontFamily: 'MonoLisa' }}>
        {/* Header with transparent menu background */}
        <header className="bg-transparent text-white p-4 flex justify-between items-center shadow-lg">
          <div className="flex items-center">
            <img src={logo} alt="Logo" className="h-12 w-auto mr-3" />
            {/* HOME button with hover effects */}
            <Link
              to="/"
              className="text-blue-200 px-4 py-2 rounded transition duration-300 transform hover:bg-yellow-300 hover:text-black hover:scale-110"
              style={{ fontFamily: 'MonoLisa' }}
            >
              SecAuditRuleEngine+
            </Link>
          </div>
          <nav className="flex space-x-4" style={{ fontFamily: 'MonoLisa' }}>
            <Link to="/script-management" className="text-blue-200 px-4 py-2 rounded transition duration-300 transform hover:bg-yellow-300 hover:text-black hover:scale-110">
              Script Management
            </Link>
            <Link to="/execute-scripts" className="text-blue-200 px-4 py-2 rounded transition duration-300 transform hover:bg-yellow-300 hover:text-black hover:scale-110">
              Project Management
            </Link>
          </nav>
        </header>
        <main className="flex-1 p-6 bg-gray-900"> {/* Set background color to dark gray */}
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/script-management" element={<ScriptManagement />} />
            <Route path="/execute-scripts" element={<ExecuteScripts />} />
            <Route path="/prototype" element={<PrototypePage />} /> {/* New Prototype Route */}
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
