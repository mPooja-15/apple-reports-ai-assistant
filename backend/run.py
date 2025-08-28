#!/usr/bin/env python3
"""
Simple startup script for the Apple Annual Reports QA System Backend.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if environment is properly set up."""
    print("🔍 Checking environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("   Creating .env file from template...")
        
        if Path("env_example.txt").exists():
            with open("env_example.txt", "r") as src:
                with open(".env", "w") as dst:
                    dst.write(src.read())
            print("✅ .env file created from template")
            print("⚠️  Please edit .env and add your OpenAI API key before running again")
            return False
        else:
            print("❌ env_example.txt not found")
            return False
    
    # Check if data directory exists
    data_dir = Path("data")
    if not data_dir.exists():
        print("⚠️  data directory not found")
        print("   Creating data directory...")
        data_dir.mkdir()
        print("✅ data directory created")
        print("⚠️  Please add PDF files to data/ directory")
    
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import langchain
        import openai
        print("✅ All required dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def main():
    """Main function to start the backend."""
    print("🍎 Apple Annual Reports QA System - Backend")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install required dependencies.")
        return
    
    print("\n✅ All checks passed!")
    print("\n🚀 Starting FastAPI backend...")
    print("   API will be available at: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop")
    print("\n" + "=" * 50)
    
    try:
        # Start the FastAPI application
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Backend failed to start: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
