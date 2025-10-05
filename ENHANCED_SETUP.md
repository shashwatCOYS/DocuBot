# DocuBot Enhanced Web Crawling with Context7 Integration

This enhanced version of DocuBot provides robust web crawling capabilities using Docker MCP Gateway with Exa integration, cloud-based vector database (Weaviate), and Context7 documentation enhancement.

## Features

### 🔍 Enhanced Web Crawling
- **MCP Gateway Integration**: Uses Docker MCP Gateway with Exa MCP for superior web crawling
- **Recursive Crawling**: Can crawl entire documentation sites with configurable depth
- **Fallback Support**: Falls back to traditional crawling if MCP services are unavailable
- **Concurrent Processing**: Configurable concurrent request handling

### 🧠 Context7 Integration
- **Documentation Enhancement**: Automatically enhances crawled content with Context7 documentation
- **Library-Specific Context**: Supports multiple Context7 libraries for targeted enhancement
- **Query Enhancement**: Improves search queries with Context7 context

### ☁️ Cloud Vector Database
- **Weaviate Integration**: Uses Weaviate as the cloud-based vector database
- **Semantic Search**: Advanced semantic similarity search capabilities
- **Scalable Storage**: Cloud-native vector storage for large document collections

### 🐳 Docker-First Architecture
- **Containerized Services**: All services run in Docker containers
- **Service Orchestration**: Docker Compose for easy deployment
- **Production Ready**: Configured for production deployment

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   MCP Gateway   │
│   (Next.js)     │◄──►│   (FastAPI)      │◄──►│   (Exa MCP)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        │
                       ┌──────────────────┐             │
                       │   Weaviate       │             │
                       │ (Vector DB)      │             │
                       └──────────────────┘             │
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │     Redis        │    │   Context7 MCP  │
                       │   (Caching)      │    │   (Enhancement) │
                       └──────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- API keys for:
  - Cerebras AI
  - Exa (for web crawling)
  - Context7 (for documentation enhancement)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd DocuBot
cp env.example .env
```

### 2. Configure Environment
Edit `.env` file with your API keys:
```bash
# Required API Keys
CEREBRAS_API_KEY=your_cerebras_api_key_here
EXA_API_KEY=your_exa_api_key_here
CONTEXT7_API_KEY=your_context7_api_key_here

# Optional: MCP Gateway API Key (if required)
MCP_GATEWAY_API_KEY=your_mcp_gateway_api_key_here
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## API Endpoints

### Enhanced Crawling Endpoints

#### Crawl Multiple URLs with Context7 Enhancement
```bash
POST /crawl/enhanced
Content-Type: application/json

{
  "urls": ["https://example.com/docs", "https://api.example.com"],
  "context7_libraries": ["/supabase/supabase", "/vercel/next.js"]
}
```

#### Crawl Documentation Site
```bash
POST /crawl/documentation
Content-Type: application/json

{
  "base_url": "https://docs.example.com",
  "context7_libraries": ["/fastapi/fastapi"]
}
```

#### Enhanced Search with Context7
```bash
POST /search/enhanced
Content-Type: application/json

{
  "query": "How to implement authentication?",
  "limit": 5,
  "context7_libraries": ["/supabase/supabase"]
}
```

#### Get Available Context7 Libraries
```bash
GET /context7/libraries
```

### Traditional Endpoints (Still Available)
- `POST /chat` - Chat with the AI assistant
- `POST /documents` - Add single document
- `GET /search` - Basic search
- `GET /health` - Health check

## Configuration Options

### Web Crawling Configuration
```bash
MAX_CRAWL_DEPTH=3                    # Maximum crawl depth
MAX_CONCURRENT_REQUESTS=5            # Concurrent requests
CRAWL_DELAY=1.0                      # Delay between requests (seconds)
USE_MCP_FOR_CRAWLING=true            # Enable MCP Gateway crawling
```

### Vector Database Configuration
```bash
WEAVIATE_URL=http://localhost:8080   # Weaviate instance URL
USE_CLOUD_VECTORDB=true              # Enable cloud vector database
```

### Context7 Configuration
```bash
CONTEXT7_API_KEY=your_key_here       # Context7 API key
```

## Usage Examples

### 1. Crawl a Documentation Site
```python
import requests

response = requests.post("http://localhost:8000/crawl/documentation", json={
    "base_url": "https://docs.python.org/3/",
    "context7_libraries": ["/python/cpython"]
})

print(response.json())
```

### 2. Enhanced Search
```python
response = requests.post("http://localhost:8000/search/enhanced", json={
    "query": "How to use decorators in Python?",
    "limit": 3,
    "context7_libraries": ["/python/cpython"]
})

print(response.json())
```

### 3. Chat with Enhanced Context
```python
response = requests.post("http://localhost:8000/chat", json={
    "message": "Explain Python decorators with examples",
    "session_id": "my_session"
})

print(response.json())
```

## Service Management

### Start All Services
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Stop Services
```bash
docker-compose down
```

### Restart a Service
```bash
docker-compose restart backend
```

## Monitoring and Health Checks

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

### Service Status
```bash
docker-compose ps
```

### Database Statistics
```bash
curl http://localhost:8000/documents/stats
```

## Troubleshooting

### Common Issues

1. **MCP Gateway Connection Failed**
   - Check if MCP Gateway is running: `docker-compose logs mcp-gateway`
   - Verify EXA_API_KEY is set correctly
   - Ensure port 7777 is not blocked

2. **Weaviate Connection Issues**
   - Check Weaviate logs: `docker-compose logs weaviate`
   - Verify port 8080 is available
   - Check Weaviate health: `curl http://localhost:8080/v1/meta`

3. **Context7 Enhancement Not Working**
   - Verify CONTEXT7_API_KEY is set
   - Check Context7 MCP logs: `docker-compose logs context7-mcp`
   - Test Context7 connection

4. **Crawling Failures**
   - Check network connectivity
   - Verify target URLs are accessible
   - Review crawling logs in backend service

### Debug Mode
Enable debug mode by setting `DEBUG=true` in your `.env` file for detailed logging.

## Performance Optimization

### For Large-Scale Crawling
1. Increase `MAX_CONCURRENT_REQUESTS` (but be respectful of target sites)
2. Adjust `CRAWL_DELAY` based on target site's rate limits
3. Use `MAX_CRAWL_DEPTH` to control crawl scope

### For Better Search Performance
1. Ensure Weaviate has adequate resources
2. Monitor vector database size
3. Consider periodic cleanup of old documents

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Rate Limiting**: Be respectful when crawling external sites
3. **CORS**: Configure allowed origins appropriately
4. **Network**: Use proper firewall rules for production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker Compose
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review service logs
3. Create an issue in the repository


