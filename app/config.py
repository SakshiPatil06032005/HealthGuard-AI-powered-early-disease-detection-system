"""
Enhanced configuration for the AI Disease Prediction System
"""
import os
from datetime import timedelta

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database - Using SQLite for compatibility (MySQL can be set later)
    # For MySQL, uncomment the line below and set MYSQL_URI
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:sakshi123@localhost/disease_prediction'
    
    # For SQLite (default):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.abspath('uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Model settings
    MODEL_PATH = os.path.join('app', 'models', 'chest_xray_model.keras')
    
    # Gemini API for medical reports
    # You can set this via environment variable GEMINI_API_KEY
    GEMINI_API_KEY = 'AIzaSyB-uuKO7DU-fCBti0hlvHkd9RxCxig6Rq0'
    
    # Demo credentials - for hackathon only
    DEMO_DOCTOR = {
        "id": "mahima",
        "password": "mahima"
    }
    
    DEMO_USERS = {
        'admin': {'password': 'admin123', 'role': 'admin'},
        'doctor': {'password': 'doctor123', 'role': 'doctor'}
    }

    # Development settings
    DEBUG = True
    DEVELOPMENT = True
    SKIP_MODEL_LOAD = False  # Set to True to skip model loading for UI development
    
    @classmethod
    def init_app(cls, app):
        """Initialize application configuration."""
        # Create required directories
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs('app/static/heatmaps', exist_ok=True)
        
        # Initialize database
        with app.app_context():
            from app.models import db, User
            db.create_all()
            
            # Create demo users if they don't exist
            for username, data in cls.DEMO_USERS.items():
                if not User.query.filter_by(username=username).first():
                    user = User(username=username, role=data['role'])
                    user.set_password(data['password'])
                    db.session.add(user)
            
            try:
                db.session.commit()
            except Exception as e:
                app.logger.warning(f"Could not create demo users: {str(e)}")
                db.session.rollback()
        
        # Set up logging
        import logging
        logging.basicConfig(level=logging.INFO)
        
        # Development-specific setup
        if cls.SKIP_MODEL_LOAD:
            app.logger.warning("⚠️ Running in UI development mode - ML features disabled")
            db.session.commit()