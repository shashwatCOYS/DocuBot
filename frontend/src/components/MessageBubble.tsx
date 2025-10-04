'use client';

import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';

interface MessageBubbleProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
  sources?: Array<{
    content: string;
    metadata: {
      source_url: string;
      content_type?: string;
      has_markdown?: boolean;
    };
    similarity_score: number;
    rank: number;
  }>;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ 
  message, 
  isUser, 
  timestamp, 
  sources = [] 
}) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-3xl ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message bubble */}
        <div
          className={`
            px-4 py-3 rounded-lg shadow-sm
            ${isUser 
              ? 'bg-blue-600 text-white rounded-br-sm' 
              : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-sm border border-gray-200 dark:border-gray-700'
            }
          `}
        >
          {isUser ? (
            <div className="text-white">
              {message}
            </div>
          ) : (
            <MarkdownRenderer content={message} />
          )}
        </div>
        
        {/* Timestamp */}
        {timestamp && (
          <div className={`text-xs text-gray-500 dark:text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {new Date(timestamp).toLocaleTimeString()}
          </div>
        )}
        
        {/* Sources for AI messages */}
        {!isUser && sources.length > 0 && (
          <div className="mt-3 space-y-2">
            <div className="text-xs text-gray-500 dark:text-gray-400 font-medium">
              Sources:
            </div>
            <div className="space-y-2">
              {sources.slice(0, 3).map((source, index) => (
                <div 
                  key={index}
                  className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 border border-gray-200 dark:border-gray-600"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Source {source.rank} • {(source.similarity_score * 100).toFixed(1)}% match
                    </div>
                    <div className="text-xs text-gray-400 dark:text-gray-500">
                      {source.metadata.content_type || 'content'}
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                    {source.metadata.has_markdown ? (
                      <MarkdownRenderer 
                        content={source.content.slice(0, 200) + (source.content.length > 200 ? '...' : '')} 
                        className="text-sm"
                      />
                    ) : (
                      source.content.slice(0, 200) + (source.content.length > 200 ? '...' : '')
                    )}
                  </div>
                  
                  <a 
                    href={source.metadata.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 truncate block"
                  >
                    {source.metadata.source_url}
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Avatar */}
      <div className={`flex-shrink-0 ${isUser ? 'order-1 ml-3' : 'order-2 mr-3'}`}>
        <div className={`
          w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
          ${isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
          }
        `}>
          {isUser ? 'U' : 'AI'}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
