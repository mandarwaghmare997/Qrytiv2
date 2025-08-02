import React, { useState, useEffect } from 'react';
import './App.css';
import apiService from './services/api.js';
import config from './config.js';
import AIModelRegistry from './components/AIModelRegistry.jsx';
import './components/AIModelRegistry.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [apiStatus, setApiStatus] = useState('checking');
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, ai-models

  // Login form state
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  });

  // Check API health and authentication status on mount
  useEffect(() => {
    checkApiHealth();
    checkAuthStatus();
  }, []);

  const checkApiHealth = async () => {
    try {
      await apiService.healthCheck();
      setApiStatus('healthy');
    } catch (error) {
      setApiStatus('error');
      console.error('API health check failed:', error);
    }
  };

  const checkAuthStatus = () => {
    const token = apiService.getToken();
    if (token) {
      setIsAuthenticated(true);
      // In a real app, you'd validate the token with the backend
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await apiService.login(loginForm.email, loginForm.password);
      setUser(response.user);
      setIsAuthenticated(true);
      setLoginForm({ email: '', password: '' });
    } catch (error) {
      setError(error.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    apiService.logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  // Login form component
  const LoginForm = () => (
    <div className="login-container">
      <div className="login-card">
        <h2>Login to Qrytiv2</h2>
        <p className="login-subtitle">ISO 42001 AI Governance Platform</p>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={loginForm.email}
              onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={loginForm.password}
              onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
              required
              disabled={loading}
            />
          </div>

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="forgot-password">
          <a href="#" className="forgot-link">Forgot Password?</a>
        </div>

        <div className="api-status">
          <span className={`status-indicator ${apiStatus}`}></span>
          API Status: {apiStatus === 'healthy' ? 'Connected' : apiStatus === 'error' ? 'Disconnected' : 'Checking...'}
        </div>
      </div>
    </div>
  );

  // Dashboard component
  const Dashboard = () => (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Qrytiv2 Dashboard</h1>
          <div className="user-info">
            <span>Welcome, {user?.full_name || 'User'}</span>
            <span className="user-role">({user?.role || 'user'})</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-grid">
          <div className="dashboard-card">
            <h3>ISO 42001 Compliance</h3>
            <p>Monitor your AI governance compliance status</p>
            <div className="compliance-score">
              <span className="score">85%</span>
              <span className="score-label">Compliance Score</span>
            </div>
          </div>

          <div className="dashboard-card clickable" onClick={() => setCurrentView('ai-models')}>
            <h3>AI Model Registry</h3>
            <p>Manage your AI models and their lifecycle</p>
            <div className="stat">
              <span className="stat-number">12</span>
              <span className="stat-label">Active Models</span>
            </div>
            <div className="card-action">
              <span>Click to manage →</span>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Risk Assessment</h3>
            <p>Identify and mitigate AI-related risks</p>
            <div className="stat">
              <span className="stat-number">3</span>
              <span className="stat-label">High Priority Items</span>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Audit Trail</h3>
            <p>Track all compliance activities and changes</p>
            <div className="stat">
              <span className="stat-number">247</span>
              <span className="stat-label">Recent Activities</span>
            </div>
          </div>
        </div>

        <div className="user-details">
          <h3>User Information</h3>
          <div className="user-details-grid">
            <div><strong>Email:</strong> {user?.email}</div>
            <div><strong>Role:</strong> {user?.role}</div>
            <div><strong>Organization:</strong> {user?.organization}</div>
          </div>
        </div>
      </main>
    </div>
  );

  const renderCurrentView = () => {
    if (!isAuthenticated) {
      return <LoginForm />;
    }

    switch (currentView) {
      case 'ai-models':
        return (
          <AIModelRegistry 
            user={user} 
            onBack={() => setCurrentView('dashboard')} 
          />
        );
      case 'dashboard':
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="App">
      {renderCurrentView()}
    </div>
  );
}

export default App;

