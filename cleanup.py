#!/usr/bin/env python3
"""
Cleanup script to remove files that should be ignored by git.
"""

import os
import shutil
from pathlib import Path

def cleanup_python_cache():
    """Remove Python cache files."""
    print("🧹 Cleaning up Python cache files...")
    
    # Find and remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:  # Use slice to avoid modifying list while iterating
            if dir_name == '__pycache__':
                full_path = os.path.join(root, dir_name)
                print(f"   Removing: {full_path}")
                shutil.rmtree(full_path)
                dirs.remove(dir_name)  # Remove from dirs to avoid traversing into it
        
        # Remove .pyc files
        for file_name in files:
            if file_name.endswith('.pyc'):
                full_path = os.path.join(root, file_name)
                print(f"   Removing: {full_path}")
                os.remove(full_path)

def cleanup_node_modules():
    """Remove node_modules directories."""
    print("🧹 Cleaning up node_modules...")
    
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:
            if dir_name == 'node_modules':
                full_path = os.path.join(root, dir_name)
                print(f"   Removing: {full_path}")
                shutil.rmtree(full_path)
                dirs.remove(dir_name)

def cleanup_build_dirs():
    """Remove build directories."""
    print("🧹 Cleaning up build directories...")
    
    build_dirs = ['.next', 'build', 'dist', 'out']
    
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:
            if dir_name in build_dirs:
                full_path = os.path.join(root, dir_name)
                print(f"   Removing: {full_path}")
                shutil.rmtree(full_path)
                dirs.remove(dir_name)

def cleanup_logs():
    """Remove log files."""
    print("🧹 Cleaning up log files...")
    
    log_extensions = ['.log', '.logs']
    
    for root, dirs, files in os.walk('.'):
        for file_name in files:
            if any(file_name.endswith(ext) for ext in log_extensions):
                full_path = os.path.join(root, file_name)
                print(f"   Removing: {full_path}")
                os.remove(full_path)

def cleanup_temp_files():
    """Remove temporary files."""
    print("🧹 Cleaning up temporary files...")
    
    temp_patterns = ['.DS_Store', 'Thumbs.db', '*.tmp', '*.temp', '*.bak', '*.backup']
    
    for root, dirs, files in os.walk('.'):
        for file_name in files:
            if any(file_name.endswith(pattern.replace('*', '')) for pattern in temp_patterns):
                full_path = os.path.join(root, file_name)
                print(f"   Removing: {full_path}")
                os.remove(full_path)

def main():
    """Main cleanup function."""
    print("🧹 DocuBot Repository Cleanup")
    print("=" * 50)
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Run cleanup functions
    cleanup_python_cache()
    cleanup_node_modules()
    cleanup_build_dirs()
    cleanup_logs()
    cleanup_temp_files()
    
    print("\n" + "=" * 50)
    print("✅ Cleanup completed!")
    print("\n📝 Next steps:")
    print("1. Run: git add .")
    print("2. Run: git status")
    print("3. Commit your changes")

if __name__ == "__main__":
    main()
