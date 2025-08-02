import React, { useState, useEffect } from 'react';
import './Certifications.css';

const Certifications = ({ onBack }) => {
  const [certifications, setCertifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCert, setSelectedCert] = useState(null);

  // Demo certifications data
  const demoCertifications = [
    {
      id: 1,
      name: 'ISO 42001:2023 AI Management System',
      status: 'In Progress',
      progress: 75,
      issuer: 'International Organization for Standardization',
      validFrom: '2024-01-01',
      validUntil: '2027-01-01',
      lastAssessment: '2024-01-15',
      nextAssessment: '2024-04-15',
      requirements: [
        { id: 'A.2', name: 'AI Policy', status: 'Completed', score: 90 },
        { id: 'A.3', name: 'AI Roles & Responsibilities', status: 'Completed', score: 85 },
        { id: 'A.4', name: 'Resource Management', status: 'In Progress', score: 70 },
        { id: 'A.5', name: 'Impact Assessment', status: 'Completed', score: 88 },
        { id: 'A.6', name: 'Development & Deployment', status: 'In Progress', score: 65 },
        { id: 'A.7', name: 'Operation & Monitoring', status: 'Pending', score: 0 },
        { id: 'A.8', name: 'Performance Evaluation', status: 'Pending', score: 0 },
        { id: 'A.9', name: 'Improvement', status: 'Pending', score: 0 }
      ],
      documents: [
        { name: 'AI Policy Document', status: 'Approved', date: '2024-01-10' },
        { name: 'Risk Assessment Report', status: 'Under Review', date: '2024-01-15' },
        { name: 'Training Records', status: 'Pending', date: null }
      ]
    },
    {
      id: 2,
      name: 'ISO 27001:2022 Information Security',
      status: 'Certified',
      progress: 100,
      issuer: 'International Organization for Standardization',
      validFrom: '2023-06-01',
      validUntil: '2026-06-01',
      lastAssessment: '2023-12-15',
      nextAssessment: '2024-06-15',
      requirements: [
        { id: 'A.5', name: 'Information Security Policies', status: 'Completed', score: 95 },
        { id: 'A.6', name: 'Organization of Information Security', status: 'Completed', score: 92 },
        { id: 'A.7', name: 'Human Resource Security', status: 'Completed', score: 88 },
        { id: 'A.8', name: 'Asset Management', status: 'Completed', score: 90 },
        { id: 'A.9', name: 'Access Control', status: 'Completed', score: 94 },
        { id: 'A.10', name: 'Cryptography', status: 'Completed', score: 87 },
        { id: 'A.11', name: 'Physical and Environmental Security', status: 'Completed', score: 91 },
        { id: 'A.12', name: 'Operations Security', status: 'Completed', score: 89 }
      ],
      documents: [
        { name: 'Security Policy', status: 'Approved', date: '2023-05-15' },
        { name: 'Risk Register', status: 'Approved', date: '2023-05-20' },
        { name: 'Incident Response Plan', status: 'Approved', date: '2023-05-25' }
      ]
    },
    {
      id: 3,
      name: 'ISO 9001:2015 Quality Management',
      status: 'Renewal Required',
      progress: 85,
      issuer: 'International Organization for Standardization',
      validFrom: '2021-03-01',
      validUntil: '2024-03-01',
      lastAssessment: '2023-09-15',
      nextAssessment: '2024-02-15',
      requirements: [
        { id: '4', name: 'Context of the Organization', status: 'Completed', score: 92 },
        { id: '5', name: 'Leadership', status: 'Completed', score: 88 },
        { id: '6', name: 'Planning', status: 'Completed', score: 85 },
        { id: '7', name: 'Support', status: 'In Progress', score: 78 },
        { id: '8', name: 'Operation', status: 'Completed', score: 90 },
        { id: '9', name: 'Performance Evaluation', status: 'In Progress', score: 82 },
        { id: '10', name: 'Improvement', status: 'Pending', score: 75 }
      ],
      documents: [
        { name: 'Quality Manual', status: 'Under Review', date: '2023-12-01' },
        { name: 'Process Documentation', status: 'Approved', date: '2023-11-15' },
        { name: 'Audit Reports', status: 'Approved', date: '2023-09-15' }
      ]
    }
  ];

  useEffect(() => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setCertifications(demoCertifications);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'certified': return '#10b981';
      case 'in progress': return '#f59e0b';
      case 'renewal required': return '#ef4444';
      case 'expired': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'certified': return '✅';
      case 'in progress': return '🔄';
      case 'renewal required': return '⚠️';
      case 'expired': return '❌';
      default: return '📋';
    }
  };

  const getRequirementStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'completed': return '#10b981';
      case 'in progress': return '#f59e0b';
      case 'pending': return '#6b7280';
      case 'under review': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const calculateDaysUntilExpiry = (validUntil) => {
    const today = new Date();
    const expiryDate = new Date(validUntil);
    const diffTime = expiryDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <div className="certifications">
        <div className="certifications-header">
          <button className="back-btn" onClick={onBack}>
            ← Back to Dashboard
          </button>
          <h2>Certifications</h2>
        </div>
        <div className="loading-state">
          <div className="loading-spinner">Loading certifications...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="certifications">
      <div className="certifications-header">
        <button className="back-btn" onClick={onBack}>
          ← Back to Dashboard
        </button>
        <div className="header-content">
          <h2>ISO 42001 Certifications</h2>
          <p>Track your certification status and compliance requirements</p>
        </div>
        <button className="add-cert-btn">
          + Add Certification
        </button>
      </div>

      <div className="certifications-overview">
        <div className="overview-stats">
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-number">
                {certifications.filter(cert => cert.status === 'Certified').length}
              </div>
              <div className="stat-label">Certified</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🔄</div>
            <div className="stat-content">
              <div className="stat-number">
                {certifications.filter(cert => cert.status === 'In Progress').length}
              </div>
              <div className="stat-label">In Progress</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⚠️</div>
            <div className="stat-content">
              <div className="stat-number">
                {certifications.filter(cert => cert.status === 'Renewal Required').length}
              </div>
              <div className="stat-label">Renewal Required</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-number">
                {Math.round(certifications.reduce((acc, cert) => acc + cert.progress, 0) / certifications.length)}%
              </div>
              <div className="stat-label">Average Progress</div>
            </div>
          </div>
        </div>
      </div>

      <div className="certifications-grid">
        {certifications.map(cert => (
          <div key={cert.id} className="certification-card">
            <div className="cert-header">
              <div className="cert-info">
                <h3>{cert.name}</h3>
                <div className="cert-issuer">{cert.issuer}</div>
              </div>
              <div className="cert-status">
                <span 
                  className="status-badge"
                  style={{ 
                    backgroundColor: `${getStatusColor(cert.status)}20`,
                    color: getStatusColor(cert.status)
                  }}
                >
                  {getStatusIcon(cert.status)} {cert.status}
                </span>
              </div>
            </div>

            <div className="cert-progress">
              <div className="progress-header">
                <span>Progress</span>
                <span className="progress-percentage">{cert.progress}%</span>
              </div>
              <div className="progress-bar-container">
                <div 
                  className="progress-bar"
                  style={{ 
                    width: `${cert.progress}%`,
                    backgroundColor: getStatusColor(cert.status)
                  }}
                ></div>
              </div>
            </div>

            <div className="cert-dates">
              <div className="date-item">
                <label>Valid From</label>
                <span>{new Date(cert.validFrom).toLocaleDateString()}</span>
              </div>
              <div className="date-item">
                <label>Valid Until</label>
                <span>{new Date(cert.validUntil).toLocaleDateString()}</span>
              </div>
              <div className="date-item">
                <label>Days Until Expiry</label>
                <span className={calculateDaysUntilExpiry(cert.validUntil) < 90 ? 'expiry-warning' : ''}>
                  {calculateDaysUntilExpiry(cert.validUntil)} days
                </span>
              </div>
            </div>

            <div className="cert-requirements">
              <div className="requirements-header">Requirements Status</div>
              <div className="requirements-grid">
                {cert.requirements.slice(0, 4).map(req => (
                  <div key={req.id} className="requirement-item">
                    <div className="req-id">{req.id}</div>
                    <div className="req-info">
                      <div className="req-name">{req.name}</div>
                      <div 
                        className="req-status"
                        style={{ color: getRequirementStatusColor(req.status) }}
                      >
                        {req.status}
                      </div>
                    </div>
                    <div className="req-score">{req.score}%</div>
                  </div>
                ))}
                {cert.requirements.length > 4 && (
                  <div className="more-requirements">
                    +{cert.requirements.length - 4} more
                  </div>
                )}
              </div>
            </div>

            <div className="cert-actions">
              <button 
                className="view-details-btn"
                onClick={() => setSelectedCert(cert)}
              >
                📋 View Details
              </button>
              <button className="download-cert-btn">
                📄 Download Certificate
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedCert && (
        <div className="cert-modal-overlay" onClick={() => setSelectedCert(null)}>
          <div className="cert-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedCert.name}</h3>
              <button 
                className="close-btn"
                onClick={() => setSelectedCert(null)}
              >
                ×
              </button>
            </div>
            <div className="modal-content">
              <div className="cert-overview">
                <div className="overview-grid">
                  <div className="overview-item">
                    <label>Status</label>
                    <span style={{ color: getStatusColor(selectedCert.status) }}>
                      {getStatusIcon(selectedCert.status)} {selectedCert.status}
                    </span>
                  </div>
                  <div className="overview-item">
                    <label>Progress</label>
                    <span>{selectedCert.progress}%</span>
                  </div>
                  <div className="overview-item">
                    <label>Last Assessment</label>
                    <span>{new Date(selectedCert.lastAssessment).toLocaleDateString()}</span>
                  </div>
                  <div className="overview-item">
                    <label>Next Assessment</label>
                    <span>{new Date(selectedCert.nextAssessment).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              <div className="detailed-requirements">
                <h4>All Requirements</h4>
                {selectedCert.requirements.map(req => (
                  <div key={req.id} className="detailed-requirement">
                    <div className="req-header">
                      <span className="req-id-large">{req.id}</span>
                      <span className="req-name-large">{req.name}</span>
                      <span 
                        className="req-score-large"
                        style={{ color: getRequirementStatusColor(req.status) }}
                      >
                        {req.score}%
                      </span>
                    </div>
                    <div className="req-progress">
                      <div 
                        className="req-progress-bar"
                        style={{ 
                          width: `${req.score}%`,
                          backgroundColor: getRequirementStatusColor(req.status)
                        }}
                      ></div>
                    </div>
                    <div className="req-status-detail">
                      Status: <span style={{ color: getRequirementStatusColor(req.status) }}>
                        {req.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="cert-documents">
                <h4>Required Documents</h4>
                <div className="documents-list">
                  {selectedCert.documents.map((doc, index) => (
                    <div key={index} className="document-item">
                      <div className="doc-info">
                        <span className="doc-name">{doc.name}</span>
                        {doc.date && (
                          <span className="doc-date">{new Date(doc.date).toLocaleDateString()}</span>
                        )}
                      </div>
                      <span 
                        className="doc-status"
                        style={{ color: getRequirementStatusColor(doc.status) }}
                      >
                        {doc.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="modal-actions">
              <button className="download-report-btn">
                📊 Download Progress Report
              </button>
              <button className="schedule-assessment-btn">
                📅 Schedule Assessment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Certifications;

