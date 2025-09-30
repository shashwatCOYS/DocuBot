// Message interface for chat functionality
export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
  isLoading?: boolean;
}

// Settings interface for configuration
export interface Settings {
  documentationUrl: string;
  lastUpdated?: Date;
  isConfigured: boolean;
}

// Chat state interface
export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error?: string;
}

// API response interface for chatbot
export interface ChatResponse {
  message: string;
  success: boolean;
  error?: string;
}

// Navigation item interface
export interface NavItem {
  href: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
}