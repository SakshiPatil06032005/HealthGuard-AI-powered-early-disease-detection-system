"""
Instructions for setting up the AI Disease Prediction System
"""

## Quick Setup

1. Install Python 3.11 (TensorFlow requirement)
   - Download from: https://www.python.org/downloads/release/python-3115/
   - Choose Windows installer (64-bit)
   - During installation, check "Add Python 3.11 to PATH"

2. Create virtual environment:
```powershell
# Create venv using Python 3.11
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# If you get a security error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Set OpenAI API key (optional, for medical reports):
```powershell
$env:API_TOKEN = "your-openai-key"
```

5. Run the application:
```powershell
python run.py
```

6. Open in browser:
   - http://localhost:3000

## Demo Credentials

1. Admin User
   - Username: admin
   - Password: admin123

2. Doctor User
   - Username: doctor
   - Password: doctor123

## Features

1. Disease Prediction
   - Upload chest X-rays
   - Get AI predictions
   - View heatmap visualizations
   - Generate PDF reports

2. Patient Management
   - Add/view patients
   - Track patient history
   - View prediction history

3. Admin Features
   - User management
   - System statistics
   - Model management

## Directory Structure

- `app/` - Main application code
  - `models/` - AI models
  - `static/` - CSS, JS, images
  - `templates/` - HTML templates
  - `uploads/` - Patient images
- `instance/` - Instance-specific files (database)

## Troubleshooting

1. TensorFlow Issues
   - Ensure Python 3.11 is installed
   - Use 64-bit Python
   - Install Visual C++ Redistributable if needed

2. Database Issues
   - Delete `instance/app.db`
   - Restart application to recreate

3. OpenAI/Chat Features
   - Set API_TOKEN environment variable
   - Check OpenAI API key validity