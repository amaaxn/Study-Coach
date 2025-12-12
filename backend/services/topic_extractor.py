import re
from typing import List, Dict


def extract_topics_from_material(material: Dict) -> List[str]:
    """
    Extract topics/chapters from PDF material text using heuristics.
    
    Looks for:
    - Numbered sections (e.g., "1. Introduction", "Chapter 2: Topic")
    - Headers (all caps lines, lines ending with colon)
    - Common syllabus patterns
    """
    if not material.raw_text:
        return []
    
    text = material.raw_text
    
    topics = []
    
    # Pattern 1: Numbered sections like "1. Topic", "2. Topic", etc.
    numbered_pattern = r'^\s*(?:Chapter\s+)?(\d+)[\.:]\s+([A-Z][^\n]{10,80})'
    matches = re.finditer(numbered_pattern, text, re.MULTILINE | re.IGNORECASE)
    for match in matches:
        topic = match.group(2).strip()
        # Clean up topic name
        topic = re.sub(r'\s+', ' ', topic)
        topic = topic.split('\n')[0]  # Take first line only
        if len(topic) > 10 and len(topic) < 100:
            topics.append(topic)
    
    # Pattern 2: Lines that look like headers (all caps or title case, end with colon)
    header_pattern = r'^([A-Z][A-Za-z\s]{5,60}):\s*$'
    matches = re.finditer(header_pattern, text, re.MULTILINE)
    for match in matches:
        topic = match.group(1).strip()
        # Skip common non-topic headers
        skip_words = ['SYLLABUS', 'OBJECTIVES', 'REQUIREMENTS', 'GRADING', 'SCHEDULE', 
                     'ASSIGNMENTS', 'TEXTBOOK', 'REFERENCES', 'COURSE']
        if not any(skip in topic.upper() for skip in skip_words):
            if len(topic) > 5 and len(topic) < 80:
                topics.append(topic)
    
    # Pattern 3: Common syllabus topic patterns
    syllabus_patterns = [
        r'(?:Week|Unit|Module)\s+\d+[:\-]\s*([A-Z][^\n]{10,60})',
        r'Topic\s+\d+[:\-]\s*([A-Z][^\n]{10,60})',
    ]
    for pattern in syllabus_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            topic = match.group(1).strip()
            topic = re.sub(r'\s+', ' ', topic)
            if len(topic) > 10 and len(topic) < 100:
                topics.append(topic)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_topics = []
    for topic in topics:
        topic_lower = topic.lower()
        if topic_lower not in seen:
            seen.add(topic_lower)
            unique_topics.append(topic)
    
    # If we found many topics, take the most distinct ones
    if len(unique_topics) > 15:
        # Keep first few and sample the rest
        unique_topics = unique_topics[:5] + unique_topics[5::len(unique_topics)//10][:10]
    
    return unique_topics


def extract_key_terms(material: Dict) -> List[str]:
    """
    Extract key terms/concepts from material text.
    Looks for capitalized terms, technical terms, etc.
    """
    if not material.get("raw_text"):
        return []
    
    text = material["raw_text"][:5000]  # Limit to first 5k chars for performance
    
    # Find capitalized terms that might be concepts
    # Pattern: sequences of capitalized words (2-4 words)
    term_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
    matches = re.finditer(term_pattern, text)
    
    terms = []
    for match in matches:
        term = match.group(1).strip()
        # Skip if it's a common phrase
        skip = ['Course', 'Students', 'Instructor', 'Required', 'Optional', 
                'Assignment', 'Project', 'Exam', 'Final', 'Midterm']
        if not any(skip_word in term for skip_word in skip):
            if len(term) > 5 and len(term) < 40:
                terms.append(term)
    
    # Remove duplicates
    seen = set()
    unique_terms = []
    for term in terms:
        term_lower = term.lower()
        if term_lower not in seen:
            seen.add(term_lower)
            unique_terms.append(term)
    
    return unique_terms[:20]  # Limit to 20 terms
