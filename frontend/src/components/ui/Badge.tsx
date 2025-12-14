import React from 'react';

interface BadgeProps {
  status: 'running' | 'stopped' | 'error' | 'unknown' | 'success' | 'warning';
  children: React.ReactNode;
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ status, children, className = '' }) => {
  const statusClasses = {
    running: 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200',
    success: 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200',
    stopped: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    error: 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-200',
    warning: 'bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-200',
    unknown: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClasses[status]} ${className}`}>
      <span className={`w-2 h-2 mr-1.5 rounded-full ${status === 'running' || status === 'success' ? 'bg-success-500 animate-pulse' : status === 'error' ? 'bg-danger-500' : 'bg-gray-400'}`}></span>
      {children}
    </span>
  );
};

export default Badge;
