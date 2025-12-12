from datetime import date, timedelta
from typing import List, Dict, Optional
import json
from models import Material, StudyTask
from services.topic_extractor import extract_topics_from_material, extract_key_terms
from services.pdf_analyzer import split_content_for_study


def generate_study_tasks_for_course(course: Dict) -> List[Dict]:
    """
    Generate intelligent study tasks based on:
    - Course timeline (term start, end, exam date)
    - Topics extracted from uploaded materials
    - Spaced repetition principles (more frequent sessions near exam)
    - Varied study activities
    """
    start = date.fromisoformat(course["term_start"])
    exam_date_str = course.get("main_exam_date")
    exam_date = date.fromisoformat(exam_date_str) if exam_date_str else None
    end_str = course["term_end"]
    end = date.fromisoformat(end_str) if end_str else start

    if end < start:
        end = course.term_end

    total_days = (end - start).days + 1
    if total_days <= 0:
        total_days = 1

    # Extract topics and structured content from materials
    all_topics = []
    key_terms = []
    all_sections = []
    material_content_chunks = []
    
    course_id = course["id"]
    materials = Material.find_by_course(course_id)
    
    for material in materials:
        topics = extract_topics_from_material(material)
        all_topics.extend(topics)
        terms = extract_key_terms(material)
        key_terms.extend(terms)
        
        # Extract structured content from PDF
        if material.get("metadata_json"):
            try:
                pdf_structure = json.loads(material["metadata_json"])
                sections = pdf_structure.get("sections", [])
                if sections:
                    all_sections.extend(sections)
                    # Store material reference with sections
                    for section in sections:
                        section["materialId"] = material["id"]
                        section["materialTitle"] = material["title"]
            except Exception as e:
                print(f"Error parsing PDF structure for material {material.get('id')}: {e}")

    # Remove duplicates while preserving order
    seen = set()
    unique_topics = []
    for topic in all_topics:
        topic_lower = topic.lower()
        if topic_lower not in seen:
            seen.add(topic_lower)
            unique_topics.append(topic)

    # Split content into study chunks if we have structured sections
    content_chunks = None
    if all_sections:
        # Determine number of study sessions first
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
        
        content_chunks = split_content_for_study(all_sections, num_sessions)

    # Determine number of study sessions based on timeline
    if content_chunks:
        num_sessions = len(content_chunks)
    elif total_days <= 7:
        num_sessions = min(3, total_days)
    elif total_days <= 30:
        num_sessions = min(8, total_days // 3)
    elif total_days <= 60:
        num_sessions = min(12, total_days // 5)
    else:
        num_sessions = min(16, total_days // 7)

    if num_sessions <= 0:
        num_sessions = 1

    tasks: List[StudyTask] = []
    
    # Calculate session dates with spaced repetition (more frequent near exam)
    session_dates = _calculate_session_dates(start, end, num_sessions, exam_date)
    
    # Generate tasks with meaningful content and specific material references
    for i, session_date in enumerate(session_dates):
        progress = (i + 1) / len(session_dates)
        is_near_exam = exam_date and (exam_date - session_date).days <= 7
        
        # Get content chunk for this session if available
        content_chunk = content_chunks[i] if content_chunks and i < len(content_chunks) else None
        
        # Determine session type and content
        if i == 0:
            # First session: Overview and introduction
            title = "Course Overview & Initial Review"
            description = _generate_intro_description(course, unique_topics, content_chunk)
        elif is_near_exam and progress > 0.7:
            # Exam prep sessions
            title, description = _generate_exam_prep_session(unique_topics, key_terms, i, len(session_dates), content_chunk)
        elif content_chunk:
            # Content-based session with specific pages/sections
            title = content_chunk.get("title", f"Study Session {i + 1}")
            description = _generate_content_based_description(content_chunk, progress)
        elif i < len(unique_topics):
            # Topic-focused sessions
            topic = unique_topics[i % len(unique_topics)]
            title = f"Study: {topic[:50]}"
            description = _generate_topic_description(topic, progress, key_terms)
        else:
            # Review sessions
            title = f"Review Session {i + 1}"
            topics_to_review = unique_topics[:min(3, len(unique_topics))]
            description = _generate_review_description(topics_to_review, progress)

        task = {
            "course_id": course_id,
            "date": session_date.isoformat(),
            "title": title,
            "description": description,
            "completed": False,
        }
        tasks.append(task)

    return tasks


def _calculate_session_dates(start: date, end: date, num_sessions: int, exam_date: date = None) -> List[date]:
    """
    Calculate session dates using spaced repetition:
    - More frequent sessions as exam approaches
    - Avoid weekends for early sessions (optional, can be removed)
    """
    total_days = (end - start).days + 1
    if total_days <= 1:
        return [start]

    dates = []
    
    if exam_date and num_sessions > 4:
        # Two-phase approach: regular spacing early, intensive near exam
        exam_prep_days = min(14, (end - exam_date).days) if exam_date else 0
        early_sessions = max(1, num_sessions // 2)
        prep_sessions = num_sessions - early_sessions
        
        # Early sessions: evenly spaced
        early_start = start
        early_end = max(start, exam_date - timedelta(days=exam_prep_days + 1))
        early_days = (early_end - early_start).days + 1
        if early_days > 0:
            early_step = max(1, early_days // max(1, early_sessions))
            for i in range(early_sessions):
                day_offset = i * early_step
                session_date = early_start + timedelta(days=day_offset)
                if session_date <= early_end:
                    dates.append(session_date)
        
        # Exam prep sessions: more frequent
        prep_start = max(dates[-1] + timedelta(days=3), exam_date - timedelta(days=exam_prep_days)) if dates else exam_date - timedelta(days=exam_prep_days)
        prep_end = exam_date - timedelta(days=1)  # Don't schedule on exam day
        prep_days = (prep_end - prep_start).days + 1
        if prep_days > 0:
            prep_step = max(1, prep_days // max(1, prep_sessions))
            for i in range(prep_sessions):
                day_offset = i * prep_step
                session_date = prep_start + timedelta(days=day_offset)
                if session_date < exam_date and session_date not in dates:
                    dates.append(session_date)
    else:
        # Simple spacing: exponential curve (more frequent near end)
        for i in range(num_sessions):
            # Use exponential spacing: sessions get closer together as we approach end
            progress = (i + 1) / num_sessions
            # Early sessions spaced more, later sessions closer together
            day_position = int(total_days * (progress ** 1.5))
            session_date = start + timedelta(days=min(day_position, total_days - 1))
            if session_date not in dates:
                dates.append(session_date)

    # Sort and ensure no duplicates
    dates = sorted(set(dates))
    
    # If we have too few dates, fill gaps
    if len(dates) < num_sessions:
        extra_needed = num_sessions - len(dates)
        # Add evenly spaced dates in gaps
        for i in range(1, len(dates)):
            if extra_needed <= 0:
                break
            gap = (dates[i] - dates[i-1]).days
            if gap > 2:
                mid_date = dates[i-1] + timedelta(days=gap // 2)
                dates.append(mid_date)
                extra_needed -= 1
        dates = sorted(set(dates))

    return dates[:num_sessions]


def _generate_intro_description(course: Dict, topics: List[str], content_chunk: Optional[Dict] = None) -> str:
    """Generate description for introductory session."""
    parts = []
    
    if content_chunk and content_chunk.get("sections"):
        # First section of material
        first_section = content_chunk["sections"][0]
        pages = first_section.get("pageNumbers", [])
        if pages:
            page_range = f"pages {min(pages)}-{max(pages)}" if len(pages) > 1 else f"page {pages[0]}"
            material_title = first_section.get("materialTitle", "course materials")
            parts.append(f"Read {page_range} of {material_title}")
            section_title = first_section.get("title", "")
            if section_title:
                parts.append(f"Focus on: {section_title}")
    
    if topics:
        topics_preview = ", ".join(topics[:3])
        parts.append(f"Familiarize yourself with key topics: {topics_preview}")
    
    if not parts:
        parts.append(f"Review course syllabus and materials for {course['name']}")
    
    parts.append("Set up study schedule and create initial notes structure")
    
    return " • ".join(parts)


def _generate_topic_description(topic: str, progress: float, key_terms: List[str]) -> str:
    """Generate description for topic-focused session."""
    activities = []
    
    # Add study activities based on progress
    activities.append(f"Study and take notes on: {topic}")
    
    if progress > 0.3:
        activities.append("Review previous topics")
    
    if progress > 0.5 and key_terms:
        sample_terms = ", ".join(key_terms[:3])
        activities.append(f"Practice concepts: {sample_terms}")
    
    if progress > 0.7:
        activities.append("Complete practice problems or exercises")
    
    return " • ".join(activities)


def _generate_review_description(topics: List[str], progress: float) -> str:
    """Generate description for review session."""
    if topics:
        topics_str = ", ".join(topics)
        activities = [f"Review: {topics_str}"]
    else:
        activities = ["Review course materials"]
    
    if progress > 0.6:
        activities.append("Practice problems")
        activities.append("Self-test on key concepts")
    
    if progress > 0.8:
        activities.append("Focus on areas needing improvement")
    
    return " • ".join(activities)


def _generate_content_based_description(content_chunk: Dict, progress: float) -> str:
    """Generate description for session with specific content assignment."""
    parts = []
    
    sections = content_chunk.get("sections", [])
    pages = content_chunk.get("pages", [])
    
    if sections:
        # List the sections/topics to cover
        section_titles = [s.get("title", "Content") for s in sections[:3]]
        if len(sections) > 3:
            section_titles.append(f"+ {len(sections) - 3} more")
        
        parts.append(f"Study: {', '.join(section_titles)}")
        
        # Include page numbers
        if pages:
            page_range_str = _format_page_range(pages)
            material_title = sections[0].get("materialTitle", "course materials")
            parts.append(f"Pages {page_range_str} of {material_title}")
    elif pages:
        # Just page numbers if no sections
        page_range_str = _format_page_range(pages)
        parts.append(f"Review pages {page_range_str}")
    
    # Add study activities based on progress
    if progress > 0.3:
        parts.append("Take notes on key concepts")
    
    if progress > 0.5:
        parts.append("Complete practice problems")
    
    if progress > 0.7:
        parts.append("Self-test understanding")
    
    return " • ".join(parts) if parts else "Study course materials"


def _format_page_range(pages: List[int]) -> str:
    """Format list of page numbers into readable range string."""
    if not pages:
        return ""
    
    pages_sorted = sorted(set(pages))
    if len(pages_sorted) == 1:
        return str(pages_sorted[0])
    elif len(pages_sorted) <= 3:
        return ", ".join(str(p) for p in pages_sorted)
    else:
        return f"{min(pages_sorted)}-{max(pages_sorted)}"


def _generate_exam_prep_session(topics: List[str], key_terms: List[str], session_num: int, total_sessions: int, content_chunk: Optional[Dict] = None) -> tuple:
    """Generate exam preparation session."""
    parts = []
    
    if content_chunk and content_chunk.get("sections"):
        # Include specific content to review
        sections = content_chunk.get("sections", [])
        pages = content_chunk.get("pages", [])
        
        if sections:
            section_titles = [s.get("title", "Content") for s in sections[:2]]
            parts.append(f"Review: {', '.join(section_titles)}")
        
        if pages:
            page_range_str = _format_page_range(pages)
            parts.append(f"Pages {page_range_str}")
    
    if session_num == total_sessions - 2:
        # Second to last session
        title = "Final Review & Practice"
        if not parts:
            if topics:
                topics_str = ", ".join(topics[:5])
                parts.append(f"Comprehensive review of all topics: {topics_str}")
            else:
                parts.append("Comprehensive review of all course materials")
        parts.extend(["Practice problems", "Review notes", "Identify weak areas"])
    elif session_num == total_sessions - 1:
        # Last session
        title = "Final Exam Preparation"
        if not parts:
            parts.append("Review key concepts, formulas, and definitions")
        parts.extend(["Organize notes for quick reference", "Get adequate rest before the exam"])
    else:
        # Other exam prep sessions
        title = "Exam Prep Session"
        if not parts:
            if topics:
                focus_topic = topics[session_num % len(topics)]
                parts.append(f"Focus on: {focus_topic}")
            else:
                parts.append("Review course materials")
        parts.extend(["Practice problems", "Self-test", "Identify questions to clarify"])
    
    description = " • ".join(parts) if parts else "Review and practice for exam"
    return title, description