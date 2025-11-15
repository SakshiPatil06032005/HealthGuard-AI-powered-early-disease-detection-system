"""
AI-Powered Early Disease Prediction System
Author: Patan Musthakheem
Enhanced with development tools and error handling
"""

import os
import sys

# Change to the script's directory so relative imports and file operations work correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from app import create_app
from app.config import Config

def main():
    """Initialize and run the application with proper error handling."""
    try:
        # Set Gemini API key
        os.environ['GEMINI_API_KEY'] = Config.GEMINI_API_KEY
        
        # Create app
        app = create_app()
        
        # Development server settings
        host = '0.0.0.0'  # Allow external access
        port = 3000
        
        print("\nAI-Powered Disease Prediction System")
        print("===================================")
        print(f"🌐 Server: http://localhost:{port}")
        print("👤 Demo login:")
        print(f"   Username: {Config.DEMO_DOCTOR['id']}")
        print(f"   Password: {Config.DEMO_DOCTOR['password']}")
        
        if Config.SKIP_MODEL_LOAD:
            print("\n⚠️ Running in UI development mode (ML features disabled)")
        
        if not os.path.exists(Config.MODEL_PATH):
            print(f"\n⚠️ Warning: Model not found at {Config.MODEL_PATH}")
            print("Disease prediction will not work until model is installed.")
        
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == 'your-gemini-api-key-here':
            print("\n⚠️ GEMINI_API_KEY not set - medical explanations disabled")
            print("Set GEMINI_API_KEY in config to enable Gemini features")
        
        # Start development server
        app.run(host=host, port=port, debug=True)
        
    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
