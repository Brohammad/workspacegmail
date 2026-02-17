import { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import MetricsDashboard from './components/MetricsDashboard';
import './App.css';

interface Metrics {
  total_queries: number;
  avg_spec_accuracy: number;
  avg_pricing_accuracy: number;
  avg_hallucination_check: number;
  avg_overall_score: number;
}

function App() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');

  // Check backend health on mount
  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(() => setHealthStatus('healthy'))
      .catch(() => setHealthStatus('unhealthy'));
  }, []);

  // Fetch metrics
  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  useEffect(() => {
    fetchMetrics();
    // Refresh metrics every 5 seconds
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🤖</span>
            <h1>ZenBot</h1>
          </div>
          <p className="tagline">AI-Powered Steel Specifications Assistant</p>
          <div className={`status-badge ${healthStatus}`}>
            <span className="status-dot"></span>
            {healthStatus === 'checking' && 'Connecting...'}
            {healthStatus === 'healthy' && 'Online'}
            {healthStatus === 'unhealthy' && 'Offline'}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="content-grid">
          {/* Chat Section */}
          <section className="chat-section">
            <ChatInterface onMessageSent={fetchMetrics} />
          </section>

          {/* Metrics Section */}
          <aside className="metrics-section">
            <MetricsDashboard metrics={metrics} />
          </aside>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Powered by Google Gemini 2.0 Flash • LangSmith Tracing • FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
