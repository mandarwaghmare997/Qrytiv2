import React, { useState, useEffect } from 'react';
import apiService from '../services/api.js';

const AIModelRegistry = ({ user, onBack }) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingModel, setEditingModel] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    version: '',
    model_type: 'machine_learning',
    framework: '',
    algorithm: '',
    business_purpose: '',
    risk_level: 'medium',
    data_classification: 'internal',
    monitoring_enabled: false
  });

  // Model types and risk levels
  const modelTypes = [
    { value: 'machine_learning', label: 'Machine Learning' },
    { value: 'deep_learning', label: 'Deep Learning' },
    { value: 'natural_language', label: 'Natural Language Processing' },
    { value: 'computer_vision', label: 'Computer Vision' },
    { value: 'recommendation', label: 'Recommendation System' },
    { value: 'predictive_analytics', label: 'Predictive Analytics' },
    { value: 'generative_ai', label: 'Generative AI' },
    { value: 'decision_support', label: 'Decision Support' },
    { value: 'other', label: 'Other' }
  ];

  const riskLevels = [
    { value: 'minimal', label: 'Minimal', color: '#10b981' },
    { value: 'low', label: 'Low', color: '#3b82f6' },
    { value: 'medium', label: 'Medium', color: '#f59e0b' },
    { value: 'high', label: 'High', color: '#ef4444' },
    { value: 'critical', label: 'Critical', color: '#dc2626' }
  ];

  const statusOptions = [
    { value: 'development', label: 'Development', color: '#6b7280' },
    { value: 'testing', label: 'Testing', color: '#f59e0b' },
    { value: 'staging', label: 'Staging', color: '#3b82f6' },
    { value: 'production', label: 'Production', color: '#10b981' },
    { value: 'deprecated', label: 'Deprecated', color: '#ef4444' },
    { value: 'retired', label: 'Retired', color: '#6b7280' }
  ];

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      // For now, use mock data since backend endpoint isn't implemented yet
      const mockModels = [
        {
          id: 1,
          name: 'Customer Sentiment Analyzer',
          description: 'NLP model for analyzing customer feedback sentiment',
          version: '2.1.0',
          model_type: 'natural_language',
          framework: 'TensorFlow',
          algorithm: 'BERT',
          status: 'production',
          risk_level: 'medium',
          risk_score: 65,
          compliance_score: 85,
          business_purpose: 'Analyze customer feedback to improve service quality',
          monitoring_enabled: true,
          created_date: '2024-01-15T10:30:00Z'
        },
        {
          id: 2,
          name: 'Fraud Detection System',
          description: 'ML model for detecting fraudulent transactions',
          version: '1.5.2',
          model_type: 'machine_learning',
          framework: 'Scikit-learn',
          algorithm: 'Random Forest',
          status: 'production',
          risk_level: 'high',
          risk_score: 85,
          compliance_score: 92,
          business_purpose: 'Detect and prevent fraudulent financial transactions',
          monitoring_enabled: true,
          created_date: '2023-11-20T14:15:00Z'
        },
        {
          id: 3,
          name: 'Product Recommendation Engine',
          description: 'Collaborative filtering model for product recommendations',
          version: '3.0.1',
          model_type: 'recommendation',
          framework: 'PyTorch',
          algorithm: 'Neural Collaborative Filtering',
          status: 'staging',
          risk_level: 'low',
          risk_score: 35,
          compliance_score: 78,
          business_purpose: 'Provide personalized product recommendations to customers',
          monitoring_enabled: false,
          created_date: '2024-02-10T09:45:00Z'
        }
      ];
      setModels(mockModels);
    } catch (error) {
      setError('Failed to load AI models');
      console.error('Error loading models:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (editingModel) {
        // Update existing model
        const updatedModel = { ...editingModel, ...formData };
        setModels(models.map(m => m.id === editingModel.id ? updatedModel : m));
      } else {
        // Create new model
        const newModel = {
          id: Date.now(), // Mock ID
          ...formData,
          status: 'development',
          risk_score: 0,
          compliance_score: 0,
          created_date: new Date().toISOString(),
          monitoring_enabled: formData.monitoring_enabled
        };
        setModels([...models, newModel]);
      }

      // Reset form
      setFormData({
        name: '',
        description: '',
        version: '',
        model_type: 'machine_learning',
        framework: '',
        algorithm: '',
        business_purpose: '',
        risk_level: 'medium',
        data_classification: 'internal',
        monitoring_enabled: false
      });
      setShowForm(false);
      setEditingModel(null);
    } catch (error) {
      setError('Failed to save model');
      console.error('Error saving model:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (model) => {
    setEditingModel(model);
    setFormData({
      name: model.name,
      description: model.description,
      version: model.version,
      model_type: model.model_type,
      framework: model.framework || '',
      algorithm: model.algorithm || '',
      business_purpose: model.business_purpose || '',
      risk_level: model.risk_level,
      data_classification: model.data_classification || 'internal',
      monitoring_enabled: model.monitoring_enabled || false
    });
    setShowForm(true);
  };

  const handleDelete = (modelId) => {
    if (window.confirm('Are you sure you want to delete this AI model?')) {
      setModels(models.filter(m => m.id !== modelId));
    }
  };

  const getRiskColor = (riskLevel) => {
    const risk = riskLevels.find(r => r.value === riskLevel);
    return risk ? risk.color : '#6b7280';
  };

  const getStatusColor = (status) => {
    const statusObj = statusOptions.find(s => s.value === status);
    return statusObj ? statusObj.color : '#6b7280';
  };

  if (showForm) {
    return (
      <div className="ai-model-form">
        <div className="form-header">
          <h2>{editingModel ? 'Edit AI Model' : 'Register New AI Model'}</h2>
          <button 
            onClick={() => {
              setShowForm(false);
              setEditingModel(null);
              setFormData({
                name: '',
                description: '',
                version: '',
                model_type: 'machine_learning',
                framework: '',
                algorithm: '',
                business_purpose: '',
                risk_level: 'medium',
                data_classification: 'internal',
                monitoring_enabled: false
              });
            }}
            className="close-button"
          >
            ×
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="model-form">
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="name">Model Name *</label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
                placeholder="e.g., Customer Sentiment Analyzer"
              />
            </div>

            <div className="form-group">
              <label htmlFor="version">Version *</label>
              <input
                type="text"
                id="version"
                value={formData.version}
                onChange={(e) => setFormData({...formData, version: e.target.value})}
                required
                placeholder="e.g., 1.0.0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="model_type">Model Type *</label>
              <select
                id="model_type"
                value={formData.model_type}
                onChange={(e) => setFormData({...formData, model_type: e.target.value})}
                required
              >
                {modelTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="risk_level">Risk Level *</label>
              <select
                id="risk_level"
                value={formData.risk_level}
                onChange={(e) => setFormData({...formData, risk_level: e.target.value})}
                required
              >
                {riskLevels.map(risk => (
                  <option key={risk.value} value={risk.value}>
                    {risk.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="framework">Framework</label>
              <input
                type="text"
                id="framework"
                value={formData.framework}
                onChange={(e) => setFormData({...formData, framework: e.target.value})}
                placeholder="e.g., TensorFlow, PyTorch, Scikit-learn"
              />
            </div>

            <div className="form-group">
              <label htmlFor="algorithm">Algorithm</label>
              <input
                type="text"
                id="algorithm"
                value={formData.algorithm}
                onChange={(e) => setFormData({...formData, algorithm: e.target.value})}
                placeholder="e.g., Random Forest, Neural Network, BERT"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows="3"
              placeholder="Describe the purpose and functionality of this AI model"
            />
          </div>

          <div className="form-group">
            <label htmlFor="business_purpose">Business Purpose</label>
            <textarea
              id="business_purpose"
              value={formData.business_purpose}
              onChange={(e) => setFormData({...formData, business_purpose: e.target.value})}
              rows="2"
              placeholder="Explain how this model supports business objectives"
            />
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={formData.monitoring_enabled}
                onChange={(e) => setFormData({...formData, monitoring_enabled: e.target.checked})}
              />
              Enable Performance Monitoring
            </label>
          </div>

          <div className="form-actions">
            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Saving...' : (editingModel ? 'Update Model' : 'Register Model')}
            </button>
            <button 
              type="button" 
              onClick={() => setShowForm(false)}
              className="cancel-button"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="ai-model-registry">
      <div className="registry-header">
        <div className="header-left">
          <button onClick={onBack} className="back-button">
            ← Back to Dashboard
          </button>
          <h2>AI Model Registry</h2>
          <p>Manage your organization's AI models and their compliance status</p>
        </div>
        <button 
          onClick={() => setShowForm(true)}
          className="add-model-button"
        >
          + Register New Model
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading && <div className="loading">Loading AI models...</div>}

      <div className="models-grid">
        {models.map(model => (
          <div key={model.id} className="model-card">
            <div className="model-header">
              <h3>{model.name}</h3>
              <div className="model-actions">
                <button 
                  onClick={() => handleEdit(model)}
                  className="edit-button"
                  title="Edit Model"
                >
                  ✏️
                </button>
                <button 
                  onClick={() => handleDelete(model.id)}
                  className="delete-button"
                  title="Delete Model"
                >
                  🗑️
                </button>
              </div>
            </div>

            <div className="model-info">
              <p className="model-description">{model.description}</p>
              
              <div className="model-meta">
                <div className="meta-item">
                  <span className="meta-label">Version:</span>
                  <span className="meta-value">{model.version}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Type:</span>
                  <span className="meta-value">
                    {modelTypes.find(t => t.value === model.model_type)?.label || model.model_type}
                  </span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Framework:</span>
                  <span className="meta-value">{model.framework || 'Not specified'}</span>
                </div>
              </div>

              <div className="model-status">
                <div className="status-item">
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(model.status) }}
                  >
                    {statusOptions.find(s => s.value === model.status)?.label || model.status}
                  </span>
                </div>
                <div className="status-item">
                  <span 
                    className="risk-badge"
                    style={{ backgroundColor: getRiskColor(model.risk_level) }}
                  >
                    {riskLevels.find(r => r.value === model.risk_level)?.label || model.risk_level} Risk
                  </span>
                </div>
              </div>

              <div className="model-scores">
                <div className="score-item">
                  <span className="score-label">Risk Score:</span>
                  <div className="score-bar">
                    <div 
                      className="score-fill risk-score"
                      style={{ width: `${model.risk_score}%` }}
                    ></div>
                    <span className="score-text">{model.risk_score}%</span>
                  </div>
                </div>
                <div className="score-item">
                  <span className="score-label">Compliance:</span>
                  <div className="score-bar">
                    <div 
                      className="score-fill compliance-score"
                      style={{ width: `${model.compliance_score}%` }}
                    ></div>
                    <span className="score-text">{model.compliance_score}%</span>
                  </div>
                </div>
              </div>

              <div className="model-footer">
                <span className="created-date">
                  Created: {new Date(model.created_date).toLocaleDateString()}
                </span>
                {model.monitoring_enabled && (
                  <span className="monitoring-badge">📊 Monitored</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {models.length === 0 && !loading && (
        <div className="empty-state">
          <h3>No AI Models Registered</h3>
          <p>Start by registering your first AI model to begin compliance tracking.</p>
          <button 
            onClick={() => setShowForm(true)}
            className="add-model-button"
          >
            Register Your First Model
          </button>
        </div>
      )}
    </div>
  );
};

export default AIModelRegistry;

