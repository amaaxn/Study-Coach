# backend/app.py
import os
import sys
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Enable better error logging
sys.stdout.flush()
sys.stderr.flush()

print("🚀 Starting Learnium Backend...")
print(f"🔧 Python version: {sys.version}")

load_dotenv()
print("✅ Environment variables loaded")

from models import init_db
from routes.auth import auth_bp
from routes.courses import courses_bp
from routes.plans import plans_bp
from routes.materials import materials_bp
from routes.chat import chat_bp

app = Flask(__name__)

# Production configuration
IS_PRODUCTION = os.getenv("FLASK_ENV") == "production" or os.getenv("ENVIRONMENT") == "production"

print(f"🔧 Environment: {'PRODUCTION' if IS_PRODUCTION else 'DEVELOPMENT'}")
print(f"🔧 FLASK_ENV: {os.getenv('FLASK_ENV')}")
print(f"🔧 ENVIRONMENT: {os.getenv('ENVIRONMENT')}")

# CORS Configuration - restrict to production domain in production
if IS_PRODUCTION:
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    print(f"🔧 FRONTEND_URL: {frontend_url if frontend_url else 'NOT SET'}")
    
    if not frontend_url:
        print("⚠️  WARNING: FRONTEND_URL not set in production. Using permissive CORS.")
        # Don't crash - use permissive CORS but log warning
        CORS(app, supports_credentials=True)
    else:
        # Normalize URL - ensure HTTPS for production
        if frontend_url.startswith("http://") and IS_PRODUCTION:
            print(f"⚠️  WARNING: FRONTEND_URL uses HTTP, converting to HTTPS for production")
            frontend_url = frontend_url.replace("http://", "https://", 1)
        
        # Support both with and without trailing slash, and both http/https variants
        allowed_origins = [
            frontend_url.rstrip('/'),
            frontend_url,
            frontend_url.replace("https://", "http://", 1),  # Allow HTTP too for flexibility
            frontend_url.replace("http://", "https://", 1).rstrip('/')
        ]
        # Remove duplicates while preserving order
        allowed_origins = list(dict.fromkeys([o for o in allowed_origins if o]))
        print(f"✅ CORS configured for: {allowed_origins}")
        
        CORS(app, 
             origins=allowed_origins,
             supports_credentials=True,
             allow_headers=["Content-Type", "Authorization"],
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
else:
    # Development: allow all origins
    print("✅ CORS configured for development (all origins)")
    CORS(app, supports_credentials=True)

# JWT Configuration
jwt_secret = os.getenv("JWT_SECRET_KEY")
if IS_PRODUCTION:
    if not jwt_secret or jwt_secret == "dev-secret-key-change-in-production":
        print("⚠️  WARNING: JWT_SECRET_KEY not set or using default. Generating temporary secret.")
        # Generate a temporary secret instead of crashing
        import secrets
        jwt_secret = secrets.token_urlsafe(32)
        print("⚠️  WARNING: Using temporary JWT secret. Set JWT_SECRET_KEY in environment variables!")
    elif len(jwt_secret) < 32:
        print("⚠️  WARNING: JWT_SECRET_KEY is too short. Generating temporary secret.")
        import secrets
        jwt_secret = secrets.token_urlsafe(32)
    else:
        print("✅ JWT_SECRET_KEY configured")
else:
    jwt_secret = jwt_secret or "dev-secret-key-change-in-production"
    print("✅ JWT using development secret")

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

# Init MongoDB - defer actual connection until first use (fork-safe)
# Just initialize indexes, which will connect on first use
try:
    init_db()
    print("✅ MongoDB initialization setup complete (connection deferred for fork-safety)")
except Exception as e:
    print(f"⚠️  Warning: MongoDB initialization setup error: {e}")
    # Don't crash - connection will happen on first use

# Register blueprints
try:
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")
    app.register_blueprint(plans_bp, url_prefix="/api/plans")
    app.register_blueprint(materials_bp, url_prefix="/api/materials")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    
    # Debug: Print registered auth routes
    print("✅ All routes registered successfully")
    print(f"   Auth routes: POST /api/auth/register, POST /api/auth/login, GET /api/auth/me")
except Exception as e:
    print(f"❌ Error registering routes: {e}")
    import traceback
    traceback.print_exc()
    raise


@app.route("/api/health")
@app.route("/health")
@app.route("/")
def health():
    """Health check endpoint for monitoring and Railway health checks."""
    try:
        # Test MongoDB connection
        from models import get_db
        db = get_db()
        db.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "ok",
        "environment": "production" if IS_PRODUCTION else "development",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

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
    # Can be used in production as fallback if gunicorn fails
    port = int(os.getenv("PORT", 5001))
    debug_mode = os.getenv("FLASK_ENV") != "production" and os.getenv("ENVIRONMENT") != "production"
    print(f"🚀 Starting Flask server on port {port}")
    print(f"✅ Application ready! Environment: {'PRODUCTION' if IS_PRODUCTION else 'DEVELOPMENT'}")
    app.run(debug=debug_mode, port=port, host="0.0.0.0")