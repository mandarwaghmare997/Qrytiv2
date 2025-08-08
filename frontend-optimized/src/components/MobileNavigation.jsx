import React from 'react';

const MobileNavigation = ({ currentView, onNavigate, user }) => {
  const navItems = [
    { id: 'dashboard', icon: '🏠', label: 'Home' },
    { id: 'ai-models', icon: '🤖', label: 'Models' },
    { id: 'gap-assessment', icon: '🎯', label: 'Assessment' },
    { id: 'compliance-reports', icon: '📊', label: 'Reports' },
    { id: 'certifications', icon: '🏆', label: 'Certs' }
  ];

  return (
    <div className="mobile-nav">
      <div className="mobile-nav-items">
        {navItems.map(item => (
          <button
            key={item.id}
            className={`mobile-nav-item ${currentView === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <div className="mobile-nav-icon">{item.icon}</div>
            <div className="mobile-nav-label">{item.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default MobileNavigation;

