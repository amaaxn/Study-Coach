# backend/routes/courses.py
from flask import Blueprint, request, jsonify, current_app
from datetime import date
import os

from models import Course, Material, StudyTask
from middleware import require_auth


courses_bp = Blueprint("courses", __name__)


@courses_bp.route("", methods=["GET"])
@require_auth
def list_courses(user_id):
    """GET /api/courses - Get all courses for the authenticated user."""
    try:
        courses = Course.find_by_user(user_id)
        
        data = [
            {
                "id": c["id"],
                "name": c["name"],
                "termStart": c["term_start"],
                "termEnd": c["term_end"],
                "mainExamDate": c.get("main_exam_date"),
            }
            for c in courses
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch courses: {str(e)}"}), 500


@courses_bp.route("", methods=["POST"])
@require_auth
def create_course(user_id):
    """POST /api/courses - Create a new course."""
    try:
        body = request.get_json() or {}

        name = body.get("name")
        term_start_str = body.get("termStart")
        term_end_str = body.get("termEnd")
        exam_str = body.get("mainExamDate")

        if not name or not term_start_str or not term_end_str:
            return jsonify({"error": "Missing required fields"}), 400

        try:
            # HTML date inputs return "YYYY-MM-DD" format
            term_start = date.fromisoformat(term_start_str)
            term_end = date.fromisoformat(term_end_str)
            main_exam_date = None
            if exam_str:
                main_exam_date = date.fromisoformat(exam_str)
        except ValueError as e:
            return jsonify({"error": f"Invalid date format: {str(e)}"}), 400

        course = Course.create(
            user_id=user_id,
            name=name,
            term_start=term_start,
            term_end=term_end,
            main_exam_date=main_exam_date,
        )

        return jsonify({
            "id": course["id"],
            "name": course["name"],
            "termStart": course["term_start"],
            "termEnd": course["term_end"],
            "mainExamDate": course.get("main_exam_date"),
        }), 201
    except Exception as e:
        return jsonify({"error": f"Failed to save course: {str(e)}"}), 500


@courses_bp.route("/<string:course_id>", methods=["DELETE"])
@require_auth
def delete_course(course_id, user_id):
    """DELETE /api/courses/<course_id> - Delete a course and all associated materials and study tasks."""
    try:
        # Verify course exists and belongs to user
        course = Course.find_by_id(course_id, user_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        # Delete associated materials and their files
        materials = Material.find_by_course(course_id)
        for material in materials:
            if material.get("file_path"):
                upload_folder = current_app.config["UPLOAD_FOLDER"]
                file_path = os.path.join(upload_folder, material["file_path"])
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")
        
        # Delete study tasks
        StudyTask.delete_by_course(course_id)
        
        # Delete materials
        for material in materials:
            Material.delete(material["id"])
        
        # Delete the course
        success = Course.delete(course_id, user_id)
        
        if not success:
            return jsonify({"error": "Failed to delete course"}), 500
        
        return jsonify({"message": "Course deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete course: {str(e)}"}), 500
