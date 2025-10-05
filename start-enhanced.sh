#!/bin/bash

# DocuBot Enhanced System Startup Script
# This script starts the enhanced DocuBot system with all services

set -e

echo "🚀 Starting DocuBot Enhanced System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from env.example..."
    cp env.example .env
    echo "📝 Please edit .env file with your API keys before continuing."
    echo "   Required keys: CEREBRAS_API_KEY, EXA_API_KEY, CONTEXT7_API_KEY"
    read -p "Press Enter to continue after editing .env file..."
fi

# Validate required environment variables
echo "🔍 Validating environment configuration..."

source .env

required_vars=("CEREBRAS_API_KEY" "EXA_API_KEY" "CONTEXT7_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "your_${var,,}_here" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing or invalid API keys:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo "Please edit .env file and set valid API keys."
    exit 1
fi

echo "✅ Environment configuration validated"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/chroma_db
mkdir -p mcp-config

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose pull

# Build custom images
echo "🔨 Building custom images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

services=("backend" "frontend" "mcp-gateway" "context7-mcp" "weaviate" "redis")
healthy_services=()

for service in "${services[@]}"; do
    if docker-compose ps $service | grep -q "Up"; then
        healthy_services+=("$service")
        echo "✅ $service is running"
    else
        echo "❌ $service is not running"
    fi
done

# Test backend health endpoint
echo "🔍 Testing backend health..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend health check passed"
        break
    else
        echo "⏳ Waiting for backend to be ready... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Backend health check failed after $max_attempts attempts"
    echo "📋 Checking backend logs..."
    docker-compose logs backend
    exit 1
fi

# Display service URLs
echo ""
echo "🎉 DocuBot Enhanced System is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Frontend:        http://localhost:3000"
echo "🔧 Backend API:     http://localhost:8000"
echo "📚 API Docs:        http://localhost:8000/docs"
echo "🔍 MCP Gateway:     http://localhost:7777"
echo "🧠 Context7 MCP:    http://localhost:7778"
echo "🗄️  Weaviate:       http://localhost:8080"
echo "⚡ Redis:          redis://localhost:6379"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Display useful commands
echo "📋 Useful Commands:"
echo "   View logs:       docker-compose logs -f"
echo "   Stop services:   docker-compose down"
echo "   Restart:         docker-compose restart"
echo "   Service status:  docker-compose ps"
echo ""

# Test enhanced endpoints
echo "🧪 Testing enhanced endpoints..."

# Test Context7 libraries endpoint
if curl -s http://localhost:8000/context7/libraries > /dev/null; then
    echo "✅ Context7 libraries endpoint is working"
else
    echo "⚠️  Context7 libraries endpoint may not be working"
fi

# Display next steps
echo "📝 Next Steps:"
echo "1. Visit http://localhost:3000 to access the frontend"
echo "2. Try crawling some documentation:"
echo "   curl -X POST http://localhost:8000/crawl/documentation \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"base_url\": \"https://docs.python.org/3/\", \"context7_libraries\": [\"/python/cpython\"]}'"
echo "3. Test enhanced search:"
echo "   curl -X POST http://localhost:8000/search/enhanced \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"How to use decorators?\", \"context7_libraries\": [\"/python/cpython\"]}'"
echo ""

echo "🎯 DocuBot Enhanced System is ready for use!"


