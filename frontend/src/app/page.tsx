'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import ThemeToggle from './components/ThemeToggle';
import MessageBubble from '../components/MessageBubble';
import ChatInput from '../components/ChatInput';
import LoadingIndicator from '../components/LoadingIndicator';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
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

interface ChatSession {
  id: string;
  title: string;
  timestamp: Date;
  messageCount: number;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m **DocuBot**, your AI assistant for technical documentation. I can help you understand code, APIs, frameworks, and more.\n\n## What I can help with:\n- 📚 **Documentation**: Explain concepts, APIs, and frameworks\n- 💻 **Code Examples**: Show you how to implement features\n- 🔍 **Search**: Find specific information across documentation\n- 🚀 **Best Practices**: Guide you through implementation patterns\n\nWhat would you like to know?',
      isUser: false,
      timestamp: new Date(),
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatSession[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: message,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Create new chat session if this is the first user message
    if (messages.length === 1) {
      const newSession: ChatSession = {
        id: Date.now().toString(),
        title: message.length > 30 ? message.substring(0, 30) + '...' : message,
        timestamp: new Date(),
        messageCount: 1,
      };
      setChatHistory(prev => [newSession, ...prev]);
    }

    // Call the actual DocuBot API
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: messages.length === 1 ? Date.now().toString() : undefined
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date(data.timestamp),
        sources: data.sources || [],
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error calling DocuBot API:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error while processing your request. Please make sure the DocuBot backend is running and try again.',
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewChat = () => {
    setMessages([
      {
        id: '1',
        text: 'Hello! I\'m **DocuBot**, your AI assistant for technical documentation. I can help you understand code, APIs, frameworks, and more.\n\n## What I can help with:\n- 📚 **Documentation**: Explain concepts, APIs, and frameworks\n- 💻 **Code Examples**: Show you how to implement features\n- 🔍 **Search**: Find specific information across documentation\n- 🚀 **Best Practices**: Guide you through implementation patterns\n\nWhat would you like to know?',
        isUser: false,
        timestamp: new Date(),
      }
    ]);
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden bg-white dark:bg-slate-800 border-r border-gray-200 dark:border-slate-700 flex flex-col`}>
        <div className="p-4 border-b border-gray-200 dark:border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Chat History</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <button
            onClick={startNewChat}
            className="w-full bg-blue-500 dark:bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-600 dark:hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            + New Chat
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4">
          {chatHistory.length === 0 ? (
            <div className="text-center text-gray-500 text-sm">
              <p>No chat history yet</p>
              <p className="mt-1 dark:text-gray-400">Start a conversation to see it here</p>
            </div>
          ) : (
            <div className="space-y-2">
              {chatHistory.map((session) => (
                <div
                  key={session.id}
                  className="p-3 rounded-lg border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700 cursor-pointer transition-colors"
                >
                  <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {session.title}
                  </h3>
                  <div className="flex items-center justify-between mt-1">
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {session.timestamp.toLocaleDateString()}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">
                      {session.messageCount} messages
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700">
          <div className="px-4 py-4 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">DocuBot</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/settings"
                className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
              >
                Settings
              </Link>
              <ThemeToggle />
            </div>
          </div>
        </header>

        {/* Chat Container */}
        <div className="flex-1 flex flex-col h-[calc(100vh-80px)]">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message.text}
                isUser={message.isUser}
                timestamp={message.timestamp.toISOString()}
                sources={message.sources}
              />
            ))}
            {isLoading && <LoadingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder="Ask me anything about the documentation..."
          />
        </div>
      </div>
    </div>
  );
}
