import React, { useState, useEffect } from 'react';
import './AdminDashboardNew.css';
import CreateClientForm from './CreateClientForm.jsx';
import CreateProjectForm from './CreateProjectForm.jsx';
import DeleteConfirmModal from './DeleteConfirmModal.jsx';
import qrytiLogo from '../assets/qryti-logo.png';
import apiService from '../services/api.js';

const AdminDashboardNew = ({ user, onNavigate, onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [showCreateClient, setShowCreateClient] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [clients, setClients] = useState([]);
  const [projects, setProjects] = useState([]);
  const [statistics, setStatistics] = useState({
    total_clients: 0,
    total_projects: 0,
    active_projects: 0,
    avg_compliance_score: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      // Use the new API service methods
      const [stats, clientsData, projectsData] = await Promise.all([
        apiService.getAdminStats(),
        apiService.getClients(),
        apiService.getProjects()
      ]);

      setStatistics(stats);
      setClients(clientsData);
      setProjects(projectsData);

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateClient = async (clientData) => {
    try {
      const result = await apiService.createClient(clientData);
      
      // Add the new client to the list
      setClients(prev => [...prev, result.client]);
      
      // Add the new project if created
      if (result.project) {
        setProjects(prev => [...prev, result.project]);
      }
      
      // Refresh statistics to get updated counts
      const updatedStats = await apiService.getAdminStats();
      setStatistics(updatedStats);
      
      setShowCreateClient(false);
      return { success: true };
      
    } catch (error) {
      console.error('Failed to create client:', error);
      return { success: false, error: error.message || 'Failed to create client' };
    }
  };

  const handleCreateProject = async (projectData) => {
    try {
      const result = await apiService.createProject(projectData);
      
      // Add the new project to the list
      setProjects(prev => [...prev, result.project]);
      
      // Refresh statistics
      const updatedStats = await apiService.getAdminStats();
      setStatistics(updatedStats);
      
      setShowCreateProject(false);
      return { success: true };
      
    } catch (error) {
      console.error('Failed to create project:', error);
      return { success: false, error: error.message || 'Failed to create project' };
    }
  };

  const handleDelete = (type, item) => {
    setDeleteTarget({ type, item });
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;

    try {
      const { type, item } = deleteTarget;
      
      // For now, just remove from local state since delete endpoints aren't implemented
      if (type === 'client') {
        setClients(prev => prev.filter(c => c.id !== item.id));
        setProjects(prev => prev.filter(p => p.client_id !== item.id));
      } else {
        setProjects(prev => prev.filter(p => p.id !== item.id));
      }
      
      // Refresh statistics
      const updatedStats = await apiService.getAdminStats();
      setStatistics(updatedStats);
      
    } catch (error) {
      console.error('Delete error:', error);
    } finally {
      setShowDeleteModal(false);
      setDeleteTarget(null);
    }
  };

  const renderOverview = () => (
    <div className="overview-section">
      <div className="stats-grid">
        <div className="stat-card clients">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{statistics.total_clients}</h3>
            <p>Total Clients</p>
          </div>
          <div className="stat-trend">+{statistics.total_clients > 0 ? '12%' : '0%'}</div>
        </div>
        
        <div className="stat-card projects">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>{statistics.total_projects}</h3>
            <p>Active Projects</p>
          </div>
          <div className="stat-trend">+{statistics.total_projects > 0 ? '8%' : '0%'}</div>
        </div>
        
        <div className="stat-card compliance">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <h3>{Math.round(statistics.avg_compliance_score)}%</h3>
            <p>Avg Compliance</p>
          </div>
          <div className="stat-trend">+{statistics.avg_compliance_score > 0 ? '15%' : '0%'}</div>
        </div>
        
        <div className="stat-card certificates">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <h3>0</h3>
            <p>Certificates Issued</p>
          </div>
          <div className="stat-trend">+0</div>
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
            <span className="btn-icon">📋</span>
            Create New Project
          </button>
          <button className="action-btn tertiary">
            <span className="btn-icon">📊</span>
            Generate Report
          </button>
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          {statistics.recent_activity && statistics.recent_activity.length > 0 ? (
            statistics.recent_activity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">📝</div>
                <div className="activity-content">
                  <p>{activity.message}</p>
                  <span className="activity-time">
                    {new Date(activity.timestamp).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="activity-item">
              <div className="activity-icon">📝</div>
              <div className="activity-content">
                <p>No recent activity</p>
                <span className="activity-time">Start by creating your first client</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderClientProgress = () => (
    <div className="clients-section">
      <div className="section-header">
        <h3>Client Management</h3>
        <button 
          className="add-btn"
          onClick={() => setShowCreateClient(true)}
        >
          + Add New Client
        </button>
      </div>
      
      <div className="clients-grid">
        {clients.map(client => (
          <div key={client.id} className="client-card">
            <div className="client-header">
              <div className="client-avatar">
                {client.name.charAt(0).toUpperCase()}
              </div>
              <div className="client-info">
                <h4>{client.name}</h4>
                <p>{client.organization}</p>
                <span className="client-email">{client.email}</span>
              </div>
              <div className="client-actions">
                <button 
                  className="action-btn-small edit"
                  title="Edit Client"
                >
                  ✏️
                </button>
                <button 
                  className="action-btn-small delete"
                  onClick={() => handleDelete('client', client)}
                  title="Delete Client"
                >
                  🗑️
                </button>
              </div>
            </div>
            
            <div className="client-stats">
              <div className="stat-item">
                <span className="stat-label">Department:</span>
                <span className="stat-value">{client.department || 'N/A'}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Projects:</span>
                <span className="stat-value">{client.projects_count || 0}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Compliance:</span>
                <span className="stat-value">{client.compliance_score || 0}%</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Status:</span>
                <span className={`status-badge ${client.is_active ? 'active' : 'inactive'}`}>
                  {client.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
            
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${client.compliance_score || 0}%` }}
              ></div>
            </div>
          </div>
        ))}
        
        {clients.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">👥</div>
            <h4>No clients yet</h4>
            <p>Create your first client to get started</p>
            <button 
              className="action-btn primary"
              onClick={() => setShowCreateClient(true)}
            >
              Create First Client
            </button>
          </div>
        )}
      </div>
    </div>
  );

  const renderEvidenceReview = () => (
    <div className="evidence-section">
      <h3>Evidence Review Queue</h3>
      <div className="evidence-list">
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h4>No evidence to review</h4>
          <p>Evidence uploads will appear here for review</p>
        </div>
      </div>
    </div>
  );

  const renderCertificates = () => (
    <div className="certificates-section">
      <h3>Certificate Management</h3>
      <div className="certificates-list">
        <div className="empty-state">
          <div className="empty-icon">🏆</div>
          <h4>No certificates issued</h4>
          <p>Completed compliance projects will appear here</p>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="admin-dashboard loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <img src={qrytiLogo} alt="Qryti" className="header-logo" />
          <div className="header-title">
            <h1>Qryti Admin</h1>
            <p>ISO 42001 Compliance Platform</p>
          </div>
        </div>
        <div className="header-right">
          <div className="user-info">
            <div className="user-avatar">
              {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'A'}
            </div>
            <div className="user-details">
              <span className="user-name">{user?.full_name || 'Admin'}</span>
              <span className="user-role">Administrator</span>
            </div>
          </div>
          <button onClick={onLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <nav className="dashboard-nav">
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <span className="tab-icon">📊</span>
            Overview
          </button>
          <button 
            className={`nav-tab ${activeTab === 'clients' ? 'active' : ''}`}
            onClick={() => setActiveTab('clients')}
          >
            <span className="tab-icon">👥</span>
            Clients
          </button>
          <button 
            className={`nav-tab ${activeTab === 'evidence' ? 'active' : ''}`}
            onClick={() => setActiveTab('evidence')}
          >
            <span className="tab-icon">📄</span>
            Evidence Review
          </button>
          <button 
            className={`nav-tab ${activeTab === 'certificates' ? 'active' : ''}`}
            onClick={() => setActiveTab('certificates')}
          >
            <span className="tab-icon">🏆</span>
            Certificates
          </button>
        </div>
      </nav>

      <main className="dashboard-main">
        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            {error}
            <button 
              className="retry-btn"
              onClick={fetchDashboardData}
            >
              Retry
            </button>
          </div>
        )}
        
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'clients' && renderClientProgress()}
        {activeTab === 'evidence' && renderEvidenceReview()}
        {activeTab === 'certificates' && renderCertificates()}
      </main>

      {/* Modals */}
      {showCreateClient && (
        <CreateClientForm
          onSubmit={handleCreateClient}
          onClose={() => setShowCreateClient(false)}
        />
      )}

      {showCreateProject && (
        <CreateProjectForm
          clients={clients}
          onSubmit={handleCreateProject}
          onClose={() => setShowCreateProject(false)}
        />
      )}

      {showDeleteModal && (
        <DeleteConfirmModal
          target={deleteTarget}
          onConfirm={confirmDelete}
          onCancel={() => setShowDeleteModal(false)}
        />
      )}
    </div>
  );
};

export default AdminDashboardNew;

