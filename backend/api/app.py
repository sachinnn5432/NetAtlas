"""Flask Application Factory for NetAtlas Platform.

Configures application security headers, CORS policies, Blueprint routing,
and static frontend distribution.
"""

from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.config.settings import (
    ALLOWED_ORIGINS,
    PROJECT_ROOT,
    NETATLAS_DEBUG
)
from backend.api.routes import api_bp
from backend.config.logging_config import logger

def create_app() -> Flask:
    """Creates and configures the Flask application."""
    frontend_public = PROJECT_ROOT / "frontend" / "public"

    app = Flask(
        __name__,
        static_folder=str(frontend_public),
        static_url_path=""
    )

    # CORS configuration
    CORS(
        app,
        origins=ALLOWED_ORIGINS,
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
    )

    # Register API blueprint
    app.register_blueprint(api_bp)

    # Security headers middleware
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Permissive script policy for open mapping CDNs (Leaflet, Plotly, OpenStreetMap)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: blob: https://*.tile.openstreetmap.org https://tile.openstreetmap.org https://unpkg.com; "
            "connect-src 'self' https://unpkg.com;"
        )
        return response

    # Frontend single-page entrypoint
    @app.route("/")
    def index():
        return send_from_directory(str(frontend_public), "index.html")

    logger.info("NetAtlas Flask application initialized.")
    return app

