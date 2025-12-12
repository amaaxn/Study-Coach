from flask import Blueprint, jsonify
from models import Course, StudyTask
from services.planner import generate_study_tasks_for_course
from middleware import require_auth

plans_bp = Blueprint("plans", __name__)


@plans_bp.route("/<string:course_id>", methods=["GET"])
@require_auth
def get_plan(course_id, user_id):
    """Return all study tasks for a given course."""
    try:
        # Verify course belongs to user
        course = Course.find_by_id(course_id, user_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        tasks = StudyTask.find_by_course(course_id)
        
        data = [
            {
                "id": t["id"],
                "date": t["date"],
                "title": t["title"],
                "description": t.get("description"),
                "completed": t.get("completed", False),
            }
            for t in tasks
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch plan: {str(e)}"}), 500


@plans_bp.route("/generate/<string:course_id>", methods=["POST"])
@require_auth
def generate_plan(course_id, user_id):
    """Generate a new plan for a course (overwrite existing tasks for now)."""
    try:
        # Verify course belongs to user
        course = Course.find_by_id(course_id, user_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        # Delete existing tasks
        StudyTask.delete_by_course(course_id)
        
        # Generate new tasks
        new_tasks = generate_study_tasks_for_course(course)
        for t in new_tasks:
            from datetime import date as date_type
            task_date = date_type.fromisoformat(t["date"])
            StudyTask.create(
                course_id=course_id,
                date=task_date,
                title=t["title"],
                description=t.get("description"),
                completed=t.get("completed", False),
                material_id=t.get("material_id"),
            )

        return jsonify({"created": len(new_tasks)}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to generate plan: {str(e)}"}), 500
