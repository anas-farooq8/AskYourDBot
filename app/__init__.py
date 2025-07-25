from flask import Flask                    # Flask application class
from app.settings.config import Config     # Application configuration
from app.routes.routes import bp           # Blueprint holding your route definitions
from app.utils.logger import setup_logging, get_logger

def create_app():
    """
    Application factory function.

    This creates and configures the Flask app instance:
      1. Setup centralized logging system
      2. Instantiates Flask with the current module's name.
      3. Loads configuration from the Config class.
      4. Registers your routes blueprint.
      5. Returns the fully configured app.
    """
    # 1) Setup logging before anything else
    setup_logging()
    logger = get_logger(__name__)
    logger.info("🚀 Initializing AskYourDBot application")
    
    # 2) Create the Flask application
    app = Flask(__name__)
    
    # 3) Load configuration settings
    app.config.from_object(Config)
    logger.info(f"📋 Loaded config - Environment: {Config.FLASK_ENV}, Debug: {Config.DEBUG}, Host: {Config.HOST}, Port: {Config.PORT}")
    
    # 4) Register the routes blueprint
    app.register_blueprint(bp)
    logger.info("🔗 Registered routes blueprint")
    
    # 5) Return the configured Flask app
    logger.info("✅ Application factory completed successfully")
    return app
