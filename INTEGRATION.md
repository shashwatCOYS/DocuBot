# DocuBot Integration Guide

This guide explains how to connect your frontend with the backend API.

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.example .env
# Edit .env and add your Cerebras AI API key
```

### 3. Start Backend Server
```bash
python start.py
```
Server runs on: `http://localhost:8000`

## Frontend Integration

### 1. Update API Base URL

In your frontend, create an API configuration file:

```typescript
// frontend/src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  chat: async (message: string, sessionId?: string) => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
    return response.json();
  },

  addDocument: async (url: string) => {
    const response = await fetch(`${API_BASE_URL}/documents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });
    return response.json();
  },

  getStats: async () => {
    const response = await fetch(`${API_BASE_URL}/documents/stats`);
    return response.json();
  },
};
```

### 2. Update Frontend Components

Update your chat page to use the real API:

```typescript
// frontend/src/app/page.tsx
import { api } from '../lib/api';

// In your handleSendMessage function:
const handleSendMessage = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!inputValue.trim() || isLoading) return;

  const userMessage: Message = {
    id: Date.now().toString(),
    text: inputValue,
    isUser: true,
    timestamp: new Date(),
  };

  setMessages(prev => [...prev, userMessage]);
  setInputValue('');
  setIsLoading(true);

  try {
    const response = await api.chat(inputValue);
    
    if (response.response) {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
    }
  } catch (error) {
    console.error('Chat error:', error);
    // Handle error
  } finally {
    setIsLoading(false);
  }
};
```

Update your settings page to use the real document API:

```typescript
// frontend/src/app/settings/page.tsx
import { api } from '../lib/api';

// In your handleSubmit function:
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!url.trim()) return;

  setIsLoading(true);
  setMessage(null);

  try {
    const response = await api.addDocument(url);
    
    if (response.success) {
      setMessage({
        type: 'success',
        text: response.message
      });
      setUrl('');
    } else {
      setMessage({
        type: 'error',
        text: response.error || 'Failed to process the URL'
      });
    }
  } catch (error) {
    setMessage({
      type: 'error',
      text: 'Failed to process the URL. Please check if the URL is accessible and try again.'
    });
  } finally {
    setIsLoading(false);
  }
};
```

### 3. Environment Variables

Add to your frontend `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

### Chat
```typescript
POST /chat
{
  "message": "How do I configure the API?",
  "session_id": "optional-session-id"
}

Response:
{
  "response": "To configure the API, you need to...",
  "session_id": "session_123",
  "timestamp": "2024-01-01T12:00:00Z",
  "sources": [...],
  "usage": {...}
}
```

### Add Document
```typescript
POST /documents
{
  "url": "https://docs.example.com"
}

Response:
{
  "success": true,
  "message": "Successfully indexed 15 chunks from https://docs.example.com",
  "chunk_count": 15
}
```

### Get Stats
```typescript
GET /documents/stats

Response:
{
  "total_chunks": 150,
  "unique_sources": 5,
  "sources": ["https://docs.example.com", ...]
}
```

## Testing

### 1. Test Backend
```bash
cd backend
python test_setup.py
```

### 2. Test API Endpoints
Visit: `http://localhost:8000/docs` for interactive API testing

### 3. Test Integration
1. Start backend: `python start.py`
2. Start frontend: `npm run dev`
3. Add a document URL in settings
4. Chat with the AI about the documentation

## Troubleshooting

### CORS Issues
If you get CORS errors, ensure your backend `.env` includes your frontend URL:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### API Connection Issues
1. Check backend is running: `http://localhost:8000/health`
2. Verify API key is set in backend `.env`
3. Check console for network errors

### Document Indexing Issues
1. Ensure URLs are publicly accessible
2. Check backend logs for crawling errors
3. Verify ChromaDB has write permissions

## Production Deployment

### Backend
- Use a production ASGI server like Gunicorn with Uvicorn workers
- Set up proper environment variables
- Configure reverse proxy (nginx)

### Frontend
- Build for production: `npm run build`
- Deploy to Vercel, Netlify, or similar
- Update API URL to production backend

## Security Considerations

1. **API Key**: Never expose Cerebras API key in frontend
2. **CORS**: Configure allowed origins properly
3. **Rate Limiting**: Implement rate limiting for production
4. **Input Validation**: Validate all inputs on both frontend and backend
5. **HTTPS**: Use HTTPS in production

## Performance Tips

1. **Caching**: Implement response caching for common queries
2. **Pagination**: Add pagination for large document sets
3. **Streaming**: Consider streaming responses for long AI responses
4. **Database**: Monitor ChromaDB performance and optimize queries
