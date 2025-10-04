'use client';

import React from 'react';

interface LoadingIndicatorProps {
  message?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ 
  message = "AI is thinking..." 
}) => {
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-3xl order-1">
        <div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg rounded-bl-sm border border-gray-200 dark:border-gray-700 px-4 py-3 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-sm text-gray-600 dark:text-gray-400">{message}</span>
          </div>
        </div>
      </div>
      
      <div className="flex-shrink-0 order-2 mr-3">
        <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 flex items-center justify-center text-sm font-medium">
          AI
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
