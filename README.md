# 📘 Study Coach  
### AI-Powered Personalized Study Planner

Study Coach is a full-stack web application that helps students organize courses, parse syllabi, and automatically generate personalized study plans using AI.

Built with:

- React + Vite (frontend)  
- Flask + MongoDB (backend)  
- JWT Authentication
- PDF parsing + LLM integration (coming soon)

---

## 🔧 Tech Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | React, Vite, TypeScript, Axios |
| Backend | Python, Flask, Flask-JWT-Extended, PyMongo |
| Database | MongoDB |
| Authentication | JWT tokens |
| AI | LLM-powered study plan generation (upcoming) |

---

## ✨ Features

### ✅ Current
- User authentication (sign up, login, logout)
- Modern dashboard UI  
- Dark theme with responsive layout  
- Add, view, and delete courses  
- Upload and manage PDF materials
- Intelligent study plan generation based on course content
- Content-based study sessions with specific page references
- REST API with MongoDB storage
- Clean backend architecture (routes, models, services)

### 🔮 In Development
- PDF upload and syllabus parsing  
- Topic extraction from documents  
- AI-generated study plan  
- Daily task breakdown  
- "Today's Plan" suggestions  

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
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URI and JWT secret
   ```

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
```

For production, use:
- MongoDB Atlas connection string for `MONGO_URI`
- Strong random string for `JWT_SECRET_KEY`

---

## 🎯 Usage

1. **Sign Up**: Create a new account at `/register`
2. **Login**: Sign in at `/login`
3. **Add Course**: Enter course details (name, term dates, exam date)
4. **Upload Materials**: Upload PDF syllabi or course materials
5. **Generate Plan**: Click "Generate plan" to create personalized study sessions
6. **Study**: Follow the generated plan with specific content assignments

---

## 🤝 Contributing

This project is in active development. Suggestions and feature ideas are welcome.

---

## 📄 License

License will be added once project direction is finalized.
