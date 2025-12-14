import React from 'react';

interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  headerAction?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, children, className = '', headerAction }) => {
  return (
    <div className={`bg-white dark:bg-dark-800 rounded-lg shadow-md border border-gray-200 dark:border-dark-700 ${className}`}>
      {title && (
        <div className="px-6 py-4 border-b border-gray-200 dark:border-dark-700 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
    </div>
  );
};

export default Card;
