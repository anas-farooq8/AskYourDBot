from app import create_app                 # Import the application factory
from app.settings.config import Config     # Import centralized configuration

# Instantiate the Flask application
app = create_app()

if __name__ == "__main__":
    # When executed as the main program, start the Flask development server
    # with host, port, and debug settings pulled from the Config class.
    app.run(
        host=Config.HOST,       # Network interface to bind to (e.g., "0.0.0.0")
        port=Config.PORT,       # TCP port to listen on (e.g., 5000)
        debug=Config.DEBUG      # Enable debug mode if True (auto-reloads on change)
    )
