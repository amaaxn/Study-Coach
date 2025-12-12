"""
AI-Enhanced Study Planner using LLM for intelligent plan generation.
"""
from datetime import date, timedelta
from typing import List, Dict, Optional
import json
from models import Material
from services.llm_service import (
    generate_study_plan_with_ai,
    extract_topics_with_ai,
    analyze_syllabus_for_schedule
)
from services.pdf_analyzer import split_content_for_study


def generate_ai_study_plan(course: Dict) -> List[Dict]:
    """
    Generate AI-powered study plan for a course.
    Combines structured content analysis with LLM intelligence.
    """
    start = date.fromisoformat(course["term_start"])
    exam_date_str = course.get("main_exam_date")
    exam_date = date.fromisoformat(exam_date_str) if exam_date_str else None
    end_str = course["term_end"]
    
    try:
        end = date.fromisoformat(end_str) if end_str else start
    except:
        end = start
    
    if end < start:
        end = start

    total_days = (end - start).days + 1
    if total_days <= 0:
        total_days = 1

    course_id = course["id"]
    materials = Material.find_by_course(course_id)
    
    # Extract topics using AI
    all_topics = []
    all_sections = []
    syllabus_data = {}
    
    for material in materials:
        # Use AI to extract topics from PDF text
        if material.get("raw_text"):
            ai_topics = extract_topics_with_ai(material["raw_text"], course.get("name", ""))
            all_topics.extend(ai_topics)
            
            # Analyze syllabus for schedule if it looks like a syllabus
            if "syllabus" in material.get("title", "").lower() or "course outline" in material.get("title", "").lower():
                syllabus_data = analyze_syllabus_for_schedule(material["raw_text"])
        
        # Get structured sections from PDF
        if material.get("metadata_json"):
            try:
                pdf_structure = json.loads(material["metadata_json"])
                sections = pdf_structure.get("sections", [])
                if sections:
                    all_sections.extend(sections)
                    for section in sections:
                        section["materialId"] = material["id"]
                        section["materialTitle"] = material["title"]
            except Exception as e:
                print(f"Error parsing PDF structure: {e}")

    # Determine number of sessions
    if total_days <= 7:
        num_sessions = min(3, total_days)
    elif total_days <= 30:
        num_sessions = min(8, total_days // 3)
    elif total_days <= 60:
        num_sessions = min(12, total_days // 5)
    else:
        num_sessions = min(16, total_days // 7)
    
    if num_sessions <= 0:
        num_sessions = 1

    # Calculate session dates with spaced repetition
    session_dates = _calculate_session_dates(start, end, num_sessions, exam_date)
    
    # Generate AI study plan
    try:
        ai_sessions = generate_study_plan_with_ai(
            course,
            all_topics[:20],
            all_sections[:10],
            num_sessions
        )
        
        # Combine AI-generated content with dates and sections
        tasks = []
        for i, session_date in enumerate(session_dates):
            if i < len(ai_sessions):
                # Use AI-generated session
                ai_session = ai_sessions[i]
                title = ai_session.get("title", f"Study Session {i + 1}")
                description = ai_session.get("description", "Study course materials")
            else:
                # Fallback if AI didn't generate enough
                title = f"Study Session {i + 1}"
                description = "Review course materials and practice key concepts"
            
            # Enhance with section/page info if available
            if i < len(all_sections):
                section = all_sections[i % len(all_sections)]
                pages = section.get("pageNumbers", [])
                if pages:
                    page_range = f"{min(pages)}-{max(pages)}" if len(pages) > 1 else str(pages[0])
                    description = f"Pages {page_range}: {description}"
            
            tasks.append({
                "course_id": course_id,
                "date": session_date.isoformat(),
                "title": title,
                "description": description,
                "completed": False,
            })
        
        return tasks
    except Exception as e:
        print(f"Error generating AI study plan, using fallback: {e}")
        # Fallback to basic plan
        return _generate_fallback_plan(course, session_dates, all_topics, all_sections)


def _calculate_session_dates(start: date, end: date, num_sessions: int, exam_date: date = None) -> List[date]:
    """Calculate session dates using spaced repetition."""
    total_days = (end - start).days + 1
    if total_days <= 1:
        return [start]

    dates = []
    
    if exam_date and num_sessions > 4:
        # Two-phase: regular spacing early, intensive near exam
        exam_prep_days = min(14, (end - exam_date).days) if exam_date else 0
        early_sessions = max(1, num_sessions // 2)
        prep_sessions = num_sessions - early_sessions
        
        early_end = max(start, exam_date - timedelta(days=exam_prep_days + 1))
        early_days = (early_end - start).days + 1
        if early_days > 0:
            early_step = max(1, early_days // max(1, early_sessions))
            for i in range(early_sessions):
                day_offset = i * early_step
                session_date = start + timedelta(days=day_offset)
                if session_date <= early_end:
                    dates.append(session_date)
        
        prep_start = max(dates[-1] + timedelta(days=3), exam_date - timedelta(days=exam_prep_days)) if dates else exam_date - timedelta(days=exam_prep_days)
        prep_end = exam_date - timedelta(days=1)
        prep_days = (prep_end - prep_start).days + 1
        if prep_days > 0:
            prep_step = max(1, prep_days // max(1, prep_sessions))
            for i in range(prep_sessions):
                day_offset = i * prep_step
                session_date = prep_start + timedelta(days=day_offset)
                if session_date < exam_date and session_date not in dates:
                    dates.append(session_date)
    else:
        # Simple exponential spacing
        for i in range(num_sessions):
            progress = (i + 1) / num_sessions
            day_position = int(total_days * (progress ** 1.5))
            session_date = start + timedelta(days=min(day_position, total_days - 1))
            if session_date not in dates:
                dates.append(session_date)

    dates = sorted(set(dates))
    return dates[:num_sessions]


def _generate_fallback_plan(
    course: Dict,
    session_dates: List[date],
    topics: List[str],
    sections: List[Dict]
) -> List[Dict]:
    """Fallback plan generation if AI fails."""
    tasks = []
    course_id = course["id"]
    
    for i, session_date in enumerate(session_dates):
        if i == 0:
            title = "Course Overview & Initial Review"
            description = f"Review course syllabus and materials for {course['name']}. Set up study schedule."
        elif i < len(topics):
            topic = topics[i % len(topics)]
            title = f"Study: {topic[:50]}"
            description = f"Study and take notes on: {topic}. Review key concepts and practice problems."
        else:
            title = f"Review Session {i + 1}"
            description = "Review course materials, practice problems, and self-test on key concepts."
        
        tasks.append({
            "course_id": course_id,
            "date": session_date.isoformat(),
            "title": title,
            "description": description,
            "completed": False,
        })
    
    return tasks
