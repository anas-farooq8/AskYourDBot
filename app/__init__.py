from flask import Flask                    # Flask application class
from app.settings.config import Config     # Application configuration
from app.routes.routes import bp           # Blueprint holding your route definitions

def create_app():
    """
    Application factory function.

    This creates and configures the Flask app instance:
      1. Instantiates Flask with the current module’s name.
      2. Loads configuration from the Config class.
      3. Registers your routes blueprint.
      4. Returns the fully configured app.
    """
    # 1) Create the Flask application
    app = Flask(__name__)
    
    # 2) Load configuration settings
    app.config.from_object(Config)
    
    # 3) Register the routes blueprint
    app.register_blueprint(bp)
    
    # 4) Return the configured Flask app
    return app
