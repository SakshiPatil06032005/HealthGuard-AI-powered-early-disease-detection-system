"""
Quick setup script for the AI Disease Prediction System
Requires Python 3.11
"""
import os
import sys
import subprocess
import platform

def check_python_version():
    """Ensure we're using Python 3.11"""
    version = sys.version_info
    if version.major != 3 or version.minor != 11:
        print("\n❌ Error: This application requires Python 3.11")
        print(f"Current Python version: {platform.python_version()}")
        print("\nPlease:")
        print("1. Download Python 3.11 from https://www.python.org/downloads/release/python-3115/")
        print("2. Run this script using Python 3.11")
        sys.exit(1)

def setup_environment():
    """Create virtual environment and install requirements"""
    print("\nSetting up AI Disease Prediction System...")
    
    # Create venv if it doesn't exist
    if not os.path.exists('venv'):
        print("\n1. Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    
    # Activate venv and install requirements
    print("\n2. Installing requirements...")
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:  # Linux/Mac
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    # Upgrade pip
    subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
    
    # Install minimal requirements first
    subprocess.run([pip_path, 'install', '-r', 'requirements-minimal.txt'], check=True)

def create_directories():
    """Create necessary directories"""
    print("\n3. Creating required directories...")
    dirs = [
        'uploads',
        'app/static/heatmaps',
        'instance'
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✓ Created {d}/")

def print_instructions():
    """Show next steps"""
    print("\n✨ Setup Complete! ✨")
    print("\nTo run the application:")
    if os.name == 'nt':  # Windows
        print("1. .\\venv\\Scripts\\activate")
    else:
        print("1. source venv/bin/activate")
    print("2. python run.py")
    print("3. Open http://localhost:3000 in your browser")
    
    print("\nLogin Credentials:")
    print("1. Doctor:")
    print("   Username: mahima")
    print("   Password: mahima")
    
    print("\nOptional: Enable medical reports")
    print("export API_TOKEN=your_openai_key  # or use Windows Environment Variables")

if __name__ == '__main__':
    try:
        check_python_version()
        setup_environment()
        create_directories()
        print_instructions()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during setup: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)