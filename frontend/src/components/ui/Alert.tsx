import React from 'react';
import { AlertCircle, CheckCircle, Info, AlertTriangle, X } from 'lucide-react';

interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

const Alert: React.FC<AlertProps> = ({ type, title, children, onClose, className = '' }) => {
  const typeConfig = {
    success: {
      bgClass: 'bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800',
      textClass: 'text-success-800 dark:text-success-200',
      icon: CheckCircle,
    },
    error: {
      bgClass: 'bg-danger-50 dark:bg-danger-900/20 border-danger-200 dark:border-danger-800',
      textClass: 'text-danger-800 dark:text-danger-200',
      icon: AlertCircle,
    },
    warning: {
      bgClass: 'bg-warning-50 dark:bg-warning-900/20 border-warning-200 dark:border-warning-800',
      textClass: 'text-warning-800 dark:text-warning-200',
      icon: AlertTriangle,
    },
    info: {
      bgClass: 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800',
      textClass: 'text-primary-800 dark:text-primary-200',
      icon: Info,
    },
  };

  const { bgClass, textClass, icon: Icon } = typeConfig[type];

  return (
    <div className={`border rounded-lg p-4 ${bgClass} ${className}`}>
      <div className="flex items-start">
        <Icon className={`w-5 h-5 ${textClass} mr-3 flex-shrink-0 mt-0.5`} />
        <div className="flex-1">
          {title && <h4 className={`font-medium ${textClass} mb-1`}>{title}</h4>}
          <div className={textClass}>{children}</div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className={`ml-3 ${textClass} hover:opacity-75 transition-opacity`}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default Alert;
