#!/usr/bin/env python3
"""
Startup script for DocuBot backend.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import uvicorn
from config import settings


def main():
    """Start the DocuBot backend server."""
    print("🚀 Starting DocuBot Backend Server...")
    print(f"📍 Host: {settings.host}")
    print(f"🔌 Port: {settings.port}")
    print(f"🐛 Debug Mode: {settings.debug}")
    print(f"🤖 Model: {settings.model_name}")
    print("-" * 50)
    
    # Check if API key is set
    if not settings.cerebras_api_key or settings.cerebras_api_key == "your_cerebras_api_key_here":
        print("⚠️  WARNING: CEREBRAS_API_KEY not set or using default value!")
        print("   Please set your Cerebras AI API key in the .env file")
        print("   Copy env.example to .env and update the API key")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )


if __name__ == "__main__":
    main()
