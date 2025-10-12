#!/usr/bin/env python3
"""
Simple server startup script for YodaAI
"""

import os
import sys
import subprocess

def main():
    # Set environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///./yodaai.db'
    os.environ['SECRET_KEY'] = 'test-secret-key-for-development'
    os.environ['OPENAI_API_KEY'] = 'sk-demo-key-for-development'
    os.environ['FIREBASE_PROJECT_ID'] = 'yodaai-development'
    os.environ['FIREBASE_PRIVATE_KEY'] = 'demo-private-key'
    os.environ['FIREBASE_CLIENT_EMAIL'] = 'demo@yodaai.com'
    
    print("🚀 Starting YodaAI Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🌐 UI will be available at: http://localhost:8000/ui")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("\n" + "="*50)
    
    try:
        # Import and run the FastAPI app
        import uvicorn
        from main import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try installing dependencies: py -m pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
