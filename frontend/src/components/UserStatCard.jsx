import React from 'react';

const UserStatCard = ({ icon, label, value, color, className }) => {
  return (
    <div className={`stat-card ${className}`}>
      <div className="icon-background" style={{ backgroundColor: color ? `${color}20` : 'var(--accent-color-transparent)' }}>
        {React.cloneElement(icon, { style: { color: color || 'var(--accent-color)' } })}
      </div>
      <div className="stat-card-content">
        <span>{label}</span>
        <h3 style={{ color: color || 'var(--accent-color)' }}>{value}</h3>
      </div>
    </div>
  );
};

export default UserStatCard;