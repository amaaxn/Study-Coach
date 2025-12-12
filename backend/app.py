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

app = Flask(__name__)
CORS(app, supports_credentials=True)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # We handle expiration in routes
jwt = JWTManager(app)

# Uploads folder
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Init MongoDB
init_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(courses_bp, url_prefix="/api/courses")
app.register_blueprint(plans_bp, url_prefix="/api/plans")
app.register_blueprint(materials_bp, url_prefix="/api/materials")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)