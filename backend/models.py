from pymongo import MongoClient
from datetime import datetime, date
from bson import ObjectId
from typing import Optional, Dict, Any
import os
from functools import wraps

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "study_coach")

# Don't initialize client at module level - causes fork-safety issues with Gunicorn
# Initialize lazily on first use
_client = None
_db = None

def get_client():
    """Get MongoDB client, initializing if needed (fork-safe)."""
    global _client
    if _client is None:
        try:
            print(f"🔗 Connecting to MongoDB: {DB_NAME}")
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            _client.admin.command('ping')
            print("✅ MongoDB connection successful")
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            print(f"   URI: {MONGO_URI[:50]}..." if len(MONGO_URI) > 50 else f"   URI: {MONGO_URI}")
            raise
    return _client

def get_db():
    """Get MongoDB database, initializing client if needed."""
    global _db
    if _db is None:
        _db = get_client()[DB_NAME]
    return _db

# For backward compatibility, create lazy properties
class LazyDB:
    def __getattr__(self, name):
        return getattr(get_db(), name)

db = LazyDB()
client = None  # Will be set on first use

# Collections - use lazy initialization
def get_collection(name):
    """Get a collection by name (fork-safe)."""
    return get_db()[name]

def get_users_collection():
    return get_collection("users")

def get_courses_collection():
    return get_collection("courses")

def get_materials_collection():
    return get_collection("materials")

def get_study_tasks_collection():
    return get_collection("study_tasks")

# For backward compatibility, create lazy accessors
class LazyCollection:
    def __init__(self, name):
        self.name = name
    def __getattr__(self, attr):
        return getattr(get_collection(self.name), attr)
    def find(self, *args, **kwargs):
        return get_collection(self.name).find(*args, **kwargs)
    def find_one(self, *args, **kwargs):
        return get_collection(self.name).find_one(*args, **kwargs)
    def insert_one(self, *args, **kwargs):
        return get_collection(self.name).insert_one(*args, **kwargs)
    def update_one(self, *args, **kwargs):
        return get_collection(self.name).update_one(*args, **kwargs)
    def delete_many(self, *args, **kwargs):
        return get_collection(self.name).delete_many(*args, **kwargs)
    def create_index(self, *args, **kwargs):
        return get_collection(self.name).create_index(*args, **kwargs)
    def update_many(self, *args, **kwargs):
        return get_collection(self.name).update_many(*args, **kwargs)

users_collection = LazyCollection("users")
courses_collection = LazyCollection("courses")
materials_collection = LazyCollection("materials")
study_tasks_collection = LazyCollection("study_tasks")


def init_db():
    """Initialize database indexes (fork-safe - called after fork)."""
    # Create indexes for better query performance
    try:
        get_users_collection().create_index("email", unique=True)
        get_courses_collection().create_index("user_id")
        get_courses_collection().create_index([("user_id", 1), ("name", 1)])
        get_materials_collection().create_index("course_id")
        get_study_tasks_collection().create_index("course_id")
        get_study_tasks_collection().create_index([("course_id", 1), ("date", 1)])
        print("✅ Database indexes created successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not create indexes: {e}")
        # Don't fail startup if indexes can't be created


