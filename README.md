# 🚀 PrePilot AI — AI-Powered Placement Preparation Platform

PrePilot AI is a comprehensive, production-grade placement preparation platform powered by Google Gemini AI. It equips students and job seekers with end-to-end tools to ace campus placements and tech interviews.

---

## ✨ Core Features

1. **📄 AI Resume Analyzer & ATS Scorer**
   - Upload PDF/DOCX resumes.
   - Comprehensive ATS scoring (0–100), missing technical skills identification, keyword match analysis, and actionable bullet-point recommendations.

2. **🎙️ AI Mock Interview Simulator**
   - Company-specific interviews (Google, Microsoft, Amazon, Goldman Sachs, and more).
   - Dynamic AI questioning adapting to your answers.
   - Evaluation with detailed rubric: STAR method adherence, technical depth, communication clarity, and constructive feedback.

3. **💻 Coding Arena & DSA Practice**
   - Curated placement coding challenges with test cases and difficulty tiers (Easy, Medium, Hard).
   - In-browser code runner supporting multiple languages.
   - Solutions, time/space complexity analysis, and submission tracking.

4. **📅 AI Study Planner & Roadmap**
   - Customized 7-day and 30-day placement preparation roadmaps.
   - Daily actionable tasks categorized by DSA, System Design, Aptitude, and HR questions.
   - Progress tracking and completion status.

5. **💬 AI Mentor Chat**
   - 24/7 personalized placement coach powered by Gemini.
   - Career guidance, interview strategies, salary negotiation, and resume phrasing assistance.

6. **📊 Analytics Dashboard**
   - Overall placement readiness index.
   - Activity tracking, streak counters, problem-solving analytics, and interview performance trends.

7. **🛡️ Admin & Moderation**
   - Manage coding challenges, curate companies, and monitor platform activity.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.11, SQLAlchemy 2.0, Pydantic v2
- **Database:** SQLite (default for development) / MySQL (production)
- **AI Engine:** Google Gemini AI (`google-generativeai`) with graceful mock fallbacks
- **Security:** JWT authentication (HS256), Passlib/Bcrypt password hashing, CORS
- **Frontend:** Vanilla CSS & JavaScript SPA with glassmorphic dark UI, Google Fonts (Plus Jakarta Sans & JetBrains Mono), Chart.js
- **Deployment:** Docker, Docker Compose, Railway

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Set Up Virtual Environment

```bash
cd "PrePilotAI- major"
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional: add your `GEMINI_API_KEY` for live AI responses. Mock mode is automatically enabled if left empty.)*

### 3. Run the Application

```bash
uvicorn backend.app.main:app --reload --port 8000
```

- **Frontend App:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🐳 Docker Deployment

```bash
docker compose up -d --build
```
Access the application at `http://localhost:8000`.

---

## 🔑 Default Seed Credentials

When starting with `SEED_DEMO_DATA=true`:
- **Admin Email:** `admin@preppilot.com`
- **Admin Password:** `Admin@123456`
- **Student Demo:** Register any account or test with existing users.
