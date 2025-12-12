from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User


def get_current_user_id():
    """Get current authenticated user ID from JWT token."""
    return get_jwt_identity()


def require_auth(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_current_user_id()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Add user_id to kwargs for route functions
        kwargs['user_id'] = user_id
        return f(*args, **kwargs)
    
    return decorated_function
