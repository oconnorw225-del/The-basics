import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import SystemStatusPanel from './components/SystemStatusPanel';
import TradingControlPanel from './components/TradingControlPanel';
import AIControlPanel from './components/AIControlPanel';
import AWSControlPanel from './components/AWSControlPanel';
import SystemManagementPanel from './components/SystemManagementPanel';
import MonitoringPanel from './components/MonitoringPanel';
import ConfigurationPanel from './components/ConfigurationPanel';
import websocketService from './services/websocket';

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    websocketService.connect();

    // Subscribe to status updates
    websocketService.subscribe('status', (message) => {
      console.log('Status update:', message);
    });

    return () => {
      websocketService.disconnect();
    };
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-900 transition-colors duration-200">
      {/* Header */}
      <header className="bg-white dark:bg-dark-800 shadow-md border-b border-gray-200 dark:border-dark-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Production Control Dashboard
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                The Basics - Comprehensive System Management
              </p>
            </div>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg bg-gray-200 dark:bg-dark-700 hover:bg-gray-300 dark:hover:bg-dark-600 transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? (
                <Sun className="w-5 h-5 text-yellow-500" />
              ) : (
                <Moon className="w-5 h-5 text-gray-700" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* System Status Panel - Full Width at Top */}
        <SystemStatusPanel />

        {/* Control Panels Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Trading Control Panel */}
          <TradingControlPanel />

          {/* AI/Freelance Control Panel */}
          <AIControlPanel />

          {/* AWS Deployment Panel */}
          <AWSControlPanel />

          {/* System Management Panel */}
          <SystemManagementPanel />

          {/* Monitoring Panel */}
          <MonitoringPanel />

          {/* Configuration Panel */}
          <ConfigurationPanel />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-dark-800 border-t border-gray-200 dark:border-dark-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            © 2024 The Basics - Production Control Dashboard v1.0.0
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
