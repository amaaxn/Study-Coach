import os
from typing import List, Dict, Optional
from openai import OpenAI
import tiktoken
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = None

def get_openai_client():
    """Get OpenAI client, initializing if needed."""
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        client = OpenAI(api_key=api_key)
    return client


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text for a given model."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4


def truncate_to_token_limit(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """Truncate text to fit within token limit."""
    tokens = count_tokens(text, model)
    if tokens <= max_tokens:
        return text
    
    # Estimate characters per token
    ratio = len(text) / tokens
    max_chars = int(max_tokens * ratio * 0.9)  # 90% safety margin
    return text[:max_chars]


def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """
    Send messages to OpenAI and get completion.
    Uses gpt-4o-mini for cost efficiency (much cheaper than gpt-4).
    For production, consider gpt-4o for better quality when needed.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (gpt-4o-mini for cost efficiency, gpt-4o for best quality)
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens in response
    
    Returns:
        Response text from the model
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        openai_client = get_openai_client()
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30.0  # 30 second timeout
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in OpenAI API call: {e}", exc_info=True)
        # Don't expose internal errors to users in production
        import os
        if os.getenv("FLASK_ENV") == "production":
            raise Exception("AI service temporarily unavailable. Please try again.")
        raise


def extract_topics_with_ai(pdf_text: str, course_name: str = "") -> List[str]:
    """
    Use AI to extract topics and chapters from PDF text.
    More accurate than regex-based extraction.
    """
    if not pdf_text or len(pdf_text.strip()) < 100:
        return []
    
    # Truncate to fit context window (leave room for prompt and response)
    truncated_text = truncate_to_token_limit(pdf_text, 12000, "gpt-4o-mini")
    
    prompt = f"""Analyze the following course material{' for ' + course_name if course_name else ''} and extract a comprehensive list of topics, chapters, and key concepts.

Extract:
1. Main topics/chapters (numbered sections, unit titles, etc.)
2. Key concepts and themes
3. Important subject areas

Return ONLY a clean list, one topic per line. Be specific and concise. Include 10-20 of the most important topics.

Course Material:
{truncated_text}

Topics:"""

    try:
        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing academic course materials and extracting structured topics and concepts. Always return a clean, numbered list of topics."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = chat_completion(messages, model="gpt-4o-mini", temperature=0.3, max_tokens=1000)
        
        # Parse response into list
        topics = []
        for line in response.strip().split('\n'):
            line = line.strip()
            # Remove numbering (1., 2., - , •, etc.)
            line = line.lstrip('0123456789.-•)\t ').strip()
            if line and len(line) > 5 and len(line) < 100:
                topics.append(line)
        
        return topics[:20]  # Limit to 20 topics
    except Exception as e:
        print(f"Error extracting topics with AI: {e}")
        return []


def generate_study_plan_with_ai(
    course_info: Dict,
    topics: List[str],
    sections: List[Dict],
    num_sessions: int
) -> List[Dict]:
    """
    Use AI to generate a detailed, personalized study plan.
    
    Returns list of session dicts with title and description.
    """
    course_name = course_info.get("name", "this course")
    term_start = course_info.get("term_start", "")
    term_end = course_info.get("term_end", "")
    exam_date = course_info.get("main_exam_date", "")
    
    # Build context
    context_parts = []
    if topics:
        context_parts.append(f"Key topics: {', '.join(topics[:15])}")
    if sections:
        section_info = "\n".join([f"- {s.get('title', 'Section')}: pages {s.get('startPage', '?')}-{s.get('endPage', '?')}" 
                                  for s in sections[:10]])
        context_parts.append(f"Course sections:\n{section_info}")
    
    context = "\n".join(context_parts) if context_parts else "No specific course content available."
    
    prompt = f"""Create a detailed study plan for {course_name}.

Course Details:
- Term: {term_start} to {term_end}
- Exam Date: {exam_date if exam_date else 'Not specified'}
- Number of study sessions: {num_sessions}

Course Content:
{context}

Generate {num_sessions} study sessions with:
1. A clear, specific title (what to study)
2. A detailed description (how to study, what activities, what pages to review if available)

Distribute sessions using spaced repetition (more frequent near exam). Make sessions practical and actionable.
Include a mix of: reading, note-taking, practice problems, review, and exam prep.

Return ONLY a JSON array of objects, each with "title" and "description" fields. No other text.

Format:
[
  {{"title": "Session title", "description": "Detailed study activities and instructions"}},
  ...
]"""

    try:
        messages = [
            {
                "role": "system",
                "content": "You are an expert academic tutor that creates highly effective, personalized study plans. Always return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = chat_completion(messages, model="gpt-4o-mini", temperature=0.7, max_tokens=2000)
        
        # Parse JSON response
        import json
        # Try to extract JSON from response (in case there's extra text)
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        response = response.strip()
        
        sessions = json.loads(response)
        if isinstance(sessions, list):
            return sessions[:num_sessions]
        return []
    except Exception as e:
        print(f"Error generating study plan with AI: {e}")
        return []


def chatbot_response(
    user_message: str,
    user_context: Dict,
    conversation_history: List[Dict[str, str]] = None
) -> str:
    """
    Generate chatbot response using AI.
    
    Args:
        user_message: User's message
        user_context: Dict with user's courses, study plans, etc.
        conversation_history: Previous messages in conversation
    
    Returns:
        AI response text
    """
    conversation_history = conversation_history or []
    
    # Build system prompt with context
    courses_info = ""
    if user_context.get("courses"):
        courses_list = "\n".join([f"- {c.get('name', 'Course')}" for c in user_context["courses"][:5]])
        courses_info = f"\n\nUser's courses:\n{courses_list}"
    
    system_prompt = f"""You are Learnium, an intelligent AI study coach and academic assistant. You help students:
- Create effective study plans
- Understand course materials
- Break down complex topics
- Suggest study strategies
- Answer questions about their courses
- Provide motivation and study tips

Be helpful, encouraging, and practical. Keep responses concise but informative. If asked about study plans, reference their courses and provide specific, actionable advice.{courses_info}"""

    # Build messages
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (limit to last 10 messages to avoid token limits)
    for msg in conversation_history[-10:]:
        messages.append(msg)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = chat_completion(
            messages,
            model="gpt-4o-mini",
            temperature=0.8,
            max_tokens=500
        )
        return response
    except Exception as e:
        print(f"Error in chatbot: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again."


def analyze_syllabus_for_schedule(pdf_text: str) -> Dict:
    """
    Use AI to analyze syllabus and extract schedule, assignments, deadlines.
    """
    if not pdf_text or len(pdf_text.strip()) < 100:
        return {}
    
    truncated_text = truncate_to_token_limit(pdf_text, 12000, "gpt-4o-mini")
    
    prompt = f"""Analyze this course syllabus and extract key scheduling information.

Extract:
1. Important dates (exams, project due dates, etc.)
2. Assignment schedule
3. Weekly topics/readings
4. Grading breakdown

Return as JSON with keys: important_dates (list), assignments (list), weekly_topics (list), grading_info (text).

Syllabus:
{truncated_text}"""

    try:
        messages = [
            {
                "role": "system",
                "content": "You are an expert at extracting structured information from course syllabi. Always return valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = chat_completion(messages, model="gpt-4o-mini", temperature=0.3, max_tokens=1500)
        
        # Parse JSON
        import json
        response = response.strip()
        if '```json' in response:
            response = response.split('```json')[1].split('```')[0].strip()
        elif '```' in response:
            response = response.split('```')[1].split('```')[0].strip()
        
        return json.loads(response)
    except Exception as e:
        print(f"Error analyzing syllabus: {e}")
        return {}
