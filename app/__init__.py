from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.routes import routes
from app.models import db
from app.config import Config
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Load config from Config class
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Create database tables and initialize app
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            logger.info("✅ Database tables created/verified successfully")
            
            # Create uploads directory if it doesn't exist (use absolute path to avoid permission issues)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            uploads_dir = os.path.join(project_root, 'uploads')
            heatmaps_dir = os.path.join(project_root, 'app', 'static', 'heatmaps')
            
            os.makedirs(uploads_dir, exist_ok=True)
            os.makedirs(heatmaps_dir, exist_ok=True)
            
            # Initialize disease predictor model (skip in dev mode to avoid heavy ML deps)
            try:
                if not app.config.get('SKIP_MODEL_LOAD', False):
                    from app.disease_model import disease_predictor
                    logger.info("✅ Disease prediction model initialized")
                else:
                    logger.info("⚠️ SKIP_MODEL_LOAD enabled — skipping disease model initialization")
            except Exception as e:
                logger.error(f"❌ Error initializing disease model: {e}")
                import traceback
                traceback.print_exc()
            
            # Initialize medicine recommender with Gemini API
            try:
                from app.medicine_recommender import medicine_recommender
                gemini_key = app.config.get('GEMINI_API_KEY', '')
                if gemini_key and gemini_key != 'your-gemini-api-key-here':
                    # Re-initialize with the correct API key from config
                    medicine_recommender.__init__(gemini_api_key=gemini_key)
                    logger.info("✅ Medicine recommender initialized with Gemini API")
                else:
                    logger.warning("⚠️ Gemini API key not configured - using fallback recommendations")
            except Exception as e:
                logger.error(f"❌ Error initializing medicine recommender: {e}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing application: {e}")
            import traceback
            traceback.print_exc()
    
    # Register blueprints
    app.register_blueprint(routes)
    
    from app.auth_routes import auth
    from app.dashboard_routes import dashboards
    
    app.register_blueprint(auth)
    app.register_blueprint(dashboards)
    
    return app