import { useState, useEffect } from 'react';
import apiService from '../services/api.js';

const AIModelRegistry = ({ user, onBack }) => {
  const [models, setModels] = useState([]);
  const [clients, setClients] = useState([]);
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
    monitoring_enabled: false,
    client_id: '' // Added client selection
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
    { value: 'retired', label: 'Retired', color: '#ef4444' }
  ];

  // Load clients on component mount
  useEffect(() => {
    loadClients();
    loadModels();
  }, []);

  const loadClients = async () => {
    try {
      const response = await apiService.get('/api/v1/clients');
      setClients(response || []);
    } catch (error) {
      console.error('Failed to load clients:', error);
      setError('Failed to load clients');
    }
  };

  const loadModels = async () => {
    setLoading(true);
    try {
      // Mock data for now since we don't have models endpoint yet
      const mockModels = [
        {
          id: 1,
          name: 'Customer Sentiment Analyzer',
          version: '2.1.0',
          model_type: 'Natural Language Processing',
          framework: 'TensorFlow',
          risk_level: 'medium',
          status: 'production',
          compliance_score: 85,
          created_date: '1/15/2024',
          client_name: 'Acme Corporation'
        },
        {
          id: 2,
          name: 'Fraud Detection System',
          version: '1.5.2',
          model_type: 'Machine Learning',
          framework: 'Scikit-learn',
          risk_level: 'high',
          status: 'production',
          compliance_score: 92,
          created_date: '11/20/2023',
          client_name: 'TechStart Inc'
        },
        {
          id: 3,
          name: 'Product Recommendation Engine',
          version: '3.0.1',
          model_type: 'Recommendation System',
          framework: 'PyTorch',
          risk_level: 'low',
          status: 'staging',
          compliance_score: 78,
          created_date: '8/10/2024',
          client_name: 'Global Industries'
        }
      ];
      setModels(mockModels);
    } catch (error) {
      setError('Failed to load models');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate client selection
      if (!formData.client_id) {
        setError('Please select a client');
        setLoading(false);
        return;
      }

      // Find selected client name
      const selectedClient = clients.find(c => c.id === parseInt(formData.client_id));
      
      // For now, just add to local state since we don't have backend endpoint
      const newModel = {
        id: models.length + 1,
        ...formData,
        client_name: selectedClient ? selectedClient.name : 'Unknown Client',
        status: 'development',
        compliance_score: 0,
        created_date: new Date().toLocaleDateString()
      };

      setModels([...models, newModel]);
      setShowForm(false);
      resetForm();
      
      // TODO: Replace with actual API call when backend endpoint is ready
      // await apiService.post('/models', formData);
      
    } catch (error) {
      setError('Failed to register model');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
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
      monitoring_enabled: false,
      client_id: ''
    });
    setEditingModel(null);
  };

  const handleEdit = (model) => {
    setFormData({
      name: model.name,
      description: model.description || '',
      version: model.version,
      model_type: model.model_type.toLowerCase().replace(' ', '_'),
      framework: model.framework || '',
      algorithm: model.algorithm || '',
      business_purpose: model.business_purpose || '',
      risk_level: model.risk_level,
      data_classification: model.data_classification || 'internal',
      monitoring_enabled: model.monitoring_enabled || false,
      client_id: model.client_id || ''
    });
    setEditingModel(model);
    setShowForm(true);
  };

  const handleDelete = async (modelId) => {
    if (window.confirm('Are you sure you want to delete this model?')) {
      try {
        setModels(models.filter(m => m.id !== modelId));
        // TODO: Replace with actual API call
        // await apiService.delete(`/models/${modelId}`);
      } catch (error) {
        setError('Failed to delete model');
      }
    }
  };

  const getRiskColor = (riskLevel) => {
    const risk = riskLevels.find(r => r.value === riskLevel);
    return risk ? risk.color : '#6b7280';
  };

  const getStatusColor = (status) => {
    const statusOption = statusOptions.find(s => s.value === status);
    return statusOption ? statusOption.color : '#6b7280';
  };

  if (showForm) {
    return (
      <div className="ai-model-registry">
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{editingModel ? 'Edit AI Model' : 'Register New AI Model'}</h2>
              <button 
                className="close-button"
                onClick={() => {
                  setShowForm(false);
                  resetForm();
                }}
              >
                ×
              </button>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

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
                  <label htmlFor="client_id">Client *</label>
                  <select
                    id="client_id"
                    value={formData.client_id}
                    onChange={(e) => setFormData({...formData, client_id: e.target.value})}
                    required
                  >
                    <option value="">Select a client...</option>
                    {clients.map(client => (
                      <option key={client.id} value={client.id}>
                        {client.name}
                      </option>
                    ))}
                  </select>
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
                    {riskLevels.map(level => (
                      <option key={level.value} value={level.value}>
                        {level.label}
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

                <div className="form-group full-width">
                  <label htmlFor="description">Description</label>
                  <textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    placeholder="Describe the purpose and functionality of this AI model"
                    rows="3"
                  />
                </div>

                <div className="form-group full-width">
                  <label htmlFor="business_purpose">Business Purpose</label>
                  <textarea
                    id="business_purpose"
                    value={formData.business_purpose}
                    onChange={(e) => setFormData({...formData, business_purpose: e.target.value})}
                    placeholder="Explain how this model supports business objectives"
                    rows="3"
                  />
                </div>

                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={formData.monitoring_enabled}
                      onChange={(e) => setFormData({...formData, monitoring_enabled: e.target.checked})}
                    />
                    Enable Performance Monitoring
                  </label>
                </div>
              </div>

              <div className="form-actions">
                <button 
                  type="submit" 
                  className="submit-button"
                  disabled={loading}
                >
                  {loading ? 'Registering...' : (editingModel ? 'Update Model' : 'Register Model')}
                </button>
                <button 
                  type="button" 
                  className="cancel-button"
                  onClick={() => {
                    setShowForm(false);
                    resetForm();
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-model-registry">
      <div className="page-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Dashboard
        </button>
        <div className="header-content">
          <h1>AI Model Registry</h1>
          <p>Manage your organization's AI models and their compliance status</p>
        </div>
        <button 
          className="primary-button"
          onClick={() => setShowForm(true)}
        >
          + Register New Model
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading models...</div>
      ) : (
        <div className="models-grid">
          {models.map(model => (
            <div key={model.id} className="model-card">
              <div className="model-header">
                <h3>{model.name}</h3>
                <div className="model-actions">
                  <button 
                    className="edit-button"
                    onClick={() => handleEdit(model)}
                    title="Edit Model"
                  >
                    ✏️
                  </button>
                  <button 
                    className="delete-button"
                    onClick={() => handleDelete(model.id)}
                    title="Delete Model"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              
              <p className="model-description">
                {model.model_type} model for {model.description || 'AI processing'}
              </p>
              
              <div className="model-details">
                <div className="detail-row">
                  <span className="label">Client:</span>
                  <span className="value">{model.client_name}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Version:</span>
                  <span className="value">{model.version}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Type:</span>
                  <span className="value">{model.model_type}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Framework:</span>
                  <span className="value">{model.framework}</span>
                </div>
              </div>

              <div className="model-status">
                <span 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(model.status) }}
                >
                  {model.status.toUpperCase()}
                </span>
                <span 
                  className="risk-badge"
                  style={{ backgroundColor: getRiskColor(model.risk_level) }}
                >
                  {model.risk_level.toUpperCase()} RISK
                </span>
              </div>

              <div className="compliance-section">
                <div className="compliance-header">
                  <span className="label">Risk Score:</span>
                  <span className="score">{model.compliance_score || 65}%</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${model.compliance_score || 65}%`,
                      backgroundColor: model.compliance_score >= 80 ? '#10b981' : 
                                     model.compliance_score >= 60 ? '#f59e0b' : '#ef4444'
                    }}
                  />
                </div>
                
                <div className="compliance-header">
                  <span className="label">Compliance:</span>
                  <span className="score">{model.compliance_score >= 80 ? 92 : 
                                          model.compliance_score >= 60 ? 85 : 78}%</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${model.compliance_score >= 80 ? 92 : 
                              model.compliance_score >= 60 ? 85 : 78}%`,
                      backgroundColor: '#10b981'
                    }}
                  />
                </div>
              </div>

              <div className="model-footer">
                <span className="created-date">Created: {model.created_date}</span>
                <span className="monitoring-status">
                  📊 Monitored
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {models.length === 0 && !loading && (
        <div className="empty-state">
          <h3>No AI Models Registered</h3>
          <p>Start by registering your first AI model to track its compliance status.</p>
          <button 
            className="primary-button"
            onClick={() => setShowForm(true)}
          >
            Register Your First Model
          </button>
        </div>
      )}
    </div>
  );
};

export default AIModelRegistry;

