from flask import Blueprint, request, jsonify
from models import Course, StudyTask
from services.llm_service import chatbot_response
from middleware import require_auth
from bson import ObjectId
from datetime import datetime

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/message", methods=["POST"])
@require_auth
def send_message(user_id):
    """Send a message to the AI chatbot and get response."""
    try:
        body = request.get_json() or {}
        user_message = body.get("message", "").strip()
        conversation_history = body.get("history", [])  # List of {role, content}
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get user context (courses, current study plans)
        courses = Course.find_by_user(user_id)
        
        # Get study tasks for context
        all_tasks = []
        for course in courses[:5]:  # Limit to 5 courses for context
            tasks = StudyTask.find_by_course(course["id"])
            all_tasks.extend(tasks[:10])  # Limit tasks per course
        
        user_context = {
            "courses": courses[:5],
            "study_tasks": all_tasks[:20]
        }
        
        # Get AI response
        ai_response = chatbot_response(user_message, user_context, conversation_history)
        
        return jsonify({
            "response": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": f"Failed to get response: {str(e)}"}), 500
