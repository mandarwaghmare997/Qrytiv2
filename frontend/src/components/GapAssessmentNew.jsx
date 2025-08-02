import React, { useState, useEffect } from 'react';
import './GapAssessmentNew.css';

const GapAssessmentNew = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedControl, setSelectedControl] = useState(null);
  const [assessmentData, setAssessmentData] = useState({
    overallScore: 64,
    totalControls: 5,
    completed: 2,
    inProgress: 2,
    notStarted: 1,
    riskLevel: 'MEDIUM',
    lastUpdated: '2025-01-20'
  });

  const [controls, setControls] = useState([
    {
      id: 'ai_policy',
      title: 'AI Management System',
      category: 'AI Policy',
      description: 'Establish and maintain an AI management system',
      riskLevel: 'HIGH',
      status: 'completed',
      progress: 100,
      nistMapping: 'GOVERN-1.1',
      questions: [
        {
          id: 'q1',
          text: 'Has your organization established an AI governance framework?',
          answer: 'yes',
          evidence: ['AI_Policy_Document.pdf']
        }
      ]
    },
    {
      id: 'risk_mgmt',
      title: 'AI Risk Management',
      category: 'Risk Management',
      description: 'Implement comprehensive AI risk assessment processes',
      riskLevel: 'CRITICAL',
      status: 'in_progress',
      progress: 75,
      nistMapping: 'GOVERN-2.1',
      questions: [
        {
          id: 'q2',
          text: 'Do you have processes for identifying AI risks?',
          answer: 'partial',
          evidence: []
        }
      ]
    },
    {
      id: 'data_mgmt',
      title: 'AI Data Management',
      category: 'Asset Management',
      description: 'Ensure proper management of AI training and operational data',
      riskLevel: 'HIGH',
      status: 'in_progress',
      progress: 60,
      nistMapping: 'MAP-2.1',
      questions: [
        {
          id: 'q3',
          text: 'Are AI datasets properly documented and managed?',
          answer: 'no',
          evidence: []
        }
      ]
    },
    {
      id: 'impact_assess',
      title: 'AI Impact Assessment',
      category: 'Impact Assessment',
      description: 'Conduct thorough impact assessments for AI systems',
      riskLevel: 'MEDIUM',
      status: 'completed',
      progress: 100,
      nistMapping: 'MEASURE-2.1',
      questions: [
        {
          id: 'q4',
          text: 'Do you conduct impact assessments for AI systems?',
          answer: 'yes',
          evidence: ['Impact_Assessment_Template.docx']
        }
      ]
    },
    {
      id: 'monitoring',
      title: 'AI System Monitoring',
      category: 'Monitoring',
      description: 'Continuous monitoring of AI system performance and behavior',
      riskLevel: 'HIGH',
      status: 'not_started',
      progress: 0,
      nistMapping: 'MEASURE-2.2',
      questions: [
        {
          id: 'q5',
          text: 'Do you have continuous monitoring for AI systems?',
          answer: '',
          evidence: []
        }
      ]
    }
  ]);

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'CRITICAL': return 'bg-red-100 text-red-800 border-red-200';
      case 'HIGH': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'LOW': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'not_started': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✓';
      case 'in_progress': return '⟳';
      case 'not_started': return '○';
      default: return '○';
    }
  };

  const categories = [...new Set(controls.map(c => c.category))];

  const renderOverview = () => (
    <div className="gap-overview">
      {/* Header Stats */}
      <div className="stats-header">
        <div className="stats-left">
          <h2 className="assessment-title">ISO 42001 Compliance Assessment</h2>
          <div className="assessment-meta">
            <span className={`risk-badge ${getRiskLevelColor(assessmentData.riskLevel)}`}>
              Risk Level: {assessmentData.riskLevel}
            </span>
            <span className="last-updated">Last Updated: {assessmentData.lastUpdated}</span>
          </div>
        </div>
        <div className="compliance-circle">
          <div className="circle-progress" style={{'--progress': assessmentData.overallScore}}>
            <span className="score-text">{assessmentData.overallScore}%</span>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-number">{assessmentData.totalControls}</div>
            <div className="stat-label">Total Controls</div>
          </div>
        </div>
        <div className="stat-card completed">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-number">{assessmentData.completed}</div>
            <div className="stat-label">Completed</div>
          </div>
        </div>
        <div className="stat-card in-progress">
          <div className="stat-icon">🔄</div>
          <div className="stat-content">
            <div className="stat-number">{assessmentData.inProgress}</div>
            <div className="stat-label">In Progress</div>
          </div>
        </div>
        <div className="stat-card not-started">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <div className="stat-number">{assessmentData.notStarted}</div>
            <div className="stat-label">Not Started</div>
          </div>
        </div>
      </div>

      {/* Progress by Category */}
      <div className="category-progress">
        <h3>Assessment Progress by Category</h3>
        <div className="category-grid">
          {categories.map(category => {
            const categoryControls = controls.filter(c => c.category === category);
            const completedCount = categoryControls.filter(c => c.status === 'completed').length;
            const progressPercent = Math.round((completedCount / categoryControls.length) * 100);
            
            return (
              <div key={category} className="category-card">
                <div className="category-header">
                  <h4>{category}</h4>
                  <span className="category-progress-text">{completedCount}/{categoryControls.length}</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{width: `${progressPercent}%`}}
                  ></div>
                </div>
                <div className="category-meta">
                  <span>{progressPercent}% Complete</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  const renderControls = () => (
    <div className="controls-view">
      <div className="controls-header">
        <h3>ISO 42001 Controls Assessment</h3>
        <div className="controls-filters">
          <select className="filter-select">
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
            className="control-card"
            onClick={() => setSelectedControl(control)}
          >
            <div className="control-header">
              <div className="control-title-section">
                <h4>{control.title}</h4>
                <span className={`status-badge ${getStatusColor(control.status)}`}>
                  {getStatusIcon(control.status)} {control.status.replace('_', ' ')}
                </span>
              </div>
              <span className={`risk-badge ${getRiskLevelColor(control.riskLevel)}`}>
                {control.riskLevel}
              </span>
            </div>
            
            <p className="control-description">{control.description}</p>
            
            <div className="control-meta">
              <div className="nist-mapping">
                <span className="nist-label">NIST:</span>
                <span className="nist-code">{control.nistMapping}</span>
              </div>
              <div className="progress-section">
                <div className="progress-bar small">
                  <div 
                    className="progress-fill" 
                    style={{width: `${control.progress}%`}}
                  ></div>
                </div>
                <span className="progress-text">{control.progress}%</span>
              </div>
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
            className="back-button"
            onClick={() => setSelectedControl(null)}
          >
            ← Back to Controls
          </button>
          <div className="detail-title-section">
            <h3>{selectedControl.title}</h3>
            <span className={`risk-badge ${getRiskLevelColor(selectedControl.riskLevel)}`}>
              {selectedControl.riskLevel}
            </span>
          </div>
        </div>

        <div className="detail-content">
          <div className="detail-info">
            <div className="info-grid">
              <div className="info-item">
                <label>Category</label>
                <span>{selectedControl.category}</span>
              </div>
              <div className="info-item">
                <label>NIST Mapping</label>
                <span>{selectedControl.nistMapping}</span>
              </div>
              <div className="info-item">
                <label>Status</label>
                <span className={`status-badge ${getStatusColor(selectedControl.status)}`}>
                  {getStatusIcon(selectedControl.status)} {selectedControl.status.replace('_', ' ')}
                </span>
              </div>
              <div className="info-item">
                <label>Progress</label>
                <span>{selectedControl.progress}%</span>
              </div>
            </div>
          </div>

          <div className="assessment-questions">
            <h4>Assessment Questions</h4>
            {selectedControl.questions.map(question => (
              <div key={question.id} className="question-card">
                <div className="question-text">{question.text}</div>
                <div className="answer-section">
                  <div className="radio-group">
                    <label className="radio-label">
                      <input 
                        type="radio" 
                        name={`q_${question.id}`} 
                        value="yes"
                        checked={question.answer === 'yes'}
                        readOnly
                      />
                      <span>Yes</span>
                    </label>
                    <label className="radio-label">
                      <input 
                        type="radio" 
                        name={`q_${question.id}`} 
                        value="no"
                        checked={question.answer === 'no'}
                        readOnly
                      />
                      <span>No</span>
                    </label>
                    <label className="radio-label">
                      <input 
                        type="radio" 
                        name={`q_${question.id}`} 
                        value="partial"
                        checked={question.answer === 'partial'}
                        readOnly
                      />
                      <span>Partial</span>
                    </label>
                  </div>
                </div>
                
                <div className="evidence-section">
                  <h5>Evidence</h5>
                  {question.evidence.length > 0 ? (
                    <div className="evidence-list">
                      {question.evidence.map((file, idx) => (
                        <div key={idx} className="evidence-item">
                          📎 {file}
                          <button className="view-button">View</button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="no-evidence">
                      <button className="upload-button">📎 Upload Evidence</button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="detail-actions">
            <button className="save-button">Save Assessment</button>
            <button className="report-button">Generate Report</button>
          </div>
        </div>
      </div>
    );
  };

  const renderReports = () => (
    <div className="reports-view">
      <div className="reports-header">
        <h3>Compliance Reports</h3>
        <button className="generate-report-button">Generate New Report</button>
      </div>
      
      <div className="reports-grid">
        <div className="report-card">
          <div className="report-icon">📊</div>
          <div className="report-content">
            <h4>Executive Summary</h4>
            <p>High-level compliance overview for leadership</p>
            <div className="report-meta">
              <span>Last generated: 2025-01-20</span>
              <button className="download-button">Download PDF</button>
            </div>
          </div>
        </div>
        
        <div className="report-card">
          <div className="report-icon">📋</div>
          <div className="report-content">
            <h4>Detailed Assessment</h4>
            <p>Complete control-by-control analysis</p>
            <div className="report-meta">
              <span>Last generated: 2025-01-20</span>
              <button className="download-button">Download PDF</button>
            </div>
          </div>
        </div>
        
        <div className="report-card">
          <div className="report-icon">📈</div>
          <div className="report-content">
            <h4>Gap Analysis</h4>
            <p>Identified gaps and remediation plan</p>
            <div className="report-meta">
              <span>Coming Soon</span>
              <button className="download-button" disabled>Generate</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="gap-assessment-new">
      {/* Header */}
      <div className="assessment-header">
        <div className="header-left">
          <h1>Gap Assessment</h1>
          <p>ISO 42001 AI Management System Compliance</p>
        </div>
        <div className="header-actions">
          <button className="action-button secondary">Export Report</button>
          <button className="action-button primary">Save Progress</button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => {setActiveTab('overview'); setSelectedControl(null);}}
        >
          📊 Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'controls' ? 'active' : ''}`}
          onClick={() => {setActiveTab('controls'); setSelectedControl(null);}}
        >
          📋 Controls
        </button>
        <button 
          className={`tab-button ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => {setActiveTab('reports'); setSelectedControl(null);}}
        >
          📈 Reports
        </button>
      </div>

      {/* Content */}
      <div className="assessment-content">
        {selectedControl ? renderControlDetail() : 
         activeTab === 'overview' ? renderOverview() :
         activeTab === 'controls' ? renderControls() :
         renderReports()}
      </div>
    </div>
  );
};

export default GapAssessmentNew;

