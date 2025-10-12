#!/usr/bin/env python3
"""
Simple HTTP server for YodaAI testing
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

def main():
    # Set up the server
    PORT = 3000
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Change to the directory containing the HTML file
    os.chdir(Path(__file__).parent)
    
    print("🚀 Starting YodaAI Simple Server...")
    print(f"📍 Server will be available at: http://localhost:{PORT}")
    print(f"🌐 Opening yodaai-enhanced.html...")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"✅ Server running on port {PORT}")
            print("💡 Press Ctrl+C to stop the server")
            
            # Open the browser
            html_file = Path("yodaai-enhanced.html").absolute()
            if html_file.exists():
                webbrowser.open(f"http://localhost:{PORT}/yodaai-enhanced.html")
                print(f"🌐 Opened: http://localhost:{PORT}/yodaai-enhanced.html")
            else:
                print("❌ yodaai-enhanced.html not found")
                webbrowser.open(f"http://localhost:{PORT}/")
                print(f"🌐 Opened: http://localhost:{PORT}/")
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()

