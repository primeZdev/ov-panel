import React from 'react';

const LoadingButton = ({ isLoading, onClick, className, children }) => {
  return (
    <button
      onClick={onClick}
      className={`btn ${className}`}
      disabled={isLoading}
      style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
    >
      {isLoading && (
        <div className="spinner" style={{ marginRight: '8px' }}></div>
      )}
      {children}
    </button>
  );
};

export default LoadingButton;
