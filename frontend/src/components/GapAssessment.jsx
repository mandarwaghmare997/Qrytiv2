import React, { useState, useEffect } from 'react';
import './GapAssessment.css';
import apiService from '../services/api.js';

const GapAssessment = ({ user, onNavigate }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [assessmentData, setAssessmentData] = useState(null);
  const [controls, setControls] = useState([]);
  const [selectedControl, setSelectedControl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [riskLevel, setRiskLevel] = useState('medium');
  const [complianceScore, setComplianceScore] = useState(0);
  const [evidenceModal, setEvidenceModal] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Mock data for demonstration
  const mockControls = [
    {
      id: 'A.2.1',
      name: 'AI Management System',
      category: 'AI Policy',
      description: 'The organization shall establish, implement, maintain and continually improve an AI management system.',
      status: 'completed',
      compliance_score: 95,
      risk_level: 'Critical',
      nist_mapping: ['GOVERN-1.1', 'GOVERN-1.2'],
      evidence_count: 3,
      last_updated: '2025-01-15'
    },
    {
      id: 'A.2.2',
      name: 'AI Policy',
      category: 'AI Policy',
      description: 'The organization shall document a policy for the development or use of AI systems.',
      status: 'in_progress',
      compliance_score: 75,
      risk_level: 'High',
      nist_mapping: ['GOVERN-1.3', 'GOVERN-2.1'],
      evidence_count: 2,
      last_updated: '2025-01-10'
    },
    {
      id: 'A.3.1',
      name: 'AI Risk Management',
      category: 'Risk Management',
      description: 'The organization shall establish and maintain an AI risk management process.',
      status: 'not_started',
      compliance_score: 0,
      risk_level: 'Critical',
      nist_mapping: ['MANAGE-1.1', 'MANAGE-2.1'],
      evidence_count: 0,
      last_updated: null
    },
    {
      id: 'A.4.1',
      name: 'AI System Inventory',
      category: 'Asset Management',
      description: 'The organization shall maintain an inventory of AI systems.',
      status: 'completed',
      compliance_score: 90,
      risk_level: 'Medium',
      nist_mapping: ['MAP-1.1', 'MAP-1.2'],
      evidence_count: 4,
      last_updated: '2025-01-20'
    },
    {
      id: 'A.5.1',
      name: 'AI Impact Assessment',
      category: 'Impact Assessment',
      description: 'The organization shall conduct impact assessments for AI systems.',
      status: 'in_progress',
      compliance_score: 60,
      risk_level: 'High',
      nist_mapping: ['MAP-2.1', 'MEASURE-1.1'],
      evidence_count: 1,
      last_updated: '2025-01-12'
    }
  ];

  useEffect(() => {
    fetchAssessmentData();
  }, []);

  const fetchAssessmentData = async () => {
    setLoading(true);
    try {
      // For now, use mock data
      setControls(mockControls);
      calculateComplianceScore(mockControls);
      setAssessmentData({
        project_name: 'ISO 42001 Compliance Assessment',
        risk_level: 'medium',
        total_controls: mockControls.length,
        completed_controls: mockControls.filter(c => c.status === 'completed').length,
        in_progress_controls: mockControls.filter(c => c.status === 'in_progress').length,
        last_updated: '2025-01-20'
      });
    } catch (error) {
      setError('Failed to load assessment data');
    } finally {
      setLoading(false);
    }
  };

  const calculateComplianceScore = (controlsList) => {
    const totalScore = controlsList.reduce((sum, control) => sum + control.compliance_score, 0);
    const avgScore = controlsList.length > 0 ? Math.round(totalScore / controlsList.length) : 0;
    setComplianceScore(avgScore);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#10B981';
      case 'in_progress': return '#F59E0B';
      case 'not_started': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return 'Completed';
      case 'in_progress': return 'In Progress';
      case 'not_started': return 'Not Started';
      default: return 'Unknown';
    }
  };

  const getRiskLevelColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'critical': return '#DC2626';
      case 'high': return '#EA580C';
      case 'medium': return '#D97706';
      case 'low': return '#059669';
      default: return '#6B7280';
    }
  };

  const handleControlClick = (control) => {
    setSelectedControl(control);
    setActiveTab('control-detail');
  };

  const handleEvidenceUpload = (controlId) => {
    setEvidenceModal(true);
    // Simulate upload progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setUploadProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          setEvidenceModal(false);
          setUploadProgress(0);
        }, 1000);
      }
    }, 200);
  };

  const renderOverview = () => (
    <div className="assessment-overview">
      <div className="overview-header">
        <div className="project-info">
          <h2>{assessmentData?.project_name}</h2>
          <p className="project-meta">
            Risk Level: <span className={`risk-badge ${riskLevel}`}>{riskLevel.toUpperCase()}</span>
            • Last Updated: {assessmentData?.last_updated}
          </p>
        </div>
        <div className="compliance-score-circle">
          <div className="score-circle">
            <div className="score-inner">
              <span className="score-number">{complianceScore}%</span>
              <span className="score-label">Compliance</span>
            </div>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <h3>{assessmentData?.total_controls}</h3>
            <p>Total Controls</p>
          </div>
        </div>
        
        <div className="stat-card completed">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{assessmentData?.completed_controls}</h3>
            <p>Completed</p>
          </div>
        </div>
        
        <div className="stat-card in-progress">
          <div className="stat-icon">🔄</div>
          <div className="stat-content">
            <h3>{assessmentData?.in_progress_controls}</h3>
            <p>In Progress</p>
          </div>
        </div>
        
        <div className="stat-card pending">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <h3>{assessmentData?.total_controls - assessmentData?.completed_controls - assessmentData?.in_progress_controls}</h3>
            <p>Not Started</p>
          </div>
        </div>
      </div>

      <div className="progress-section">
        <h3>Assessment Progress by Category</h3>
        <div className="category-progress">
          {['AI Policy', 'Risk Management', 'Asset Management', 'Impact Assessment'].map(category => {
            const categoryControls = controls.filter(c => c.category === category);
            const completedCount = categoryControls.filter(c => c.status === 'completed').length;
            const progressPercent = categoryControls.length > 0 ? (completedCount / categoryControls.length) * 100 : 0;
            
            return (
              <div key={category} className="category-item">
                <div className="category-header">
                  <span className="category-name">{category}</span>
                  <span className="category-stats">{completedCount}/{categoryControls.length}</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${progressPercent}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  const renderControlsList = () => (
    <div className="controls-list">
      <div className="controls-header">
        <h3>ISO 42001 Controls Assessment</h3>
        <div className="controls-filters">
          <select 
            value={riskLevel} 
            onChange={(e) => setRiskLevel(e.target.value)}
            className="risk-filter"
          >
            <option value="all">All Risk Levels</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      <div className="controls-grid">
        {controls.map(control => (
          <div 
            key={control.id} 
            className={`control-card ${control.status}`}
            onClick={() => handleControlClick(control)}
          >
            <div className="control-header">
              <div className="control-id">{control.id}</div>
              <div 
                className="status-indicator"
                style={{ backgroundColor: getStatusColor(control.status) }}
              ></div>
            </div>
            
            <h4 className="control-name">{control.name}</h4>
            <p className="control-description">{control.description}</p>
            
            <div className="control-meta">
              <div className="meta-item">
                <span className="meta-label">Category:</span>
                <span className="meta-value">{control.category}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Risk Level:</span>
                <span 
                  className="meta-value risk-level"
                  style={{ color: getRiskLevelColor(control.risk_level) }}
                >
                  {control.risk_level}
                </span>
              </div>
            </div>
            
            <div className="control-progress">
              <div className="progress-info">
                <span>Compliance: {control.compliance_score}%</span>
                <span>Evidence: {control.evidence_count}</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${control.compliance_score}%` }}
                ></div>
              </div>
            </div>
            
            <div className="control-footer">
              <span className="status-text">{getStatusText(control.status)}</span>
              {control.last_updated && (
                <span className="last-updated">Updated: {control.last_updated}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderControlDetail = () => {
    if (!selectedControl) return null;

    return (
      <div className="control-detail">
        <div className="detail-header">
          <button 
            className="back-btn"
            onClick={() => setActiveTab('controls')}
          >
            ← Back to Controls
          </button>
          <div className="control-title">
            <h2>{selectedControl.id}: {selectedControl.name}</h2>
            <div className="control-badges">
              <span 
                className="status-badge"
                style={{ backgroundColor: getStatusColor(selectedControl.status) }}
              >
                {getStatusText(selectedControl.status)}
              </span>
              <span 
                className="risk-badge"
                style={{ backgroundColor: getRiskLevelColor(selectedControl.risk_level) }}
              >
                {selectedControl.risk_level}
              </span>
            </div>
          </div>
        </div>

        <div className="detail-content">
          <div className="detail-section">
            <h3>Description</h3>
            <p>{selectedControl.description}</p>
          </div>

          <div className="detail-section">
            <h3>NIST AI RMF Mapping</h3>
            <div className="nist-mappings">
              {selectedControl.nist_mapping.map(mapping => (
                <span key={mapping} className="nist-tag">{mapping}</span>
              ))}
            </div>
          </div>

          <div className="detail-section">
            <h3>Assessment Questions</h3>
            <div className="assessment-questions">
              <div className="question-item">
                <div className="question-text">
                  Is there a documented policy for the development or use of AI systems?
                </div>
                <div className="question-controls">
                  <label className="radio-label">
                    <input type="radio" name="q1" value="yes" />
                    <span>Yes</span>
                  </label>
                  <label className="radio-label">
                    <input type="radio" name="q1" value="no" />
                    <span>No</span>
                  </label>
                  <label className="radio-label">
                    <input type="radio" name="q1" value="partial" />
                    <span>Partial</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h3>Evidence ({selectedControl.evidence_count})</h3>
            <div className="evidence-section">
              <button 
                className="upload-btn"
                onClick={() => handleEvidenceUpload(selectedControl.id)}
              >
                📎 Upload Evidence
              </button>
              <div className="evidence-list">
                <div className="evidence-item">
                  <div className="evidence-icon">📄</div>
                  <div className="evidence-info">
                    <span className="evidence-name">AI_Policy_Document_v2.pdf</span>
                    <span className="evidence-meta">Uploaded: 2025-01-15 • 2.1 MB</span>
                  </div>
                  <button className="evidence-action">View</button>
                </div>
              </div>
            </div>
          </div>

          <div className="detail-actions">
            <button className="action-btn primary">Save Assessment</button>
            <button className="action-btn secondary">Generate Report</button>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="gap-assessment loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading assessment data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="gap-assessment">
      <header className="assessment-header">
        <div className="header-left">
          <h1>Gap Assessment</h1>
          <p>ISO 42001 AI Management System Compliance</p>
        </div>
        <div className="header-actions">
          <button className="action-btn secondary">Export Report</button>
          <button className="action-btn primary">Save Progress</button>
        </div>
      </header>

      <nav className="assessment-nav">
        <div className="nav-tabs">
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
      </nav>

      <main className="assessment-main">
        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}
        
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'controls' && renderControlsList()}
        {activeTab === 'control-detail' && renderControlDetail()}
        {activeTab === 'reports' && (
          <div className="reports-section">
            <h3>Assessment Reports</h3>
            <p>Report generation coming soon...</p>
          </div>
        )}
      </main>

      {/* Evidence Upload Modal */}
      {evidenceModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Upload Evidence</h3>
            <div className="upload-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p>Uploading... {uploadProgress}%</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GapAssessment;

