import React, { useState, useEffect } from 'react';
import './CreateProjectForm.css';

const CreateProjectForm = ({ onClose, onSuccess }) => {
  const [clients, setClients] = useState([]);
  const [formData, setFormData] = useState({
    client_id: '',
    project_name: '',
    ai_system_name: '',
    risk_template: 'medium',
    target_completion_date: '',
    description: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await fetch('/api/admin/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      if (response.ok) {
        const clientsData = await response.json();
        setClients(clientsData);
      }
    } catch (error) {
      console.error('Error fetching clients:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Auto-generate project name when client is selected
    if (name === 'client_id' && value) {
      const selectedClient = clients.find(client => client.id === parseInt(value));
      if (selectedClient && !formData.project_name) {
        setFormData(prev => ({
          ...prev,
          project_name: `ISO 42001 Compliance for ${selectedClient.organization || selectedClient.name}`
        }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // For now, use mock success since backend endpoints may not be ready
      // TODO: Replace with actual API call when backend is implemented
      // const response = await fetch('/api/admin/projects', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      //   },
      //   body: JSON.stringify(formData)
      // });

      // if (!response.ok) {
      //   throw new Error('Failed to create project');
      // }

      // const newProject = await response.json();

      // Mock successful project creation
      const newProject = {
        id: Date.now(),
        ...formData,
        compliance_score: 0,
        completion_percentage: 0,
        created_at: new Date().toISOString(),
        status: 'active'
      };

      onSuccess(newProject);
      onClose();
    } catch (error) {
      console.error('Error creating project:', error);
      setError('Failed to create project. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskDescription = (riskLevel) => {
    switch (riskLevel) {
      case 'high':
        return 'All 32 controls - Comprehensive assessment for high-risk AI systems';
      case 'medium':
        return '24 controls - Standard assessment for moderate-risk AI systems';
      case 'low':
        return '16 controls - Basic assessment for low-risk AI systems';
      default:
        return '';
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Create New Project</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="create-project-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="client_id">Select Client *</label>
            <select
              id="client_id"
              name="client_id"
              value={formData.client_id}
              onChange={handleInputChange}
              required
              disabled={loading}
            >
              <option value="">Choose a client...</option>
              {clients.map(client => (
                <option key={client.id} value={client.id}>
                  {client.name} ({client.email}) - {client.organization}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="project_name">Project Name *</label>
            <input
              type="text"
              id="project_name"
              name="project_name"
              value={formData.project_name}
              onChange={handleInputChange}
              required
              disabled={loading}
              placeholder="ISO 42001 Compliance Project"
            />
          </div>

          <div className="form-group">
            <label htmlFor="ai_system_name">AI System Name</label>
            <input
              type="text"
              id="ai_system_name"
              name="ai_system_name"
              value={formData.ai_system_name}
              onChange={handleInputChange}
              disabled={loading}
              placeholder="Name of the AI system being assessed"
            />
          </div>

          <div className="form-group">
            <label htmlFor="risk_template">Risk Template *</label>
            <select
              id="risk_template"
              name="risk_template"
              value={formData.risk_template}
              onChange={handleInputChange}
              required
              disabled={loading}
            >
              <option value="high">High Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="low">Low Risk</option>
            </select>
            <small className="form-help">
              {getRiskDescription(formData.risk_template)}
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="target_completion_date">Target Completion Date</label>
            <input
              type="date"
              id="target_completion_date"
              name="target_completion_date"
              value={formData.target_completion_date}
              onChange={handleInputChange}
              disabled={loading}
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Project Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              disabled={loading}
              placeholder="Brief description of the compliance project and objectives"
              rows="3"
            />
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading || !formData.client_id}
            >
              {loading ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateProjectForm;