class User:
    @staticmethod
    def create(email: str, password_hash: str, name: str = None) -> Dict[str, Any]:
        """Create a new user."""
        user = {
            "email": email,
            "password_hash": password_hash,
            "name": name or "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = users_collection.insert_one(user)
        user["_id"] = result.inserted_id
        user["id"] = str(result.inserted_id)
        return user
    
    @staticmethod
    def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Find user by email."""
        user = users_collection.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
        return user
    
    @staticmethod
    def find_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by ID."""
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
            return user
        except:
            return None


class Course:
    @staticmethod
    def create(user_id: str, name: str, term_start: date, term_end: date, main_exam_date: date = None) -> Dict[str, Any]:
        """Create a new course."""
        course = {
            "user_id": ObjectId(user_id),
            "name": name,
            "term_start": term_start.isoformat(),
            "term_end": term_end.isoformat(),
            "main_exam_date": main_exam_date.isoformat() if main_exam_date else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = courses_collection.insert_one(course)
        course["_id"] = result.inserted_id
        course["id"] = str(result.inserted_id)
        return course
    
    @staticmethod
    def find_by_user(user_id: str) -> list:
        """Find all courses for a user."""
        courses = list(courses_collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))
        for course in courses:
            course["id"] = str(course["_id"])
        return courses
    
    @staticmethod
    def find_by_id(course_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Find course by ID, optionally verify ownership."""
        try:
            query = {"_id": ObjectId(course_id)}
            if user_id:
                query["user_id"] = ObjectId(user_id)
            
            course = courses_collection.find_one(query)
            if course:
                course["id"] = str(course["_id"])
            return course
        except:
            return None
    
    @staticmethod
    def delete(course_id: str, user_id: str) -> bool:
        """Delete a course and return True if successful."""
        try:
            result = courses_collection.delete_one({
                "_id": ObjectId(course_id),
                "user_id": ObjectId(user_id)
            })
            return result.deleted_count > 0
        except:
            return False


class Material:
    @staticmethod
    def create(course_id: str, title: str, file_path: str = None, raw_text: str = None, metadata_json: str = None) -> Dict[str, Any]:
        """Create a new material."""
        material = {
            "course_id": ObjectId(course_id),
            "title": title,
            "file_path": file_path,
            "raw_text": raw_text,
            "metadata_json": metadata_json,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = materials_collection.insert_one(material)
        material["_id"] = result.inserted_id
        material["id"] = str(result.inserted_id)
        return material
    
    @staticmethod
    def find_by_course(course_id: str) -> list:
        """Find all materials for a course."""
        materials = list(materials_collection.find({"course_id": ObjectId(course_id)}).sort("created_at", -1))
        for material in materials:
            material["id"] = str(material["_id"])
        return materials
    
    @staticmethod
    def find_by_id(material_id: str) -> Optional[Dict[str, Any]]:
        """Find material by ID."""
        try:
            material = materials_collection.find_one({"_id": ObjectId(material_id)})
            if material:
                material["id"] = str(material["_id"])
            return material
        except:
            return None
    
    @staticmethod
    def delete(material_id: str) -> bool:
        """Delete a material and return True if successful."""
        try:
            result = materials_collection.delete_one({"_id": ObjectId(material_id)})
            return result.deleted_count > 0
        except:
            return False


class StudyTask:
    @staticmethod
    def create(course_id: str, date: date, title: str, description: str = None, completed: bool = False, material_id: str = None) -> Dict[str, Any]:
        """Create a new study task."""
        task = {
            "course_id": ObjectId(course_id),
            "date": date.isoformat(),
            "title": title,
            "description": description,
            "completed": completed,
            "material_id": ObjectId(material_id) if material_id else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = study_tasks_collection.insert_one(task)
        task["_id"] = result.inserted_id
        task["id"] = str(result.inserted_id)
        return task
    
    @staticmethod
    def find_by_course(course_id: str) -> list:
        """Find all study tasks for a course."""
        tasks = list(study_tasks_collection.find({"course_id": ObjectId(course_id)}).sort("date", 1))
        for task in tasks:
            task["id"] = str(task["_id"])
        return tasks
    
    @staticmethod
    def delete_by_course(course_id: str):
        """Delete all study tasks for a course."""
        study_tasks_collection.delete_many({"course_id": ObjectId(course_id)})
    
    @staticmethod
    def delete_by_material(material_id: str):
        """Remove material reference from tasks."""
        study_tasks_collection.update_many(
            {"material_id": ObjectId(material_id)},
            {"$set": {"material_id": None}}
        )
