from flask import Blueprint, jsonify
from models import Course, StudyTask
from services.ai_planner import generate_ai_study_plan
from middleware import require_auth
from datetime import date, datetime
from bson import ObjectId

# Import collection directly
from models import study_tasks_collection

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
        
        # Generate new AI-powered tasks
        new_tasks = generate_ai_study_plan(course)
        for t in new_tasks:
            task_date = date.fromisoformat(t["date"])
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


@plans_bp.route("/today", methods=["GET"])
@require_auth
def get_today_plan(user_id):
    """Get today's study plan across all courses."""
    try:
        from datetime import timedelta
        # Get today's date in server timezone - frontend will filter by user's local date
        today_dt = date.today()
        today_str = today_dt.isoformat()
        
        # Get all user's courses
        courses = Course.find_by_user(user_id)
        
        # Return tasks from yesterday to 4 days ahead to ensure we catch "today" in any timezone
        # Frontend will filter based on user's local date
        date_range_start = (today_dt - timedelta(days=1)).isoformat()
        date_range_end = (today_dt + timedelta(days=4)).isoformat()
        
        today_tasks = []
        for course in courses:
            tasks = StudyTask.find_by_course(course["id"])
            for task in tasks:
                task_date_str = task.get("date")
                if task_date_str:
                    # Include tasks within date range (frontend filters by local date)
                    if date_range_start <= task_date_str <= date_range_end:
                        task_dict = {
                            "id": task["id"],
                            "courseId": course["id"],
                            "courseName": course["name"],
                            "date": task["date"],
                            "title": task["title"],
                            "description": task.get("description"),
                            "completed": task.get("completed", False),
                        }
                        today_tasks.append(task_dict)
        
        # Also get upcoming tasks (next 3 days) for context
        upcoming_tasks = []
        for course in courses:
            tasks = StudyTask.find_by_course(course["id"])
            for task in tasks:
                task_date_str = task.get("date")
                if task_date_str:
                    try:
                        task_date = date.fromisoformat(task_date_str)
                        today_dt = date.today()
                        days_ahead = (task_date - today_dt).days
                        if 1 <= days_ahead <= 3:
                            upcoming_tasks.append({
                                "id": task["id"],
                                "courseId": course["id"],
                                "courseName": course["name"],
                                "date": task_date_str,
                                "title": task["title"],
                                "daysAhead": days_ahead,
                            })
                    except:
                        pass
        
        return jsonify({
            "today": today_tasks,
            "upcoming": sorted(upcoming_tasks, key=lambda x: x["daysAhead"])[:5],
            "date": today_str
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to get today's plan: {str(e)}"}), 500


@plans_bp.route("/task/<string:task_id>/complete", methods=["PUT"])
@require_auth
def toggle_task_completion(task_id, user_id):
    """Toggle completion status of a study task."""
    try:
        from models import study_tasks_collection
        
        # Verify task exists and belongs to user's course
        task = study_tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        # Verify course belongs to user
        course = Course.find_by_id(str(task["course_id"]), user_id)
        if not course:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Toggle completion
        new_completed = not task.get("completed", False)
        study_tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"completed": new_completed, "updated_at": datetime.utcnow()}}
        )
        
        return jsonify({"completed": new_completed}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to update task: {str(e)}"}), 500
