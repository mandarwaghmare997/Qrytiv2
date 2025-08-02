import React, { useState, useEffect } from 'react';
import './ISO42001Compliance.css';

const ISO42001Compliance = ({ user, onNavigate }) => {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showStartJourney, setShowStartJourney] = useState(false);

  useEffect(() => {
    checkExistingProject();
  }, []);

  const checkExistingProject = async () => {
    try {
      const response = await fetch('/api/client/project', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const projectData = await response.json();
        setProject(projectData);
      } else if (response.status === 404) {
        // No project exists, show start journey option
        setShowStartJourney(true);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error checking project:', error);
      setLoading(false);
    }
  };

  const startISO42001Journey = () => {
    // This would typically open a modal or navigate to project setup
    setShowStartJourney(false);
    // For now, we'll simulate project creation
    setProject({
      id: 1,
      project_name: `ISO 42001 Compliance for ${user.organization || user.name}`,
      ai_system_name: '',
      risk_template: 'medium',
      completion_percentage: 0,
      compliance_score: 0,
      risk_score: 0,
      status: 'active'
    });
  };

  const resumeWork = () => {
    onNavigate('gap-assessment');
  };

  const getComplianceColor = (score) => {
    if (score >= 90) return '#10b981';
    if (score >= 70) return '#f59e0b';
    if (score >= 50) return '#ef4444';
    return '#6b7280';
  };

  const getRiskColor = (template) => {
    switch (template) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="iso-compliance">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading compliance data...</p>
        </div>
      </div>
    );
  }

  if (showStartJourney) {
    return (
      <div className="iso-compliance">
        <div className="start-journey-container">
          <div className="journey-card">
            <div className="journey-icon">🚀</div>
            <h1>Start ISO 42001 Journey</h1>
            <h2>for {user.organization || user.name}</h2>
            
            <div className="journey-description">
              <p>
                Begin your comprehensive ISO 42001:2023 AI Management System compliance assessment. 
                This journey will guide you through all necessary controls and requirements to achieve 
                certification.
              </p>
              
              <div className="journey-features">
                <div className="feature">
                  <span className="feature-icon">📋</span>
                  <div>
                    <strong>Comprehensive Assessment</strong>
                    <p>32 ISO 42001 controls across 9 categories</p>
                  </div>
                </div>
                
                <div className="feature">
                  <span className="feature-icon">📊</span>
                  <div>
                    <strong>Real-time Scoring</strong>
                    <p>Track compliance and risk scores as you progress</p>
                  </div>
                </div>
                
                <div className="feature">
                  <span className="feature-icon">📁</span>
                  <div>
                    <strong>Evidence Management</strong>
                    <p>Upload and manage supporting documentation</p>
                  </div>
                </div>
                
                <div className="feature">
                  <span className="feature-icon">📈</span>
                  <div>
                    <strong>Gap Analysis</strong>
                    <p>Identify areas for improvement and remediation</p>
                  </div>
                </div>
              </div>
            </div>
            
            <button 
              className="btn btn-primary btn-large"
              onClick={startISO42001Journey}
            >
              Start ISO 42001 Journey
            </button>
            
            <div className="journey-note">
              <p>
                <strong>Note:</strong> This assessment typically takes 2-4 weeks to complete 
                depending on your organization's size and AI system complexity.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (project) {
    return (
      <div className="iso-compliance">
        <div className="compliance-header">
          <div className="project-info">
            <h1>{project.project_name}</h1>
            <div className="project-meta">
              <span className="risk-badge" style={{ backgroundColor: getRiskColor(project.risk_template) }}>
                {project.risk_template.toUpperCase()} RISK
              </span>
              <span className="status-badge">
                {project.status.toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="compliance-actions">
            <button 
              className="btn btn-primary"
              onClick={resumeWork}
            >
              {project.completion_percentage > 0 ? 'Resume Work' : 'Start Assessment'}
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => onNavigate('reports')}
            >
              View Reports
            </button>
          </div>
        </div>

        <div className="compliance-overview">
          <div className="overview-card">
            <div className="card-header">
              <h3>Progress Overview</h3>
            </div>
            <div className="card-content">
              <div className="progress-metric">
                <label>Overall Completion</label>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${project.completion_percentage}%` }}
                  ></div>
                </div>
                <span className="progress-value">{project.completion_percentage.toFixed(1)}%</span>
              </div>
              
              <div className="metrics-grid">
                <div className="metric">
                  <div className="metric-value" style={{ color: getComplianceColor(project.compliance_score) }}>
                    {project.compliance_score.toFixed(1)}%
                  </div>
                  <div className="metric-label">Compliance Score</div>
                </div>
                
                <div className="metric">
                  <div className="metric-value">
                    {project.risk_score.toFixed(1)}
                  </div>
                  <div className="metric-label">Risk Score</div>
                </div>
              </div>
            </div>
          </div>

          <div className="overview-card">
            <div className="card-header">
              <h3>Assessment Categories</h3>
            </div>
            <div className="card-content">
              <div className="categories-list">
                <div className="category-item">
                  <div className="category-info">
                    <strong>AI Policy (A.2)</strong>
                    <span>3 controls</span>
                  </div>
                  <div className="category-progress">
                    <div className="mini-progress">
                      <div className="mini-progress-fill" style={{ width: '0%' }}></div>
                    </div>
                    <span>0%</span>
                  </div>
                </div>
                
                <div className="category-item">
                  <div className="category-info">
                    <strong>AI Roles & Responsibilities (A.3)</strong>
                    <span>2 controls</span>
                  </div>
                  <div className="category-progress">
                    <div className="mini-progress">
                      <div className="mini-progress-fill" style={{ width: '0%' }}></div>
                    </div>
                    <span>0%</span>
                  </div>
                </div>
                
                <div className="category-item">
                  <div className="category-info">
                    <strong>Resource Management (A.4)</strong>
                    <span>5 controls</span>
                  </div>
                  <div className="category-progress">
                    <div className="mini-progress">
                      <div className="mini-progress-fill" style={{ width: '0%' }}></div>
                    </div>
                    <span>0%</span>
                  </div>
                </div>
                
                <div className="category-item">
                  <div className="category-info">
                    <strong>Impact Assessment (A.5)</strong>
                    <span>4 controls</span>
                  </div>
                  <div className="category-progress">
                    <div className="mini-progress">
                      <div className="mini-progress-fill" style={{ width: '0%' }}></div>
                    </div>
                    <span>0%</span>
                  </div>
                </div>
                
                <div className="category-item">
                  <div className="category-info">
                    <strong>Development & Deployment (A.6)</strong>
                    <span>8 controls</span>
                  </div>
                  <div className="category-progress">
                    <div className="mini-progress">
                      <div className="mini-progress-fill" style={{ width: '0%' }}></div>
                    </div>
                    <span>0%</span>
                  </div>
                </div>
              </div>
              
              <button 
                className="btn btn-outline"
                onClick={resumeWork}
              >
                View All Categories
              </button>
            </div>
          </div>
        </div>

        <div className="quick-actions">
          <h3>Quick Actions</h3>
          <div className="actions-grid">
            <div className="action-card" onClick={resumeWork}>
              <div className="action-icon">📝</div>
              <div className="action-content">
                <strong>Continue Assessment</strong>
                <p>Answer control questions and upload evidence</p>
              </div>
            </div>
            
            <div className="action-card" onClick={() => onNavigate('evidence-upload')}>
              <div className="action-icon">📁</div>
              <div className="action-content">
                <strong>Upload Evidence</strong>
                <p>Add supporting documentation for controls</p>
              </div>
            </div>
            
            <div className="action-card" onClick={() => onNavigate('gap-analysis')}>
              <div className="action-icon">📊</div>
              <div className="action-content">
                <strong>Gap Analysis</strong>
                <p>Review compliance gaps and recommendations</p>
              </div>
            </div>
            
            <div className="action-card" onClick={() => onNavigate('reports')}>
              <div className="action-icon">📈</div>
              <div className="action-content">
                <strong>Generate Reports</strong>
                <p>Download compliance and progress reports</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default ISO42001Compliance;

