#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Hunter
# Date: February 5th 2026
# Version: 0.1.0

import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta


# Shared extensions initialized here and bound inside create_app()
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app() -> Flask:
    """Create and configure the Flask application."""
    load_dotenv()

    app = Flask(__name__)

    # Core configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-change-me")

    # Access tokens expire quickly (security)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)

    # Refresh tokens expire slowly (convenience)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

    # Database configuration
    database_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # CORS configuration to allow the frontend to call the API
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=False
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register API route blueprints
    from .routes.auth import bp as auth_bp
    from .routes.subscriptions import bp as subs_bp
    from .routes.candidates import bp as cand_bp
    from .routes.imports import bp as imports_bp
    from .routes.dashboard import bp as dash_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(subs_bp, url_prefix="/api/subscriptions")
    app.register_blueprint(cand_bp, url_prefix="/api/candidates")
    app.register_blueprint(imports_bp, url_prefix="/api/imports")
    app.register_blueprint(dash_bp, url_prefix="/api/dashboard")

    # Simple health check endpoint
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
