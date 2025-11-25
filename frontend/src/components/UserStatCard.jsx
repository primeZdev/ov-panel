import React from 'react';

const UserStatCard = ({ icon, label, value, color, className }) => {
  return (
    <div
      className={`user-stat-card ${className || ''}`}
      style={{
        background: '#23272a',
        borderRadius: '14px',
        boxShadow: '0 2px 12px #0004',
        color: '#fff',
        minWidth: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        padding: '18px 22px',
        flex: '1 1 220px',
        marginBottom: '12px',
      }}
    >
      <div className="user-stat-icon" style={{ fontSize: 28, marginBottom: 8, color }}>{icon}</div>
      <div className="user-stat-info" style={{ display: 'flex', flexDirection: 'column' }}>
        <div className="user-stat-label" style={{ fontWeight: 500, fontSize: '1.08em', marginBottom: 2, color: '#bbb' }}>{label}</div>
        <div className="user-stat-value" style={{ fontWeight: 700, fontSize: '1.18em' }}>{value}</div>
      </div>
    </div>
  );
};

export default UserStatCard;