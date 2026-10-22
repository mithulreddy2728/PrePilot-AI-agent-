"""Google Gemini AI integration service for all AI-powered features."""

import json
import logging
from ..config import settings

logger = logging.getLogger(__name__)

# Try to import and configure Gemini
_model = None
try:
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Gemini AI model initialized successfully")
    else:
        logger.warning("GEMINI_API_KEY not configured — using mock AI responses")
except Exception as e:
    logger.warning(f"Failed to initialize Gemini: {e} — using mock AI responses")


async def _generate(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    if _model is None:
        return _mock_response(prompt)
    try:
        response = _model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return _mock_response(prompt)


def _mock_response(prompt: str) -> str:
    """Return a useful mock response when Gemini is not configured."""
    prompt_lower = prompt.lower()
    if "resume" in prompt_lower and "analyze" in prompt_lower:
        return json.dumps({
            "ats_score": 72,
            "rating": 3.5,
            "skills": ["Python", "JavaScript", "SQL", "React", "Node.js", "Git"],
            "missing_skills": ["Docker", "Kubernetes", "AWS", "System Design"],
            "suggestions": [
                "Add quantifiable achievements to each work experience",
                "Include relevant certifications (AWS, Docker)",
                "Add a dedicated 'Projects' section with GitHub links",
                "Use stronger action verbs like 'architected', 'optimized', 'spearheaded'",
                "Include a brief professional summary at the top"
            ],
            "summary": "The resume demonstrates solid foundational skills in web development. To improve ATS compatibility, add more industry-specific keywords, quantify achievements, and ensure consistent formatting throughout."
        })
    elif "interview" in prompt_lower:
        return json.dumps({
            "question": "Tell me about a challenging technical problem you've solved recently. Walk me through your approach, the trade-offs you considered, and the outcome.",
            "type": "behavioral",
            "hints": ["Use the STAR method", "Focus on your specific contributions", "Mention measurable impact"]
        })
    elif "evaluate" in prompt_lower or "feedback" in prompt_lower:
        return json.dumps({
            "score": 7.5,
            "feedback": "Good answer with clear structure. You demonstrated solid problem-solving skills. To improve: provide more specific technical details, quantify the impact of your solution, and mention alternative approaches you considered.",
            "strengths": ["Clear communication", "Structured response", "Relevant example"],
            "improvements": ["Add more technical depth", "Quantify results", "Discuss trade-offs"]
        })
    elif "study" in prompt_lower or "plan" in prompt_lower or "roadmap" in prompt_lower:
        return json.dumps({
            "title": "7-Day Placement Preparation Roadmap",
            "tasks": [
                {"day": 1, "title": "Data Structures Review", "description": "Arrays, Strings, Linked Lists — solve 5 problems each", "category": "dsa"},
                {"day": 2, "title": "Trees & Graphs", "description": "Binary Trees, BST, BFS/DFS — solve 5 problems", "category": "dsa"},
                {"day": 3, "title": "Dynamic Programming", "description": "Classic DP patterns: Fibonacci, Knapsack, LCS — solve 5 problems", "category": "dsa"},
                {"day": 4, "title": "System Design Basics", "description": "Load balancers, caching, databases, microservices", "category": "interview"},
                {"day": 5, "title": "Aptitude & Reasoning", "description": "Quantitative aptitude, logical reasoning, verbal ability practice", "category": "aptitude"},
                {"day": 6, "title": "Mock Interviews", "description": "Practice 2 mock interviews — 1 technical, 1 HR", "category": "interview"},
                {"day": 7, "title": "Resume & Review", "description": "Polish resume, review weak areas, relax before placement", "category": "resume"}
            ]
        })
    else:
        return "I'm your AI placement mentor! I can help you with placement preparation, resume building, interview practice, and career guidance. What would you like to work on today?"


async def analyze_resume(text: str) -> dict:
    """Analyze resume text and return ATS score, skills, suggestions."""
    prompt = f"""Analyze the following resume text and return a JSON object with these fields:
- ats_score: number 0-100 rating how well this resume would perform in ATS systems
- rating: number 1-5 overall resume quality rating
- skills: array of technical and soft skills found in the resume
- missing_skills: array of important skills that are missing for a tech placement
- suggestions: array of 5 specific, actionable improvement suggestions
- summary: a brief 2-3 sentence analysis summary

Resume text:
{text}

Return ONLY valid JSON, no markdown formatting or code blocks."""

    response = await _generate(prompt)
    try:
        # Try to parse JSON from the response
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(response)
    except json.JSONDecodeError:
        return json.loads(_mock_response("resume analyze"))


async def generate_interview_question(company: str, role: str = "Software Engineer", context: str = "") -> dict:
    """Generate an interview question for a specific company."""
    prompt = f"""You are a {company} interviewer for a {role} position.
Generate one interview question. Consider the previous conversation context: {context}

Return a JSON object:
- question: the interview question text
- type: one of "technical", "behavioral", "system_design", "hr"
- hints: array of 2-3 brief hints for the candidate

Return ONLY valid JSON."""

    response = await _generate(prompt)
    try:
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(response)
    except json.JSONDecodeError:
        return json.loads(_mock_response("interview question"))


async def evaluate_answer(question: str, answer: str, company: str) -> dict:
    """Evaluate a candidate's answer to an interview question."""
    prompt = f"""As a {company} interviewer, evaluate this candidate's answer.

Question: {question}
Answer: {answer}

Return a JSON object:
- score: number 1-10
- feedback: detailed constructive feedback (2-3 sentences)
- strengths: array of 2-3 strengths in the answer
- improvements: array of 2-3 areas for improvement

Return ONLY valid JSON."""

    response = await _generate(prompt)
    try:
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(response)
    except json.JSONDecodeError:
        return json.loads(_mock_response("evaluate feedback"))


async def generate_study_plan(preferences: str) -> dict:
    """Generate a weekly study plan based on preferences."""
    prompt = f"""Create a 7-day placement preparation study plan based on these preferences: {preferences}

Return a JSON object:
- title: plan title
- tasks: array of objects with fields: day (1-7), title, description, category (dsa/interview/aptitude/resume/project)

Return ONLY valid JSON."""

    response = await _generate(prompt)
    try:
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(response)
    except json.JSONDecodeError:
        return json.loads(_mock_response("study plan roadmap"))


async def chat_with_mentor(mode: str, messages: list, user_message: str) -> str:
    """Chat with AI mentor in a specific mode."""
    mode_descriptions = {
        "placement": "You are an expert placement preparation mentor. Help with placement strategies, company research, aptitude preparation, and general placement guidance.",
        "resume": "You are an expert resume consultant. Help improve resumes, suggest formatting, highlight achievements, and optimize for ATS systems.",
        "interview": "You are an expert interview coach. Help practice interview questions, improve answers, body language tips, and build confidence.",
        "career": "You are an expert career counselor. Help with career planning, skill development, industry trends, and long-term career goals."
    }

    system_prompt = mode_descriptions.get(mode, mode_descriptions["placement"])

    # Build conversation context
    context = f"System: {system_prompt}\n\n"
    for msg in messages[-10:]:  # Last 10 messages for context
        role = "User" if msg.get("role") == "user" else "Assistant"
        context += f"{role}: {msg.get('content', '')}\n"
    context += f"User: {user_message}\nAssistant:"

    response = await _generate(context)
    return response.strip()
