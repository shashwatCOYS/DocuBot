# DocuBot Backend

AI-powered documentation chatbot backend using Cerebras AI API with Llama 3.1 8B model.

## Features

- 🤖 **Cerebras AI Integration**: Uses Llama 3.1 8B model via Cerebras AI API for ultra-fast inference
- 📚 **RAG System**: Retrieval-Augmented Generation for context-aware responses
- 🔍 **Document Indexing**: Crawl and index documentation from URLs
- 💾 **Vector Database**: ChromaDB for semantic document storage and retrieval
- 🚀 **FastAPI**: Modern, fast web framework with automatic API documentation
- 🔄 **CORS Support**: Configured for frontend integration

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and update it:

```bash
cp env.example .env
```

Edit `.env` and set your Cerebras AI API key:

```env
CEREBRAS_API_KEY=your_actual_api_key_here
```

### 3. Get Cerebras AI API Key

1. Visit [Cerebras Cloud](https://cloud.cerebras.ai)
2. Sign up for an account
3. Request access to the Inference API
4. Get your API key from the dashboard

### 4. Start the Server

```bash
python start.py
```

The server will start on `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

## API Endpoints

### Chat
- `POST /chat` - Send a message to the AI assistant

### Document Management
- `POST /documents` - Add a document by URL
- `GET /documents/stats` - Get document collection statistics
- `DELETE /documents` - Clear all documents
- `DELETE /documents/{source_url}` - Delete documents from specific source

### Search
- `GET /search?query={query}` - Search documents without chat response

### Health
- `GET /health` - Health check and system status

## Usage Examples

### Add Documentation
```bash
curl -X POST "http://localhost:8000/documents" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://docs.example.com"}'
```

### Chat with AI
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How do I configure the API?"}'
```

### Search Documents
```bash
curl "http://localhost:8000/search?query=API configuration&limit=3"
```

## Configuration

Key configuration options in `.env`:

```env
# Cerebras AI API
CEREBRAS_API_KEY=your_api_key
CEREBRAS_API_BASE_URL=https://api.cerebras.ai/v1

# Model Settings
MODEL_NAME=llama-3.1-8b
MAX_TOKENS=2048
TEMPERATURE=0.7
TOP_P=0.9

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Architecture

### Components

1. **CerebrasClient** (`services/cerebras_client.py`)
   - Handles communication with Cerebras AI API
   - Manages Llama 3.1 8B model interactions
   - Implements RAG with context injection

2. **RAGSystem** (`services/rag_system.py`)
   - Document crawling and indexing
   - Vector database management with ChromaDB
   - Semantic search and retrieval

3. **FastAPI App** (`main.py`)
   - REST API endpoints
   - Request/response handling
   - Error management

### Data Flow

1. **Document Indexing**:
   ```
   URL → Web Crawler → Text Extraction → Chunking → Vector Embedding → ChromaDB
   ```

2. **Chat Flow**:
   ```
   User Query → Vector Search → Context Retrieval → Cerebras AI → Response
   ```

## Development

### Running in Development Mode

```bash
python start.py
```

This will start the server with auto-reload enabled.

### Running with Uvicorn Directly

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing the API

Use the built-in FastAPI documentation at `http://localhost:8000/docs` to test endpoints interactively.

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Cerebras AI API key is correctly set in `.env`
2. **Connection Issues**: Check your internet connection and Cerebras API status
3. **ChromaDB Errors**: Ensure write permissions for the `chroma_db` directory
4. **CORS Issues**: Verify `ALLOWED_ORIGINS` includes your frontend URL

### Health Check

Visit `http://localhost:8000/health` to check:
- Server status
- Cerebras AI connection
- Database status
- Available models

## Performance

- **Cerebras AI**: Up to 18x faster inference than traditional GPU solutions
- **ChromaDB**: Efficient vector similarity search
- **FastAPI**: High-performance async framework
- **RAG**: Context-aware responses with relevant documentation

## License

This project is part of DocuBot, an AI-powered documentation assistant.
