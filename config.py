"""
Development configuration for the AI Disease Prediction System.
"""
import os

class Config:
    """Base configuration."""
    # Security
    SECRET_KEY = os.urandom(32)
    
    # File upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.abspath("uploads")
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Model settings
    MODEL_PATH = os.path.join("app", "models", "chest_xray_model.keras")
    
    # OpenAI integration
    OPENAI_API_KEY = os.getenv("API_TOKEN")
    
    # Demo/development credentials
    DEMO_DOCTOR = {
        "id": "mahima",
        "password": "mahima"
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DEVELOPMENT = True
    
    # Optional: Set to True to skip model loading for UI development
    SKIP_MODEL_LOAD = False
    
    @classmethod
    def init_app(cls, app):
        """Initialize the development configuration."""
        # Ensure required directories exist
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs("app/static/heatmaps", exist_ok=True)
        
        # Set up logging
        import logging
        logging.basicConfig(level=logging.INFO)
        
        # Development-specific setup
        if cls.SKIP_MODEL_LOAD:
            app.logger.warning("⚠️ Running in UI development mode - ML features disabled")
        
        if not os.path.exists(cls.MODEL_PATH):
            app.logger.warning(f"⚠️ Model not found at {cls.MODEL_PATH}")
        
        if not cls.OPENAI_API_KEY:
            app.logger.warning("⚠️ API_TOKEN not set - medical explanations will be disabled")