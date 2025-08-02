import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

const AdminDashboard = ({ onNavigate }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [clientsProgress, setClientsProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
    fetchClientsProgress();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/admin/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchClientsProgress = async () => {
    try {
      const response = await fetch('/api/admin/clients/progress', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setClientsProgress(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching clients progress:', error);
      setLoading(false);
    }
  };

  const getRiskColor = (riskTemplate) => {
    switch (riskTemplate) {
      case 'high': return '#dc3545';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getComplianceColor = (score) => {
    if (score >= 90) return '#28a745';
    if (score >= 70) return '#ffc107';
    if (score >= 50) return '#fd7e14';
    return '#dc3545';
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'active': { color: '#28a745', text: 'Active' },
      'completed': { color: '#007bff', text: 'Completed' },
      'on_hold': { color: '#ffc107', text: 'On Hold' },
      'cancelled': { color: '#dc3545', text: 'Cancelled' }
    };
    
    const config = statusConfig[status] || { color: '#6c757d', text: status };
    
    return (
      <span 
        className="status-badge" 
        style={{ backgroundColor: config.color }}
      >
        {config.text}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <div className="header-actions">
          <button 
            className="btn btn-primary"
            onClick={() => onNavigate('create-user')}
          >
            + Create Client
          </button>
          <button 
            className="btn btn-secondary"
            onClick={() => onNavigate('create-project')}
          >
            + New Project
          </button>
        </div>
      </div>

      <div className="dashboard-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'clients' ? 'active' : ''}`}
          onClick={() => setActiveTab('clients')}
        >
          Client Progress
        </button>
        <button 
          className={`tab ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          Evidence Review
        </button>
        <button 
          className={`tab ${activeTab === 'certificates' ? 'active' : ''}`}
          onClick={() => setActiveTab('certificates')}
        >
          Certificates
        </button>
      </div>

      {activeTab === 'overview' && dashboardData && (
        <div className="overview-tab">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <div className="stat-content">
                <h3>{dashboardData.total_clients}</h3>
                <p>Total Clients</p>
                <small>{dashboardData.active_clients} active</small>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">📋</div>
              <div className="stat-content">
                <h3>{dashboardData.total_projects}</h3>
                <p>Total Projects</p>
                <small>{dashboardData.active_projects} active</small>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">✅</div>
              <div className="stat-content">
                <h3>{dashboardData.completed_projects}</h3>
                <p>Completed</p>
                <small>Projects finished</small>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">⚠️</div>
              <div className="stat-content">
                <h3>{dashboardData.high_risk_projects}</h3>
                <p>High Risk</p>
                <small>Projects requiring attention</small>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">🔍</div>
              <div className="stat-content">
                <h3>{dashboardData.projects_needing_attention}</h3>
                <p>Need Attention</p>
                <small>Low compliance scores</small>
              </div>
            </div>
          </div>

          <div className="recent-projects">
            <h2>Recent Projects</h2>
            <div className="projects-table">
              <table>
                <thead>
                  <tr>
                    <th>Project Name</th>
                    <th>Client</th>
                    <th>Risk Level</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.recent_projects.map(project => (
                    <tr key={project.id}>
                      <td>
                        <strong>{project.project_name}</strong>
                        {project.ai_system_name && (
                          <div className="ai-system">{project.ai_system_name}</div>
                        )}
                      </td>
                      <td>
                        <div>{project.client_name}</div>
                        <small>{project.client_organization}</small>
                      </td>
                      <td>
                        <span 
                          className="risk-badge"
                          style={{ backgroundColor: getRiskColor(project.risk_template) }}
                        >
                          {project.risk_template.toUpperCase()}
                        </span>
                      </td>
                      <td>{getStatusBadge(project.status)}</td>
                      <td>{new Date(project.created_at).toLocaleDateString()}</td>
                      <td>
                        <button 
                          className="btn btn-sm"
                          onClick={() => onNavigate('project-details', project.id)}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'clients' && (
        <div className="clients-tab">
          <div className="clients-header">
            <h2>Client Progress Overview</h2>
            <div className="filters">
              <select>
                <option value="">All Risk Levels</option>
                <option value="high">High Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="low">Low Risk</option>
              </select>
              <select>
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="on_hold">On Hold</option>
              </select>
            </div>
          </div>

          <div className="clients-grid">
            {clientsProgress.map(client => (
              <div key={`${client.client_id}-${client.project_id}`} className="client-card">
                <div className="client-header">
                  <div className="client-info">
                    <h3>{client.client_name}</h3>
                    <p>{client.organization}</p>
                    <small>{client.client_email}</small>
                  </div>
                  <div className="client-status">
                    {getStatusBadge(client.status)}
                  </div>
                </div>

                <div className="project-info">
                  <h4>{client.project_name}</h4>
                  <div className="risk-level">
                    <span 
                      className="risk-indicator"
                      style={{ backgroundColor: getRiskColor(client.risk_template) }}
                    ></span>
                    {client.risk_template.toUpperCase()} RISK
                  </div>
                </div>

                <div className="progress-metrics">
                  <div className="metric">
                    <label>Completion</label>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill"
                        style={{ width: `${client.completion_percentage}%` }}
                      ></div>
                    </div>
                    <span>{client.completion_percentage.toFixed(1)}%</span>
                  </div>

                  <div className="metric">
                    <label>Compliance Score</label>
                    <div className="score-display">
                      <span 
                        className="score-value"
                        style={{ color: getComplianceColor(client.compliance_score) }}
                      >
                        {client.compliance_score.toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div className="metric">
                    <label>Risk Score</label>
                    <div className="score-display">
                      <span className="score-value">
                        {client.risk_score.toFixed(1)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="client-actions">
                  <button 
                    className="btn btn-sm btn-primary"
                    onClick={() => onNavigate('project-details', client.project_id)}
                  >
                    View Details
                  </button>
                  <button 
                    className="btn btn-sm btn-secondary"
                    onClick={() => onNavigate('edit-project', client.project_id)}
                  >
                    Edit Project
                  </button>
                  {client.compliance_score >= 80 && (
                    <button 
                      className="btn btn-sm btn-success"
                      onClick={() => onNavigate('issue-certificate', client.project_id)}
                    >
                      Issue Certificate
                    </button>
                  )}
                </div>

                <div className="last-activity">
                  <small>
                    Last activity: {new Date(client.last_activity).toLocaleDateString()}
                  </small>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'evidence' && (
        <div className="evidence-tab">
          <h2>Evidence Review Queue</h2>
          <p>Evidence review functionality will be implemented here.</p>
        </div>
      )}

      {activeTab === 'certificates' && (
        <div className="certificates-tab">
          <h2>Certificate Management</h2>
          <p>Certificate issuance and management functionality will be implemented here.</p>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;

