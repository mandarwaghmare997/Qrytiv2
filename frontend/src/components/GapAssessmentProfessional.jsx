import React, { useState, useEffect } from 'react';
import './GapAssessmentProfessional.css';

const GapAssessmentProfessional = ({ user, onNavigate, onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedControl, setSelectedControl] = useState(null);
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration
  const assessmentData = {
    complianceScore: 64,
    totalControls: 32,
    completedControls: 12,
    inProgressControls: 8,
    notStartedControls: 12,
    lastUpdated: '2025-01-20',
    riskLevel: 'MEDIUM'
  };

  const categories = [
    {
      id: 'ai-policy',
      name: 'AI Policy',
      code: 'A.2',
      controls: 3,
      completed: 2,
      progress: 67,
      riskLevel: 'medium'
    },
    {
      id: 'ai-roles',
      name: 'AI Roles & Responsibilities',
      code: 'A.3',
      controls: 2,
      completed: 1,
      progress: 50,
      riskLevel: 'high'
    },
    {
      id: 'resource-mgmt',
      name: 'Resource Management',
      code: 'A.4',
      controls: 5,
      completed: 3,
      progress: 60,
      riskLevel: 'medium'
    },
    {
      id: 'impact-assessment',
      name: 'Impact Assessment',
      code: 'A.5',
      controls: 4,
      completed: 2,
      progress: 50,
      riskLevel: 'high'
    },
    {
      id: 'development',
      name: 'Development & Deployment',
      code: 'A.6',
      controls: 8,
      completed: 3,
      progress: 38,
      riskLevel: 'critical'
    },
    {
      id: 'monitoring',
      name: 'Monitoring & Review',
      code: 'A.7',
      controls: 6,
      completed: 1,
      progress: 17,
      riskLevel: 'critical'
    }
  ];

  const controls = [
    {
      id: 'A.2.1',
      title: 'AI Policy Framework',
      category: 'AI Policy',
      status: 'completed',
      riskLevel: 'medium',
      description: 'Establish comprehensive AI governance policy',
      nistMapping: 'GOVERN-1.1',
      lastAssessed: '2025-01-15'
    },
    {
      id: 'A.2.2',
      title: 'AI Ethics Guidelines',
      category: 'AI Policy',
      status: 'in-progress',
      riskLevel: 'high',
      description: 'Define ethical principles for AI development',
      nistMapping: 'GOVERN-1.2',
      lastAssessed: '2025-01-10'
    },
    {
      id: 'A.3.1',
      title: 'AI Governance Roles',
      category: 'AI Roles & Responsibilities',
      status: 'not-started',
      riskLevel: 'critical',
      description: 'Define roles and responsibilities for AI governance',
      nistMapping: 'GOVERN-2.1',
      lastAssessed: null
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#10b981';
      case 'in-progress': return '#f59e0b';
      case 'not-started': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'critical': return '#dc2626';
      case 'high': return '#ea580c';
      case 'medium': return '#d97706';
      case 'low': return '#16a34a';
      default: return '#6b7280';
    }
  };

  const renderOverview = () => (
    <div className="gap-overview">
      {/* Header Stats */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
          </div>
          <div className="stat-content">
            <h3>Compliance Score</h3>
            <div className="stat-value">{assessmentData.complianceScore}%</div>
            <p className="stat-description">Overall compliance level</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 11H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2h-4"/>
              <path d="M9 11V7a3 3 0 0 1 6 0v4"/>
            </svg>
          </div>
          <div className="stat-content">
            <h3>Total Controls</h3>
            <div className="stat-value">{assessmentData.totalControls}</div>
            <p className="stat-description">ISO 42001 controls</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <path d="M22 4L12 14.01l-3-3"/>
            </svg>
          </div>
          <div className="stat-content">
            <h3>Completed</h3>
            <div className="stat-value">{assessmentData.completedControls}</div>
            <p className="stat-description">Controls completed</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6M12 17v6M4.22 4.22l4.24 4.24M15.54 15.54l4.24 4.24M1 12h6M17 12h6M4.22 19.78l4.24-4.24M15.54 8.46l4.24-4.24"/>
            </svg>
          </div>
          <div className="stat-content">
            <h3>In Progress</h3>
            <div className="stat-value">{assessmentData.inProgressControls}</div>
            <p className="stat-description">Controls in progress</p>
          </div>
        </div>
      </div>

      {/* Progress Chart */}
      <div className="progress-section">
        <div className="progress-card">
          <h3>Assessment Progress</h3>
          <div className="progress-chart">
            <div className="progress-circle">
              <svg viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="8"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="8"
                  strokeDasharray={`${assessmentData.complianceScore * 2.83} 283`}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div className="progress-text">
                <span className="progress-percentage">{assessmentData.complianceScore}%</span>
                <span className="progress-label">Complete</span>
              </div>
            </div>
            <div className="progress-details">
              <div className="progress-item">
                <div className="progress-dot completed"></div>
                <span>Completed: {assessmentData.completedControls}</span>
              </div>
              <div className="progress-item">
                <div className="progress-dot in-progress"></div>
                <span>In Progress: {assessmentData.inProgressControls}</span>
              </div>
              <div className="progress-item">
                <div className="progress-dot not-started"></div>
                <span>Not Started: {assessmentData.notStartedControls}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="categories-card">
          <h3>Categories Overview</h3>
          <div className="categories-list">
            {categories.map(category => (
              <div key={category.id} className="category-item">
                <div className="category-header">
                  <div className="category-info">
                    <h4>{category.name}</h4>
                    <span className="category-code">{category.code}</span>
                  </div>
                  <div className="category-stats">
                    <span className="category-progress">{category.progress}%</span>
                    <div className={`risk-badge ${category.riskLevel}`}>
                      {category.riskLevel.toUpperCase()}
                    </div>
                  </div>
                </div>
                <div className="category-progress-bar">
                  <div 
                    className="category-progress-fill"
                    style={{ width: `${category.progress}%` }}
                  ></div>
                </div>
                <div className="category-meta">
                  <span>{category.completed}/{category.controls} controls completed</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderControls = () => (
    <div className="gap-controls">
      <div className="controls-header">
        <h3>ISO 42001 Controls Assessment</h3>
        <div className="controls-filters">
          <button className="filter-btn active">All Controls</button>
          <button className="filter-btn">Critical</button>
          <button className="filter-btn">High Risk</button>
          <button className="filter-btn">Medium Risk</button>
          <button className="filter-btn">Low Risk</button>
        </div>
      </div>

      <div className="controls-grid">
        {controls.map(control => (
          <div 
            key={control.id} 
            className={`control-card ${control.status}`}
            onClick={() => setSelectedControl(control)}
          >
            <div className="control-header">
              <div className="control-id">{control.id}</div>
              <div className={`control-status ${control.status}`}>
                {control.status === 'completed' && '✓'}
                {control.status === 'in-progress' && '⏳'}
                {control.status === 'not-started' && '○'}
              </div>
            </div>
            <h4 className="control-title">{control.title}</h4>
            <p className="control-description">{control.description}</p>
            <div className="control-meta">
              <span className="control-category">{control.category}</span>
              <div className={`control-risk ${control.riskLevel}`}>
                {control.riskLevel.toUpperCase()}
              </div>
            </div>
            <div className="control-nist">
              <span>NIST: {control.nistMapping}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderReports = () => (
    <div className="gap-reports">
      <div className="reports-header">
        <h3>Compliance Reports</h3>
        <button className="btn btn-primary">Generate Report</button>
      </div>
      
      <div className="reports-grid">
        <div className="report-card">
          <div className="report-icon">📊</div>
          <h4>Executive Summary</h4>
          <p>High-level compliance overview for leadership</p>
          <button className="btn btn-outline">Download PDF</button>
        </div>
        
        <div className="report-card">
          <div className="report-icon">📋</div>
          <h4>Detailed Assessment</h4>
          <p>Complete control-by-control assessment results</p>
          <button className="btn btn-outline">Download PDF</button>
        </div>
        
        <div className="report-card">
          <div className="report-icon">🎯</div>
          <h4>Gap Analysis</h4>
          <p>Identified gaps and remediation recommendations</p>
          <button className="btn btn-outline">Download PDF</button>
        </div>
        
        <div className="report-card">
          <div className="report-icon">📈</div>
          <h4>Progress Tracking</h4>
          <p>Historical progress and trend analysis</p>
          <button className="btn btn-outline">Download PDF</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="gap-assessment-professional">
      {/* Header */}
      <div className="gap-header">
        <div className="header-left">
          <button 
            className="back-btn"
            onClick={() => onNavigate('dashboard')}
          >
            ← Back to Dashboard
          </button>
          <div className="header-info">
            <h1>Gap Assessment</h1>
            <p>ISO 42001 AI Management System Compliance</p>
          </div>
        </div>
        <div className="header-right">
          <div className="header-stats">
            <div className="header-stat">
              <span className="stat-label">Risk Level</span>
              <div className={`risk-badge ${assessmentData.riskLevel.toLowerCase()}`}>
                {assessmentData.riskLevel}
              </div>
            </div>
            <div className="header-stat">
              <span className="stat-label">Last Updated</span>
              <span className="stat-value">{assessmentData.lastUpdated}</span>
            </div>
          </div>
          <div className="header-actions">
            <button className="btn btn-outline">Export Report</button>
            <button className="btn btn-primary">Save Progress</button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="gap-nav">
        <button 
          className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <span className="tab-icon">📊</span>
          Overview
        </button>
        <button 
          className={`nav-tab ${activeTab === 'controls' ? 'active' : ''}`}
          onClick={() => setActiveTab('controls')}
        >
          <span className="tab-icon">📋</span>
          Controls
        </button>
        <button 
          className={`nav-tab ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          <span className="tab-icon">📈</span>
          Reports
        </button>
      </div>

      {/* Content */}
      <div className="gap-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'controls' && renderControls()}
        {activeTab === 'reports' && renderReports()}
      </div>

      {/* Control Detail Modal */}
      {selectedControl && (
        <div className="modal-overlay" onClick={() => setSelectedControl(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedControl.title}</h3>
              <button 
                className="modal-close"
                onClick={() => setSelectedControl(null)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="control-detail">
                <div className="control-meta-detail">
                  <div className="meta-item">
                    <label>Control ID</label>
                    <span>{selectedControl.id}</span>
                  </div>
                  <div className="meta-item">
                    <label>Category</label>
                    <span>{selectedControl.category}</span>
                  </div>
                  <div className="meta-item">
                    <label>NIST Mapping</label>
                    <span>{selectedControl.nistMapping}</span>
                  </div>
                  <div className="meta-item">
                    <label>Risk Level</label>
                    <div className={`risk-badge ${selectedControl.riskLevel}`}>
                      {selectedControl.riskLevel.toUpperCase()}
                    </div>
                  </div>
                </div>
                <div className="control-description-detail">
                  <h4>Description</h4>
                  <p>{selectedControl.description}</p>
                </div>
                <div className="control-actions">
                  <button className="btn btn-primary">Start Assessment</button>
                  <button className="btn btn-outline">Upload Evidence</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GapAssessmentProfessional;

