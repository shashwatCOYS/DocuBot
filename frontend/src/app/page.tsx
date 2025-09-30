'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Copy, RotateCcw } from 'lucide-react';
import { Message, ChatState } from '@/types';

export default function ChatPage() {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [
      {
        id: '1',
        content: 'Hello! I\'m DocuBot, your AI documentation assistant. I can help you find information from your configured documentation sources. How can I assist you today?',
        role: 'assistant',
        timestamp: new Date(),
      }
    ],
    isLoading: false,
  });
  
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatState.messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || chatState.isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date(),
    };

    setChatState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
    }));

    const currentInput = inputMessage;
    setInputMessage('');

    // Simulate API call - replace with actual API integration
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `I understand you're asking about: "${currentInput}". This is a demo response from DocuBot. 

Once you configure your documentation URL in the settings, I'll be able to provide real, context-aware answers based on your specific documentation.

For now, I can help you understand how to:
• Set up your documentation source
• Navigate the interface
• Get the most out of DocuBot's features

Would you like me to guide you through the setup process?`,
        role: 'assistant',
        timestamp: new Date(),
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const clearChat = () => {
    setChatState({
      messages: [
        {
          id: '1',
          content: 'Hello! I\'m DocuBot, your AI documentation assistant. How can I help you today?',
          role: 'assistant',
          timestamp: new Date(),
        }
      ],
      isLoading: false,
    });
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      {/* Chat Header */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                DocuBot
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                AI Documentation Assistant
              </p>
            </div>
          </div>
          <button
            onClick={clearChat}
            className="flex items-center space-x-2 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {chatState.messages.map((message) => (
          <div
            key={message.id}
            className={`flex space-x-4 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              </div>
            )}
            
            <div className={`group max-w-3xl ${message.role === 'user' ? 'order-first' : ''}`}>
              <div
                className={`relative px-4 py-3 rounded-2xl ${
                  message.role === 'user'
                    ? 'bg-indigo-600 text-white ml-12'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                }`}
              >
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </div>
                
                {/* Message actions */}
                <div className={`absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity ${message.role === 'user' ? 'text-indigo-200' : 'text-gray-400'}`}>
                  <button
                    onClick={() => copyMessage(message.content)}
                    className={`p-1 rounded hover:bg-black/10 ${message.role === 'user' ? 'hover:bg-white/20' : 'hover:bg-gray-200 dark:hover:bg-gray-700'}`}
                  >
                    <Copy className="w-3 h-3" />
                  </button>
                </div>
              </div>
              
              {/* Timestamp */}
              <div className={`mt-1 text-xs text-gray-500 dark:text-gray-400 ${
                message.role === 'user' ? 'text-right mr-4' : 'ml-4'
              }`}>
                {message.timestamp.toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </div>
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                </div>
              </div>
            )}
          </div>
        ))}
        
        {chatState.isLoading && (
          <div className="flex space-x-4">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="bg-gray-100 dark:bg-gray-800 px-4 py-3 rounded-2xl">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full typing-indicator"></div>
                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full typing-indicator"></div>
                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full typing-indicator"></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Message DocuBot..."
              className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
              disabled={chatState.isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || chatState.isLoading}
              className="absolute right-2 bottom-2 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
}
