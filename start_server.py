#!/usr/bin/env python3
"""
YodaAI Server Startup Script
Complete initialization and startup with checks
"""

import os
import sys
from pathlib import Path


def print_banner():
    """Print startup banner"""
    banner = """
    ========================================================
    
                YodaAI Server Startup
    
       AI-Powered Retrospective Assistant for Teams
    
    ========================================================
    """
    print(banner)


def check_python_version():
    """Check if Python version is compatible"""
    print("[*] Checking Python version...")
    if sys.version_info < (3, 9):
        print("[!] Error: Python 3.9 or higher is required")
        print(f"    Current version: {sys.version}")
        sys.exit(1)
    print(f"[+] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n[*] Checking dependencies...")
    required_packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[!] Missing packages: {', '.join(missing)}")
        print("[i] Install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    print("[+] All core dependencies installed")


def check_env_file():
    """Check if .env file exists"""
    print("\n[*] Checking environment configuration...")
    env_path = Path(".env")
    
    if not env_path.exists():
        print("[!] Warning: .env file not found")
        print("[i] Creating from env.example...")
        
        example_path = Path("env.example")
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            print("[+] Created .env file from template")
            print("[!] Please configure your API keys in .env before production use")
        else:
            print("[!] Error: env.example not found")
            sys.exit(1)
    else:
        print("[+] Environment file found")


def load_environment():
    """Load environment variables"""
    print("\n[*] Loading environment variables...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[+] Environment variables loaded")
    except Exception as e:
        print(f"[!] Warning: Could not load .env file: {e}")


def check_database():
    """Check database configuration"""
    print("\n[*] Checking database configuration...")
    
    try:
        from app.core.config import settings
        
        db_url = settings.NEON_DATABASE_URL or settings.DATABASE_URL
        
        if db_url.startswith("postgresql"):
            print(f"[+] Database: PostgreSQL/Neon Cloud")
        else:
            print(f"[+] Database: SQLite (local)")
        
        # Test connection
        from app.database.database import test_connection
        if test_connection():
            print("[+] Database connection successful")
        else:
            print("[!] Warning: Could not connect to database")
            
    except Exception as e:
        print(f"[!] Warning: Database check failed: {e}")


def check_openai_key():
    """Check if OpenAI API key is configured"""
    print("\n[*] Checking AI configuration...")
    
    try:
        from app.core.config import settings
        
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
            print("[+] OpenAI API key configured")
        else:
            print("[!] Warning: OpenAI API key not configured")
            print("    AI features will not work without a valid API key")
            print("    Get your key from: https://platform.openai.com/api-keys")
    except Exception as e:
        print(f"[!] Warning: Could not check API key: {e}")


def print_startup_info():
    """Print server startup information"""
    print("\n" + "="*60)
    print("Server Information:")
    print("="*60)
    print("Main Application:  http://localhost:8000")
    print("User Interface:    http://localhost:8000/ui")
    print("API Docs (Swagger): http://localhost:8000/docs")
    print("API Docs (ReDoc):  http://localhost:8000/redoc")
    print("Health Check:      http://localhost:8000/health")
    print("="*60)


def start_server():
    """Start the FastAPI server"""
    print("\n[*] Starting YodaAI server...")
    print("[i] Press Ctrl+C to stop the server\n")
    
    try:
        import uvicorn
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n[*] Server stopped by user")
        sys.exit(0)
    except ImportError as e:
        print(f"\n[!] Import error: {e}")
        print("[i] Install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main startup function"""
    print_banner()
    
    # Run all checks
    check_python_version()
    check_dependencies()
    check_env_file()
    load_environment()
    check_database()
    check_openai_key()
    
    # Print server information
    print_startup_info()
    
    # Start the server
    start_server()


if __name__ == "__main__":
    main()
