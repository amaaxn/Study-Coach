📘 Study Coach — AI-Powered Personalized Study Planner

Study Coach is a full-stack web application that helps students organize courses, parse syllabi, and generate personalized study plans using AI.
It is built with:

React + Vite (frontend)

Flask + SQLAlchemy (backend)

Python PDF parsing + LLM integration (coming next)

This project is in active development.

🚀 Features (Current)
Frontend

Modern dashboard interface built with React + Vite

Course manager (add, view, and store courses)

Beautiful dark UI with responsive grid layout

Backend

Flask REST API with CORS enabled

SQLite database using SQLAlchemy

Endpoints for creating and retrieving courses

Clean project structure: routes, models, services

🔮 Roadmap
Coming Soon

PDF upload and syllabus parsing

Automatic topic extraction

Smart study plan generator (LLM-powered)

Daily tasks and “Today’s Plan” view

User accounts and authentication

Future Ideas

Progress tracking

Study streaks and reminders

Integration with Google Calendar

Practice question generator for each topic

🧩 Project Structure
study-coach/
  backend/
    app.py
    models.py
    routes/
    services/
    requirements.txt
  frontend/
    src/
      App.tsx
      api/
      components/
    vite.config.ts
    package.json
  README.md

🛠️ Local Development
1. Backend (Flask)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py


Runs at:

http://localhost:5000


Test health endpoint:

http://localhost:5000/api/health

2. Frontend (React + Vite)
cd frontend
npm install
npm run dev


Runs at:

http://localhost:5173

🤝 Contributing

This project is currently maintained personally.
Issue reports, feedback, and suggestions are welcome as the feature set grows.