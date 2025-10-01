#!/usr/bin/env python3
"""
Test script to verify DocuBot backend setup.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import chromadb
        print("✅ ChromaDB imported successfully")
    except ImportError as e:
        print(f"❌ ChromaDB import failed: {e}")
        return False
    
    try:
        import httpx
        print("✅ HTTPX imported successfully")
    except ImportError as e:
        print(f"❌ HTTPX import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"❌ BeautifulSoup import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import settings
        print("✅ Configuration loaded successfully")
        print(f"   Model: {settings.model_name}")
        print(f"   Host: {settings.host}")
        print(f"   Port: {settings.port}")
        print(f"   API Base URL: {settings.cerebras_api_base_url}")
        
        # Check if API key is set
        if settings.cerebras_api_key and settings.cerebras_api_key != "your_cerebras_api_key_here":
            print("✅ API key is configured")
        else:
            print("⚠️  API key not configured (using default)")
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_services():
    """Test service initialization."""
    print("\n🛠️  Testing services...")
    
    try:
        from services.cerebras_client import CerebrasClient
        client = CerebrasClient()
        print("✅ CerebrasClient initialized successfully")
        
        from services.rag_system import RAGSystem
        rag = RAGSystem()
        print("✅ RAGSystem initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Services test failed: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist."""
    print("\n📁 Testing directory structure...")
    
    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "env.example",
        "services/cerebras_client.py",
        "services/rag_system.py",
        "services/__init__.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("🧪 DocuBot Backend Setup Test")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Services", test_services)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your DocuBot backend is ready to run.")
        print("\nNext steps:")
        print("1. Set your CEREBRAS_API_KEY in .env file")
        print("2. Run: python start.py")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTo fix:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Check file permissions and directory structure")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
