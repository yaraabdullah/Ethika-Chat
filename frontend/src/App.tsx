import React, { useState, useEffect } from 'react';
import './App.css';
import SearchTab from './components/SearchTab';
import PromptGenerator from './components/PromptGenerator';

function App() {
  const [activeTab, setActiveTab] = useState<'search' | 'prompt'>('prompt');
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    checkInitialization();
  }, []);

  const checkInitialization = async () => {
    try {
      // Try /api/health first, fallback to /health for compatibility
      let response = await fetch('/api/health');
      if (!response.ok) {
        response = await fetch('/health');
      }
      if (response.ok) {
        const data = await response.json();
        setIsInitialized(true);
      } else {
        console.error('Health check failed:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Backend not available:', error);
    }
  };

  const handleInitialize = async () => {
    setIsLoading(true);
    try {
      // Try /api/health first, fallback to /health for compatibility
      let response = await fetch('/api/health');
      if (!response.ok) {
        response = await fetch('/health');
      }
      if (response.ok) {
        const data = await response.json();
        setIsInitialized(true);
      } else {
        const errorText = await response.text();
        alert(`Failed to connect to backend (${response.status}). The server may still be starting up. Please wait a moment and try again.\n\nError: ${errorText}`);
      }
    } catch (error: any) {
      alert(`Backend not available. The server may still be starting up. Please wait a moment and try again.\n\nError: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📚 Ethika Chat</h1>
        <p>RAG System for Educational Resources</p>
      </header>

      {!isInitialized ? (
        <div className="init-prompt">
          <div className="init-box">
            <h2>⚠️ Backend Not Connected</h2>
            <p>Please start the API server first:</p>
            <code>python3 api_server.py</code>
            <button onClick={handleInitialize} disabled={isLoading}>
              {isLoading ? 'Checking...' : 'Check Connection'}
            </button>
          </div>
        </div>
      ) : (
        <>
          <nav className="tabs">
            <button
              className={activeTab === 'prompt' ? 'active' : ''}
              onClick={() => setActiveTab('prompt')}
            >
              ✨ Generate Content
            </button>
            <button
              className={activeTab === 'search' ? 'active' : ''}
              onClick={() => setActiveTab('search')}
            >
              🔍 Search
            </button>
          </nav>

          <main className="content">
            {activeTab === 'prompt' && <PromptGenerator />}
            {activeTab === 'search' && <SearchTab />}
          </main>
        </>
      )}
    </div>
  );
}

export default App;
