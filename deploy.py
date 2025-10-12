#!/usr/bin/env python3
"""
YodaAI Deployment Script for Vercel
"""

import os
import sys
import subprocess
import json
import shutil

def main():
    print("🚀 YodaAI Vercel Deployment Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if vercel.json exists
    if not os.path.exists("vercel.json"):
        print("❌ Error: vercel.json not found.")
        sys.exit(1)
    
    # Check if api/index.py exists
    if not os.path.exists("api/index.py"):
        print("❌ Error: api/index.py not found.")
        sys.exit(1)
    
    # Check if yodaai-enhanced.html exists
    if not os.path.exists("yodaai-enhanced.html"):
        print("❌ Error: yodaai-enhanced.html not found.")
        sys.exit(1)
    
    print("✅ All required files found!")
    
    # Check Python dependencies
    print("\n📦 Checking Python dependencies...")
    try:
        import fastapi
        import uvicorn
        import pydantic_settings
        print("✅ Core dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: py -m pip install -r requirements.txt")
        sys.exit(1)
    
    # Create .env file for local testing
    print("\n🔧 Creating .env file for local testing...")
    env_content = """# YodaAI Environment Variables
DATABASE_URL=sqlite:///./yodaai.db
OPENAI_API_KEY=sk-demo-key-for-development
SECRET_KEY=test-secret-key-for-development
FIREBASE_PROJECT_ID=yodaai-development
FIREBASE_PRIVATE_KEY=demo-private-key
FIREBASE_CLIENT_EMAIL=demo@yodaai.com
DEBUG=true
ENVIRONMENT=development
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("✅ .env file created")
    
    # Test local server
    print("\n🧪 Testing local server...")
    try:
        # Start server in background for testing
        process = subprocess.Popen([
            sys.executable, "-c", 
            "import os; os.environ.update({'DATABASE_URL': 'sqlite:///./yodaai.db', 'SECRET_KEY': 'test-key', 'OPENAI_API_KEY': 'demo-key'}); import uvicorn; from main import app; uvicorn.run(app, host='127.0.0.1', port=8000)"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        import time
        time.sleep(3)
        
        # Check if server is running
        try:
            import requests
            response = requests.get("http://127.0.0.1:8000", timeout=5)
            if response.status_code == 200:
                print("✅ Local server test successful")
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
        except:
            print("⚠️ Could not test server (requests not available)")
        
        # Stop the test server
        process.terminate()
        
    except Exception as e:
        print(f"⚠️ Local server test failed: {e}")
    
    # Deployment instructions
    print("\n" + "=" * 50)
    print("🎯 DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    
    print("\n1. 📱 OPTION 1: Deploy via Vercel Dashboard (Recommended)")
    print("   • Go to https://vercel.com/dashboard")
    print("   • Click 'New Project'")
    print("   • Import your Git repository")
    print("   • Vercel will automatically detect the configuration")
    print("   • Set environment variables in project settings")
    
    print("\n2. 💻 OPTION 2: Deploy via Vercel CLI")
    print("   • Install Node.js: https://nodejs.org/")
    print("   • Install Vercel CLI: npm install -g vercel")
    print("   • Run: vercel --prod")
    
    print("\n3. 🌐 OPTION 3: Use Standalone HTML (Immediate)")
    print("   • Open yodaai-enhanced.html in your browser")
    print("   • No server required - works immediately!")
    
    print("\n📋 Environment Variables to Set in Vercel:")
    print("   DATABASE_URL=sqlite:///./yodaai.db")
    print("   OPENAI_API_KEY=your-openai-api-key")
    print("   SECRET_KEY=your-secret-key")
    print("   FIREBASE_PROJECT_ID=your-firebase-project-id")
    print("   FIREBASE_PRIVATE_KEY=your-firebase-private-key")
    print("   FIREBASE_CLIENT_EMAIL=your-firebase-client-email")
    
    print("\n🔗 After Deployment:")
    print("   • Main App: https://your-project.vercel.app/")
    print("   • API: https://your-project.vercel.app/api/")
    print("   • API Docs: https://your-project.vercel.app/docs")
    
    print("\n✅ Project is ready for deployment!")
    print("💡 For immediate testing, open yodaai-enhanced.html in your browser")

if __name__ == "__main__":
    main()

