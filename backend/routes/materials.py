from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

from models import Material, Course, StudyTask
from middleware import require_auth

materials_bp = Blueprint("materials", __name__)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@materials_bp.route("/<string:course_id>", methods=["GET"])
@require_auth
def list_materials(course_id, user_id):
    """List all materials for a course."""
    try:
        # Verify course belongs to user
        course = Course.find_by_id(course_id, user_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        materials = Material.find_by_course(course_id)
        data = [
            {
                "id": m["id"],
                "title": m["title"],
                "filePath": m.get("file_path"),
            }
            for m in materials
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch materials: {str(e)}"}), 500


@materials_bp.route("/upload", methods=["POST"])
@require_auth
def upload_material(user_id):
    """
    Upload a PDF and attach it to a course.
    Expects multipart/form-data with:
      - file: the PDF
      - courseId: the string course id
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    course_id = request.form.get("courseId")
    if not course_id:
        return jsonify({"error": "Missing courseId"}), 400

    try:
        # Verify course belongs to user
        course = Course.find_by_id(course_id, user_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404

        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type"}), 400

        filename = secure_filename(file.filename)
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)

        # Avoid overwriting: if file exists, add suffix
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            filename = f"{base}_{counter}{ext}"
            file_path = os.path.join(upload_folder, filename)
            counter += 1

        file.save(file_path)

        # Extract text and analyze PDF structure
        raw_text = ""
        pdf_structure = None
        try:
            from services.pdf_analyzer import analyze_pdf_structure
            pdf_structure = analyze_pdf_structure(file_path)
            
            # Extract full text for backward compatibility
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            pages_text = []
            for page in reader.pages:
                txt = page.extract_text() or ""
                pages_text.append(txt)
            raw_text = "\n".join(pages_text)
        except Exception as e:
            raw_text = ""
            print("Error reading PDF:", e)
            import traceback
            traceback.print_exc()

        # Store structured content in metadata_json
        metadata_json = None
        if pdf_structure:
            import json
            metadata_json = json.dumps(pdf_structure)

        material = Material.create(
            course_id=course_id,
            title=file.filename,
            file_path=filename,
            raw_text=raw_text,
            metadata_json=metadata_json,
        )

        return jsonify(
            {
                "id": material["id"],
                "title": material["title"],
                "filePath": material.get("file_path"),
            }
        ), 201
    except Exception as e:
        return jsonify({"error": f"Failed to upload material: {str(e)}"}), 500


@materials_bp.route("/<string:material_id>", methods=["DELETE"])
@require_auth
def delete_material(material_id, user_id):
    """Delete a material and its associated file."""
    try:
        material = Material.find_by_id(material_id)
        if not material:
            return jsonify({"error": "Material not found"}), 404
        
        # Verify course belongs to user
        from bson import ObjectId
        course_id_str = str(material["course_id"]) if isinstance(material["course_id"], ObjectId) else material["course_id"]
        course = Course.find_by_id(course_id_str, user_id)
        if not course:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Delete the physical file if it exists
        if material.get("file_path"):
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            file_path = os.path.join(upload_folder, material["file_path"])
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
        
        # Remove material reference from study tasks
        StudyTask.delete_by_material(material_id)
        
        # Delete the database record
        success = Material.delete(material_id)
        
        if not success:
            return jsonify({"error": "Failed to delete material"}), 500
        
        return jsonify({"message": "Material deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete material: {str(e)}"}), 500
