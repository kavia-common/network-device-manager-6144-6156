import os
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from dotenv import load_dotenv

# Import routes and db after creating app to avoid circular imports
# Health BP import kept compatible with existing file
from .routes.health import blp as health_blp

def _get_bool_env(name: str, default: bool = False) -> bool:
    """Parse boolean-like environment variables."""
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "on")

# PUBLIC_INTERFACE
def create_app():
    """Create and configure the Flask application with API, CORS, and MongoDB.

    Returns:
        Flask: Configured Flask app instance.
    Notes:
        - Reads environment variables:
            FLASK_ENV, PORT, API_PREFIX, MONGODB_URI, MONGODB_DB,
            ENABLE_PING, CORS_ORIGINS
        - OpenAPI available under /docs and served with Swagger UI.
        - CORS defaults to allowing http://localhost:3000.
    """
    load_dotenv()

    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # OpenAPI / Swagger UI configuration
    app.config["API_TITLE"] = "Network Device Manager API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # API prefix
    api_prefix = os.getenv("API_PREFIX", "/api/v1").rstrip("/")
    app.config["API_PREFIX"] = api_prefix

    # CORS
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    CORS(app, resources={r"/*": {"origins": cors_origins}})

    # Ping feature flag
    app.config["ENABLE_PING"] = _get_bool_env("ENABLE_PING", True)

    # Mongo settings used by db module
    app.config["MONGODB_URI"] = os.getenv("MONGODB_URI")
    app.config["MONGODB_DB"] = os.getenv("MONGODB_DB")

    # Initialize API
    api = Api(app)

    # Register blueprints
    # Health at root
    api.register_blueprint(health_blp)

    # Devices routes (registered with API prefix)
    from .routes.devices import blp as devices_blp
    api.register_blueprint(devices_blp, url_prefix=f"{api_prefix}/devices")

    # Attach api to app for openapi generation script
    app.extensions = getattr(app, "extensions", {})
    app.extensions["smorest_api"] = api  # reference for generate_openapi

    return app

# For compatibility with existing import style in generate_openapi and run.py
app = create_app()
api = app.extensions["smorest_api"]
