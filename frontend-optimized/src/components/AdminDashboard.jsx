import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';
import CreateClientForm from './CreateClientForm.jsx';
import CreateProjectForm from './CreateProjectForm.jsx';
import qrytiLogo from '../assets/qryti-logo.png';

const AdminDashboard = ({ user, onNavigate, onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [showCreateClient, setShowCreateClient] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [clients, setClients] = useState([]);
  const [projects, setProjects] = useState([]);
  const [statistics, setStatistics] = useState({
    totalClients: 0,
    activeProjects: 0,
    completedProjects: 0,
    averageCompliance: 0,
    pendingEvidence: 0,
    certificatesIssued: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Mock data for now since backend endpoints may not be fully implemented
      setClients([
        {
          id: 1,
          name: 'John Smith',
          email: 'john@techcorp.com',
          organization: 'TechCorp Inc.',
          is_active: true,
          last_login: '2024-08-01T10:30:00Z'
        },
        {
          id: 2,
          name: 'Sarah Johnson',
          email: 'sarah@dataflow.com',
          organization: 'DataFlow Solutions',
          is_active: true,
          last_login: '2024-07-30T14:15:00Z'
        }
      ]);

      setProjects([
        {
          id: 1,
          project_name: 'ISO 42001 Compliance for TechCorp',
          client_id: 1,
          client_name: 'TechCorp Inc.',
          risk_template: 'high',
          compliance_score: 75,
          completion_percentage: 60
        },
        {
          id: 2,
          project_name: 'AI Governance Assessment',
          client_id: 2,
          client_name: 'DataFlow Solutions',
          risk_template: 'medium',
          compliance_score: 85,
          completion_percentage: 80
        }
      ]);

      setStatistics({
        totalClients: 2,
        activeProjects: 2,
        completedProjects: 0,
        averageCompliance: 80,
        pendingEvidence: 3,
        certificatesIssued: 0
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateClientSuccess = (newClient) => {
    setClients(prev => [...prev, { ...newClient, id: Date.now() }]);
    setStatistics(prev => ({ ...prev, totalClients: prev.totalClients + 1 }));
  };

  const handleCreateProjectSuccess = (newProject) => {
    setProjects(prev => [...prev, { ...newProject, id: Date.now() }]);
    setStatistics(prev => ({ ...prev, activeProjects: prev.activeProjects + 1 }));
  };

  const getComplianceColor = (score) => {
    if (score >= 80) return '#10b981'; // Green
    if (score >= 60) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const OverviewTab = () => (
    <div className="overview-content">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-number">{statistics.totalClients}</div>
            <div className="stat-label">Total Clients</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-number">{statistics.activeProjects}</div>
            <div className="stat-label">Active Projects</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-number">{statistics.completedProjects}</div>
            <div className="stat-label">Completed Projects</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-number">{statistics.averageCompliance}%</div>
            <div className="stat-label">Avg Compliance</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-number">{statistics.pendingEvidence}</div>
            <div className="stat-label">Pending Evidence</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <div className="stat-number">{statistics.certificatesIssued}</div>
            <div className="stat-label">Certificates Issued</div>
          </div>
        </div>
      </div>

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <button 
            className="action-btn primary"
            onClick={() => setShowCreateClient(true)}
          >
            <span className="btn-icon">👤</span>
            Create New Client
          </button>
          <button 
            className="action-btn secondary"
            onClick={() => setShowCreateProject(true)}
          >
            <span className="btn-icon">📊</span>
            Create New Project
          </button>
          <button 
            className="action-btn tertiary"
            onClick={() => setActiveTab('evidence')}
          >
            <span className="btn-icon">📋</span>
            Review Evidence
          </button>
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Projects</h3>
        <div className="activity-list">
          {projects.slice(0, 5).map(project => (
            <div key={project.id} className="activity-item">
              <div className="activity-info">
                <div className="activity-title">{project.project_name}</div>
                <div className="activity-subtitle">
                  {project.client_name} • {project.risk_template} risk
                </div>
              </div>
              <div className="activity-status">
                <div 
                  className="compliance-score"
                  style={{ color: getComplianceColor(project.compliance_score || 0) }}
                >
                  {project.compliance_score || 0}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ClientProgressTab = () => (
    <div className="client-progress-content">
      <div className="tab-header">
        <h3>Client Progress Overview</h3>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateClient(true)}
        >
          Add New Client
        </button>
      </div>

      <div className="progress-grid">
        {clients.map(client => {
          const clientProjects = projects.filter(p => p.client_id === client.id);
          const avgCompliance = clientProjects.length > 0 
            ? Math.round(clientProjects.reduce((sum, p) => sum + (p.compliance_score || 0), 0) / clientProjects.length)
            : 0;

          return (
            <div key={client.id} className="progress-card">
              <div className="progress-header">
                <div className="client-info">
                  <h4>{client.name}</h4>
                  <p>{client.organization}</p>
                  <p className="client-email">{client.email}</p>
                </div>
                <div className="progress-score">
                  <div 
                    className="score-circle"
                    style={{ color: getComplianceColor(avgCompliance) }}
                  >
                    {avgCompliance}%
                  </div>
                </div>
              </div>

              <div className="progress-details">
                <div className="detail-item">
                  <span>Projects:</span>
                  <span>{clientProjects.length}</span>
                </div>
                <div className="detail-item">
                  <span>Status:</span>
                  <span className={`status ${client.is_active ? 'active' : 'inactive'}`}>
                    {client.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="detail-item">
                  <span>Last Login:</span>
                  <span>{client.last_login ? new Date(client.last_login).toLocaleDateString() : 'Never'}</span>
                </div>
              </div>

              <div className="progress-actions">
                <button 
                  className="btn btn-sm btn-secondary"
                  onClick={() => setShowCreateProject(true)}
                >
                  New Project
                </button>
                <button className="btn btn-sm btn-outline">
                  View Details
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const EvidenceReviewTab = () => (
    <div className="evidence-review-content">
      <div className="tab-header">
        <h3>Evidence Review Queue</h3>
        <div className="review-stats">
          <span className="pending-count">{statistics.pendingEvidence} pending</span>
        </div>
      </div>

      <div className="evidence-list">
        <div className="evidence-item">
          <div className="evidence-info">
            <div className="evidence-title">AI Model Documentation.pdf</div>
            <div className="evidence-subtitle">Control 4.1 - AI System Documentation</div>
            <div className="evidence-meta">
              Uploaded by TechCorp Inc. • 2 days ago • 1.2 MB
            </div>
          </div>
          <div className="evidence-actions">
            <button className="btn btn-sm btn-success">Approve</button>
            <button className="btn btn-sm btn-danger">Reject</button>
            <button className="btn btn-sm btn-outline">Download</button>
          </div>
        </div>

        <div className="evidence-item">
          <div className="evidence-info">
            <div className="evidence-title">Risk Assessment Report.docx</div>
            <div className="evidence-subtitle">Control 6.2 - Risk Management</div>
            <div className="evidence-meta">
              Uploaded by DataFlow Solutions • 1 day ago • 856 KB
            </div>
          </div>
          <div className="evidence-actions">
            <button className="btn btn-sm btn-success">Approve</button>
            <button className="btn btn-sm btn-danger">Reject</button>
            <button className="btn btn-sm btn-outline">Download</button>
          </div>
        </div>
      </div>
    </div>
  );

  const CertificatesTab = () => (
    <div className="certificates-content">
      <div className="tab-header">
        <h3>Certificate Management</h3>
        <div className="cert-stats">
          <span className="issued-count">{statistics.certificatesIssued} issued</span>
        </div>
      </div>

      <div className="eligible-projects">
        <h4>Projects Eligible for Certification</h4>
        <div className="eligible-list">
          {projects.filter(p => (p.compliance_score || 0) >= 80).map(project => (
            <div key={project.id} className="eligible-item">
              <div className="project-info">
                <div className="project-title">{project.project_name}</div>
                <div className="project-subtitle">
                  {project.client_name} • Compliance: {project.compliance_score || 0}%
                </div>
              </div>
              <div className="cert-actions">
                <button className="btn btn-sm btn-primary">Issue Certificate</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="admin-dashboard loading">
        <div className="loading-spinner">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <div className="header-content">
          <div className="header-left">
            <img src={qrytiLogo} alt="Qryti" className="admin-logo" />
            <h1>Admin Dashboard</h1>
          </div>
          <div className="admin-info">
            <span>Welcome, {user?.name || 'Admin'}</span>
            <button className="logout-btn" onClick={onLogout}>Logout</button>
          </div>
        </div>
      </header>

      <nav className="admin-nav">
        <button 
          className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`nav-tab ${activeTab === 'clients' ? 'active' : ''}`}
          onClick={() => setActiveTab('clients')}
        >
          Client Progress
        </button>
        <button 
          className={`nav-tab ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          Evidence Review
        </button>
        <button 
          className={`nav-tab ${activeTab === 'certificates' ? 'active' : ''}`}
          onClick={() => setActiveTab('certificates')}
        >
          Certificates
        </button>
      </nav>

      <main className="admin-main">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'clients' && <ClientProgressTab />}
        {activeTab === 'evidence' && <EvidenceReviewTab />}
        {activeTab === 'certificates' && <CertificatesTab />}
      </main>

      {showCreateClient && (
        <CreateClientForm
          onClose={() => setShowCreateClient(false)}
          onSuccess={handleCreateClientSuccess}
        />
      )}

      {showCreateProject && (
        <CreateProjectForm
          onClose={() => setShowCreateProject(false)}
          onSuccess={handleCreateProjectSuccess}
        />
      )}
    </div>
  );
};

export default AdminDashboard;

