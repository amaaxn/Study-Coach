# backend/app.py
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

from models import init_db
from routes.auth import auth_bp
from routes.courses import courses_bp
from routes.plans import plans_bp
from routes.materials import materials_bp
from routes.chat import chat_bp

app = Flask(__name__)

# Production configuration
IS_PRODUCTION = os.getenv("FLASK_ENV") == "production" or os.getenv("ENVIRONMENT") == "production"

# CORS Configuration - restrict to production domain in production
if IS_PRODUCTION:
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    if not frontend_url:
        raise ValueError("FRONTEND_URL must be set in production environment")
    
    # Support both with and without trailing slash
    allowed_origins = [frontend_url.rstrip('/'), frontend_url]
    # Remove duplicates while preserving order
    allowed_origins = list(dict.fromkeys(allowed_origins))
    
    CORS(app, 
         origins=allowed_origins,
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
else:
    # Development: allow all origins
    CORS(app, supports_credentials=True)

# JWT Configuration
jwt_secret = os.getenv("JWT_SECRET_KEY")
if IS_PRODUCTION:
    if not jwt_secret or jwt_secret == "dev-secret-key-change-in-production":
        raise ValueError("JWT_SECRET_KEY must be set to a strong random string in production")
    if len(jwt_secret) < 32:
        raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production")
else:
    jwt_secret = jwt_secret or "dev-secret-key-change-in-production"

app.config["JWT_SECRET_KEY"] = jwt_secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # We handle expiration in routes
app.config["JWT_COOKIE_SECURE"] = IS_PRODUCTION  # Only send over HTTPS in production
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
jwt = JWTManager(app)

# Uploads folder
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Security headers for production
@app.after_request
def set_security_headers(response):
    if IS_PRODUCTION:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Init MongoDB
init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(courses_bp, url_prefix="/api/courses")
app.register_blueprint(plans_bp, url_prefix="/api/plans")
app.register_blueprint(materials_bp, url_prefix="/api/materials")
app.register_blueprint(chat_bp, url_prefix="/api/chat")


@app.route("/api/health")
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "ok",
        "environment": "production" if IS_PRODUCTION else "development"
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    if IS_PRODUCTION:
        return jsonify({"error": "An internal error occurred"}), 500
    else:
        return jsonify({"error": str(error)}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413


if __name__ == "__main__":
    # For development only
    port = int(os.getenv("PORT", 5001))
    app.run(debug=os.getenv("FLASK_ENV") != "production", port=port, host="0.0.0.0")