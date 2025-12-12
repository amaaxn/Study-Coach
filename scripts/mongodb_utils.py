#!/usr/bin/env python3
"""
MongoDB Utility Scripts for Study Coach
Use this script to manage your database from the command line.
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "study_coach")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def list_users():
    """List all users in the database."""
    users = db.users.find()
    print(f"\n=== Users ({db.users.count_documents({})} total) ===")
    for user in users:
        print(f"ID: {user['_id']}")
        print(f"  Email: {user['email']}")
        print(f"  Name: {user.get('name', 'N/A')}")
        print(f"  Created: {user.get('created_at', 'N/A')}")
        print()


def list_courses():
    """List all courses in the database."""
    courses = db.courses.find()
    print(f"\n=== Courses ({db.courses.count_documents({})} total) ===")
    for course in courses:
        user = db.users.find_one({"_id": course["user_id"]})
        user_email = user["email"] if user else "Unknown"
        print(f"ID: {course['_id']}")
        print(f"  Name: {course['name']}")
        print(f"  User: {user_email}")
        print(f"  Term: {course['term_start']} → {course['term_end']}")
        print()


def list_materials():
    """List all materials in the database."""
    materials = db.materials.find()
    print(f"\n=== Materials ({db.materials.count_documents({})} total) ===")
    for material in materials:
        course = db.courses.find_one({"_id": material["course_id"]})
        course_name = course["name"] if course else "Unknown"
        print(f"ID: {material['_id']}")
        print(f"  Title: {material['title']}")
        print(f"  Course: {course_name}")
        print(f"  File: {material.get('file_path', 'N/A')}")
        print()


def list_study_tasks():
    """List all study tasks in the database."""
    tasks = db.study_tasks.find()
    print(f"\n=== Study Tasks ({db.study_tasks.count_documents({})} total) ===")
    for task in tasks:
        course = db.courses.find_one({"_id": task["course_id"]})
        course_name = course["name"] if course else "Unknown"
        print(f"ID: {task['_id']}")
        print(f"  Course: {course_name}")
        print(f"  Date: {task['date']}")
        print(f"  Title: {task['title']}")
        print()


def stats():
    """Show database statistics."""
    print("\n=== Database Statistics ===")
    print(f"Database: {DB_NAME}")
    print(f"Users: {db.users.count_documents({})}")
    print(f"Courses: {db.courses.count_documents({})}")
    print(f"Materials: {db.materials.count_documents({})}")
    print(f"Study Tasks: {db.study_tasks.count_documents({})}")
    print()


def delete_user(email):
    """Delete a user and all their associated data."""
    user = db.users.find_one({"email": email})
    if not user:
        print(f"User with email {email} not found.")
        return
    
    user_id = user["_id"]
    confirm = input(f"Delete user {email} and ALL their courses, materials, and tasks? (yes/no): ")
    
    if confirm.lower() != "yes":
        print("Cancelled.")
        return
    
    # Delete user's courses and associated data
    courses = list(db.courses.find({"user_id": user_id}))
    for course in courses:
        # Delete materials
        db.materials.delete_many({"course_id": course["_id"]})
        # Delete study tasks
        db.study_tasks.delete_many({"course_id": course["_id"]})
    
    # Delete courses
    db.courses.delete_many({"user_id": user_id})
    
    # Delete user
    db.users.delete_one({"_id": user_id})
    
    print(f"User {email} and all associated data deleted.")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python mongodb_utils.py list-users")
        print("  python mongodb_utils.py list-courses")
        print("  python mongodb_utils.py list-materials")
        print("  python mongodb_utils.py list-tasks")
        print("  python mongodb_utils.py stats")
        print("  python mongodb_utils.py delete-user <email>")
        return
    
    command = sys.argv[1]
    
    if command == "list-users":
        list_users()
    elif command == "list-courses":
        list_courses()
    elif command == "list-materials":
        list_materials()
    elif command == "list-tasks":
        list_study_tasks()
    elif command == "stats":
        stats()
    elif command == "delete-user" and len(sys.argv) > 2:
        delete_user(sys.argv[2])
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
