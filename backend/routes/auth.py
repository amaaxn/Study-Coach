from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import bcrypt
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    try:
        body = request.get_json() or {}
        
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")
        name = body.get("name", "").strip()
        
        # Validation
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Create user
        user = User.create(email=email, password_hash=password_hash, name=name)
        
        # Create access token
        access_token = create_access_token(
            identity=str(user["_id"]),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            "message": "User created successfully",
            "access_token": access_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
            }
        }), 201
    
    except Exception as e:
        return jsonify({"error": f"Failed to register: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and get access token."""
    try:
        body = request.get_json() or {}
        
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user
        user = User.find_by_email(email)
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Create access token
        access_token = create_access_token(
            identity=str(user["_id"]),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            "access_token": access_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to login: {str(e)}"}), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current authenticated user."""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to get user: {str(e)}"}), 500


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh():
    """Refresh access token."""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Create new access token
        access_token = create_access_token(
            identity=str(user["_id"]),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            "access_token": access_token
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to refresh token: {str(e)}"}), 500
