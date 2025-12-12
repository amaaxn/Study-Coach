import json
import re
from typing import List, Dict, Tuple
from pypdf import PdfReader


class PDFSection:
    """Represents a section of content from a PDF."""
    def __init__(self, title: str, start_page: int, end_page: int, content: str, page_numbers: List[int]):
        self.title = title
        self.start_page = start_page
        self.end_page = end_page
        self.content = content
        self.page_numbers = page_numbers
    
    def to_dict(self):
        return {
            "title": self.title,
            "startPage": self.start_page,
            "endPage": self.end_page,
            "pageNumbers": self.page_numbers,
            "contentPreview": self.content[:200] if self.content else ""
        }


def analyze_pdf_structure(file_path: str) -> Dict:
    """
    Analyze PDF and extract structured content:
    - Page-by-page breakdown
    - Sections/chapters with page ranges
    - Topics and key concepts per section
    """
    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        
        # Extract text page by page
        pages_content = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages_content.append({
                "page": page_num,
                "text": text,
                "wordCount": len(text.split())
            })
        
        # Extract sections from the PDF
        sections = extract_sections(pages_content)
        
        # If no sections found, create page-based chunks
        if not sections:
            sections = create_page_based_chunks(pages_content)
        
        # Extract topics from each section
        for section in sections:
            section["topics"] = extract_topics_from_text(section.get("content", ""))
            section["keyTerms"] = extract_key_terms_from_text(section.get("content", ""))
        
        return {
            "totalPages": total_pages,
            "totalWords": sum(p["wordCount"] for p in pages_content),
            "sections": sections,
            "pagesContent": [{"page": p["page"], "wordCount": p["wordCount"]} for p in pages_content]
        }
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return {
            "totalPages": 0,
            "totalWords": 0,
            "sections": [],
            "pagesContent": []
        }


def extract_sections(pages_content: List[Dict]) -> List[Dict]:
    """
    Extract sections/chapters from PDF pages.
    Looks for:
    - Numbered chapters/sections (1. Title, Chapter 2, etc.)
    - Headers (all caps, bold-like patterns)
    - Page breaks that indicate new sections
    """
    sections = []
    current_section = None
    current_content = []
    current_pages = []
    
    for page_data in pages_content:
        page_num = page_data["page"]
        text = page_data["text"]
        lines = text.split('\n')
        
        # Look for section headers in first few lines of page
        header = None
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # Pattern 1: Numbered sections "1. Title", "Chapter 2: Title"
            numbered_match = re.match(r'^\s*(?:Chapter|CHAPTER|Section|SECTION|Part|PART)?\s*(\d+)[\.:]\s+([A-Z][^\n]{5,80})', line_clean, re.IGNORECASE)
            if numbered_match:
                header = numbered_match.group(2).strip()
                break
            
            # Pattern 2: All caps headers (likely section titles)
            if line_clean.isupper() and len(line_clean) > 5 and len(line_clean) < 60:
                # Check if it's not a common non-section word
                skip_words = ['TABLE OF CONTENTS', 'PAGE', 'CHAPTER', 'APPENDIX', 'BIBLIOGRAPHY', 'REFERENCES']
                if not any(skip in line_clean for skip in skip_words):
                    header = line_clean.title()
                    break
            
            # Pattern 3: Title case headers ending with colon
            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,5}:\s*$', line_clean):
                header = line_clean.rstrip(':').strip()
                break
        
        # If we found a header, save previous section and start new one
        if header and current_section:
            sections.append({
                "title": current_section,
                "startPage": current_pages[0] if current_pages else page_num,
                "endPage": current_pages[-1] if current_pages else page_num,
                "pageNumbers": current_pages.copy(),
                "content": "\n".join(current_content)
            })
            current_section = header
            current_content = [text]
            current_pages = [page_num]
        elif header:
            # First section
            current_section = header
            current_content = [text]
            current_pages = [page_num]
        else:
            # Continue current section
            current_content.append(text)
            if page_num not in current_pages:
                current_pages.append(page_num)
    
    # Add final section
    if current_section:
        sections.append({
            "title": current_section,
            "startPage": current_pages[0] if current_pages else 1,
            "endPage": current_pages[-1] if current_pages else pages_content[-1]["page"],
            "pageNumbers": current_pages.copy(),
            "content": "\n".join(current_content)
        })
    
    return sections


def create_page_based_chunks(pages_content: List[Dict], chunk_size: int = 5) -> List[Dict]:
    """
    If no sections found, create chunks based on page ranges.
    """
    chunks = []
    for i in range(0, len(pages_content), chunk_size):
        chunk_pages = pages_content[i:i+chunk_size]
        page_nums = [p["page"] for p in chunk_pages]
        content = "\n".join(p["text"] for p in chunk_pages)
        
        # Try to extract a title from first page
        first_page_text = chunk_pages[0]["text"]
        title = extract_title_from_page(first_page_text) or f"Pages {min(page_nums)}-{max(page_nums)}"
        
        chunks.append({
            "title": title,
            "startPage": min(page_nums),
            "endPage": max(page_nums),
            "pageNumbers": page_nums,
            "content": content
        })
    
    return chunks


