import React from 'react';
import './DeleteConfirmModal.css';

const DeleteConfirmModal = ({ target, onConfirm, onCancel }) => {
  if (!target) return null;

  const { type, item } = target;
  const itemName = type === 'client' ? item.name : item.name;
  const itemType = type === 'client' ? 'client' : 'project';

  return (
    <div className="modal-overlay">
      <div className="delete-modal">
        <div className="modal-header">
          <div className="warning-icon">⚠️</div>
          <h3>Confirm Deletion</h3>
        </div>
        
        <div className="modal-content">
          <p>
            Are you sure you want to delete this {itemType}?
          </p>
          <div className="item-info">
            <strong>{itemName}</strong>
            {type === 'client' && item.organization && (
              <span className="organization">({item.organization})</span>
            )}
          </div>
          {type === 'client' && (
            <div className="warning-text">
              <strong>Warning:</strong> This will also delete all associated projects and data.
              This action cannot be undone.
            </div>
          )}
        </div>
        
        <div className="modal-actions">
          <button 
            className="cancel-btn"
            onClick={onCancel}
          >
            Cancel
          </button>
          <button 
            className="delete-btn"
            onClick={onConfirm}
          >
            Delete {itemType}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmModal;

