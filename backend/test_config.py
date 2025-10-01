#!/usr/bin/env python3
"""
Test configuration loading without starting the full server.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_config():
    """Test configuration loading."""
    print("🔧 Testing configuration...")
    
    try:
        from config import settings
        print("✅ Configuration loaded successfully")
        
        print(f"   Model: {settings.model_name}")
        print(f"   Host: {settings.host}")
        print(f"   Port: {settings.port}")
        print(f"   Temperature: {settings.temperature}")
        print(f"   API Base URL: {settings.cerebras_api_base_url}")
        
        # Check API key
        if settings.cerebras_api_key and settings.cerebras_api_key != "your_cerebras_api_key_here":
            print("✅ API key is configured")
        else:
            print("⚠️  API key not configured (using default)")
            print("   To configure: Edit .env file and set CEREBRAS_API_KEY")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    print("\n🔍 Testing imports...")
    
    required_modules = [
        "fastapi",
        "uvicorn",
        "chromadb", 
        "httpx",
        "requests",
        "bs4",
        "pydantic_settings"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def main():
    """Main test function."""
    print("🧪 DocuBot Backend Configuration Test")
    print("=" * 50)
    
    config_ok = test_config()
    imports_ok = test_imports()
    
    print("\n" + "=" * 50)
    if config_ok and imports_ok:
        print("🎉 Configuration test passed!")
        print("\n📝 Next steps:")
        if "cerebras_api_key" in str(settings.cerebras_api_key):
            print("1. Get Cerebras AI API key from: https://cloud.cerebras.ai")
            print("2. Edit .env file and set CEREBRAS_API_KEY=your_actual_key")
        print("3. Run: python3 start.py")
        print("4. Visit: http://localhost:8000/docs")
    else:
        print("❌ Configuration test failed")
        if not imports_ok:
            print("\nTo fix import errors:")
            print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