def extract_title_from_page(text: str) -> str:
    """Extract a potential title from the first few lines of a page."""
    lines = text.split('\n')[:5]
    for line in lines:
        line_clean = line.strip()
        if len(line_clean) > 10 and len(line_clean) < 80:
            # Check if it looks like a title (not all caps, has proper case)
            if line_clean[0].isupper() and not line_clean.isupper():
                return line_clean
    return None


def extract_topics_from_text(text: str, max_topics: int = 10) -> List[str]:
    """Extract topics/concepts from text."""
    topics = []
    
    # Pattern 1: Numbered items like "1. Topic", "2. Concept"
    numbered = re.findall(r'^\s*\d+[\.\)]\s+([A-Z][^\n]{5,60})', text, re.MULTILINE)
    topics.extend(numbered[:max_topics])
    
    # Pattern 2: Bold-like patterns (if text formatting is preserved)
    # Pattern 3: Capitalized phrases that appear important
    capitalized = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b', text)
    # Filter out common words
    skip_words = ['The', 'This', 'That', 'There', 'These', 'Those', 'Chapter', 'Section', 'Page']
    capitalized = [c for c in capitalized if c.split()[0] not in skip_words]
    topics.extend(capitalized[:max_topics])
    
    # Remove duplicates
    seen = set()
    unique_topics = []
    for topic in topics:
        topic_lower = topic.lower()
        if topic_lower not in seen and len(topic) > 5:
            seen.add(topic_lower)
            unique_topics.append(topic)
    
    return unique_topics[:max_topics]


def extract_key_terms_from_text(text: str, max_terms: int = 15) -> List[str]:
    """Extract key technical terms from text."""
    # Look for terms that might be defined or emphasized
    # Pattern: "Term" or Term (possibly italicized or capitalized)
    
    # Find capitalized terms (technical terms often start with capitals)
    terms = re.findall(r'\b([A-Z][A-Za-z]{3,20}(?:\s+[A-Z][A-Za-z]{2,15}){0,2})\b', text)
    
    # Filter common words
    common_words = {'The', 'This', 'That', 'There', 'These', 'Those', 'When', 'Where', 
                   'What', 'Which', 'Who', 'Why', 'How', 'Chapter', 'Section', 'Page'}
    terms = [t for t in terms if not any(cw in t.split() for cw in common_words)]
    
    # Remove duplicates
    seen = set()
    unique_terms = []
    for term in terms:
        term_lower = term.lower()
        if term_lower not in seen:
            seen.add(term_lower)
            unique_terms.append(term)
    
    return unique_terms[:max_terms]


def split_content_for_study(sections: List[Dict], num_sessions: int) -> List[Dict]:
    """
    Split material content into chunks for study sessions.
    Distributes sections across sessions, considering:
    - Section size (word count)
    - Logical grouping
    - Balanced workload per session
    """
    if not sections:
        return []
    
    # Calculate total content size
    total_size = sum(len(s.get("content", "").split()) for s in sections)
    target_size_per_session = total_size / num_sessions if num_sessions > 0 else total_size
    
    study_chunks = []
    current_chunk = {
        "sections": [],
        "pages": [],
        "totalWords": 0,
        "title": ""
    }
    
    for section in sections:
        section_size = len(section.get("content", "").split())
        
        # If adding this section would exceed target, finalize current chunk
        if (current_chunk["totalWords"] + section_size > target_size_per_session * 1.5 and 
            current_chunk["sections"] and len(study_chunks) < num_sessions - 1):
            # Create title for chunk
            if len(current_chunk["sections"]) == 1:
                current_chunk["title"] = current_chunk["sections"][0].get("title", "Study Content")
            else:
                current_chunk["title"] = f"{current_chunk['sections'][0].get('title', 'Content')} & More"
            
            study_chunks.append(current_chunk)
            current_chunk = {
                "sections": [],
                "pages": [],
                "totalWords": 0,
                "title": ""
            }
        
        # Add section to current chunk
        current_chunk["sections"].append(section)
        current_chunk["pages"].extend(section.get("pageNumbers", []))
        current_chunk["totalWords"] += section_size
        current_chunk["pages"] = sorted(set(current_chunk["pages"]))
    
    # Add final chunk
    if current_chunk["sections"]:
        if len(current_chunk["sections"]) == 1:
            current_chunk["title"] = current_chunk["sections"][0].get("title", "Study Content")
        else:
            current_chunk["title"] = f"{current_chunk['sections'][0].get('title', 'Content')} & More"
        study_chunks.append(current_chunk)
    
    return study_chunks
