# 📘 Learnium  
### AI-Powered Personalized Study Planner

Learnium is a full-stack web application that helps students organize courses, parse syllabi, and automatically generate personalized study plans using AI. This intelligent study coach adapts to your learning style and creates optimized study schedules tailored to your academic needs.

Built with:

- React + Vite (frontend)  
- Flask + MongoDB (backend)  
- JWT Authentication
- OpenAI GPT-4o-mini for AI-powered features
- PDF parsing with AI topic extraction

---

## 🔧 Tech Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | React, Vite, TypeScript, Axios |
| Backend | Python, Flask, Flask-JWT-Extended, PyMongo |
| Database | MongoDB |
| Authentication | JWT tokens |
| AI | OpenAI GPT-4o-mini for chatbot and intelligent study planning |

---

## ✨ Features

### ✅ Current
- User authentication (sign up, login, logout)
- Modern dashboard UI  
- Dark theme with responsive layout  
- Add, view, and delete courses  
- Upload and manage PDF materials
- AI-powered intelligent study plan generation using OpenAI
- AI chatbot for interactive study assistance and planning
- PDF upload and syllabus parsing with AI topic extraction
- Content-based study sessions with specific page references
- Today's Plan feature showing daily study tasks
- Daily task breakdown across all courses
- Upcoming tasks preview (next 3 days)
- REST API with MongoDB storage
- Clean backend architecture (routes, models, services)  

### 🚀 Future Enhancements
- Google Calendar sync  
- Progress analytics  
- AI practice question generator  

---

## 🗂 Project Structure
study-coach/
│
├── backend/
│ ├── app.py
│ ├── models.py
│ ├── middleware.py
│ ├── routes/
│ │ ├── auth.py
│ │ ├── courses.py
│ │ ├── materials.py
│ │ └── plans.py
│ ├── services/
│ │ ├── pdf_analyzer.py
│ │ ├── planner.py
│ │ └── topic_extractor.py
│ └── requirements.txt
│
└── frontend/
├── src/
│ ├── App.tsx
│ ├── api/
│ │ └── client.ts
│ ├── pages/
│ │ ├── Login.tsx
│ │ └── Register.tsx
│ └── components/
├── package.json
└── vite.config.ts


---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud instance)

### Backend Setup

1. Install MongoDB:
   ```bash
   # macOS (using Homebrew)
   brew install mongodb-community
   brew services start mongodb-community
   
   # Or use MongoDB Atlas (cloud)
   ```

2. Set up Python environment:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r ../requirements.txt
   ```
   
   **Note:** Make sure you're in the project root when installing requirements.

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URI, JWT secret, and OpenAI API key
   ```
   
   **Important:** Get your OpenAI API key from https://platform.openai.com/api-keys
   Add it to `.env` as `OPENAI_API_KEY=sk-your-key-here`

4. Run the backend:
   ```bash
   python3 app.py
   ```
   Backend runs on `http://localhost:5001`

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the frontend:
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

---

## 🔐 Environment Variables

Create a `.env` file in the backend directory:

```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=study_coach
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
OPENAI_API_KEY=sk-your-openai-api-key-here
```

For production, use:
- MongoDB Atlas connection string for `MONGO_URI`
- Strong random string for `JWT_SECRET_KEY`
- OpenAI API key from your OpenAI account

---

## 🎯 Usage

1. **Sign Up**: Create a new account at `/register`
2. **Login**: Sign in at `/login`
3. **Add Course**: Enter course details (name, term dates, exam date)
4. **Upload Materials**: Upload PDF syllabi or course materials (AI will extract topics automatically)
5. **Generate Plan**: Click "Generate plan" to create AI-powered personalized study sessions
6. **Chat with AI**: Click "AI Coach" button to get help with study planning, strategies, and questions
7. **Today's Plan**: View your daily study tasks in the right panel
8. **Study**: Follow the AI-generated plan with specific content assignments and activities

---

## 🤝 Contributing

This project is in active development. Suggestions and feature ideas are welcome.

---

## 📄 License

License will be added once project direction is finalized.
