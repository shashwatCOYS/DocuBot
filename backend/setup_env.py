#!/usr/bin/env python3
"""
Setup script to create .env file for DocuBot backend.
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file from env.example."""
    backend_dir = Path(__file__).parent
    env_example = backend_dir / "env.example"
    env_file = backend_dir / ".env"
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    try:
        # Read the example file
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Write to .env file
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from env.example")
        print("⚠️  IMPORTANT: Please edit .env and set your CEREBRAS_API_KEY")
        print(f"   File location: {env_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    """Main setup function."""
    print("🔧 DocuBot Backend Environment Setup")
    print("=" * 50)
    
    success = create_env_file()
    
    if success:
        print("\n📝 Next Steps:")
        print("1. Edit .env file and set your CEREBRAS_API_KEY")
        print("2. Get API key from: https://cloud.cerebras.ai")
        print("3. Run: python start.py")
        print("\n💡 Tip: You can edit .env with any text editor")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()
