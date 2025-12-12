import { useEffect, useState, type FormEvent, type ChangeEvent } from "react";
import { api } from "./api/client";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Chatbot } from "./components/Chatbot";
import { TodaysPlan } from "./components/TodaysPlan";
import "./animations.css";

interface Course {
  id: string;
  name: string;
  termStart: string;
  termEnd: string;
  mainExamDate: string | null;
}

interface StudyTask {
  id: string;
  date: string;
  title: string;
  description: string | null;
  completed: boolean;
}

interface Material {
  id: string;
  title: string;
  filePath: string | null;
}

interface User {
  id: string;
  email: string;
  name: string;
}

function App() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState<"login" | "register" | "app">("app");
  const [loggingOut, setLoggingOut] = useState(false);
  const [pageTransition, setPageTransition] = useState(false);
  const [courses, setCourses] = useState<Course[]>([]);
  const [name, setName] = useState("");
  const [termStart, setTermStart] = useState("");
  const [termEnd, setTermEnd] = useState("");
  const [mainExamDate, setMainExamDate] = useState("");
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [savingCourse, setSavingCourse] = useState(false);
  const [courseError, setCourseError] = useState<string | null>(null);

  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  const [tasks, setTasks] = useState<StudyTask[]>([]);
  const [loadingPlan, setLoadingPlan] = useState(false);

  const [materials, setMaterials] = useState<Material[]>([]);
  const [loadingMaterials, setLoadingMaterials] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [showChatbot, setShowChatbot] = useState(false);

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userStr = localStorage.getItem("user");
    
    if (token && userStr) {
      setAuthenticated(true);
      setUser(JSON.parse(userStr));
      setCurrentPage("app");
      // Verify token is still valid
      api.get("/auth/me")
        .then((res) => {
          setUser(res.data);
        })
        .catch(() => {
          // Token invalid, logout
          localStorage.removeItem("access_token");
          localStorage.removeItem("user");
          setAuthenticated(false);
          setCurrentPage("login");
        });
    } else {
      setAuthenticated(false);
      const path = window.location.pathname;
      if (path.includes("/register")) {
        setCurrentPage("register");
      } else {
        setCurrentPage("login");
      }
    }
  }, []);

  // Load courses when authenticated
  useEffect(() => {
    if (authenticated) {
      api
        .get<Course[]>("/courses")
        .then((res) => setCourses(res.data))
        .catch(() => setLoadingCourses(false))
        .finally(() => setLoadingCourses(false));
    }
  }, [authenticated]);


  const handleLogout = () => {
    setLoggingOut(true);
    
    // Animate logout
    setTimeout(() => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      setAuthenticated(false);
      setUser(null);
      setCurrentPage("login");
      setCourses([]);
      setSelectedCourseId(null);
      setTasks([]);
      setMaterials([]);
      setLoggingOut(false);
    }, 500);
  };

  const handleLogin = () => {
    setPageTransition(true);
    const userStr = localStorage.getItem("user");
    if (userStr) {
      setUser(JSON.parse(userStr));
      setAuthenticated(true);
      setTimeout(() => {
        setCurrentPage("app");
        setPageTransition(false);
      }, 300);
    }
  };

  const handleRegister = () => {
    setPageTransition(true);
    const userStr = localStorage.getItem("user");
    if (userStr) {
      setUser(JSON.parse(userStr));
      setAuthenticated(true);
      setTimeout(() => {
        setCurrentPage("app");
        setPageTransition(false);
      }, 300);
    }
  };

  // Show logout overlay
  if (loggingOut) {
    return (
      <div className="logout-overlay">
        <div className="logout-content" style={{ textAlign: "center", color: "#fff" }}>
          <div className="loading-spinner" style={{ width: "48px", height: "48px", borderWidth: "4px", margin: "0 auto 1rem" }}></div>
          <p style={{ fontSize: "18px", fontFamily: "var(--font-body)", fontWeight: 600, letterSpacing: "-0.01em" }}>Signing you out...</p>
        </div>
      </div>
    );
  }

  // Show loading while checking auth
  if (authenticated === null) {
    return (
      <div className="gradient-animated" style={{ 
        minHeight: "100vh", 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center",
        color: "#fff"
      }}>
        <div style={{ textAlign: "center" }}>
          <div className="loading-spinner" style={{ width: "48px", height: "48px", borderWidth: "4px", margin: "0 auto 1rem" }}></div>
          <p style={{ fontSize: "18px", fontFamily: "var(--font-body)", fontWeight: 600, letterSpacing: "-0.01em" }}>Loading...</p>
        </div>
      </div>
    );
  }

  // Show login page
  if (currentPage === "login") {
    return (
      <div className={pageTransition ? "page-transition-enter" : ""}>
        <Login onLogin={handleLogin} />
      </div>
    );
  }

  // Show register page
  if (currentPage === "register") {
    return (
      <div className={pageTransition ? "page-transition-enter" : ""}>
        <Register onRegister={handleRegister} />
      </div>
    );
  }

  // Show main app

  const selectedCourse =
    courses.find((c) => c.id === selectedCourseId) ?? null;

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    console.log("Save course clicked");
    setCourseError(null);

    if (!name || !termStart || !termEnd) {
      setCourseError("Please fill in all required fields (course name, term start, and term end).");
      console.log("Missing required fields", { name, termStart, termEnd });
      return;
    }

    setSavingCourse(true);
    try {
      const payload = {
        name,
        termStart,
        termEnd,
        mainExamDate: mainExamDate || null,
      };
      console.log("Sending course payload:", payload);

      const postRes = await api.post("/courses", payload);
      console.log("POST /courses response:", postRes.data);

      const res = await api.get<Course[]>("/courses");
      console.log("GET /courses response:", res.data);
      setCourses(res.data);

      setName("");
      setTermStart("");
      setTermEnd("");
      setMainExamDate("");
      setCourseError(null);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || "Failed to save course. Please check your connection and try again.";
      setCourseError(errorMessage);
      console.error("Error creating course:", err);
    } finally {
      setSavingCourse(false);
    }
  };

  const fetchPlan = async (courseId: string) => {
    setLoadingPlan(true);
    try {
      const res = await api.get<StudyTask[]>(`/plans/${courseId}`);
      setTasks(res.data);
    } finally {
      setLoadingPlan(false);
    }
  };

  const fetchMaterials = async (courseId: string) => {
    setLoadingMaterials(true);
    try {
      const res = await api.get<Material[]>(`/materials/${courseId}`);
      setMaterials(res.data);
    } finally {
      setLoadingMaterials(false);
    }
  };

  const handleSelectCourse = async (courseId: string) => {
    setSelectedCourseId(courseId);
    await Promise.all([fetchPlan(courseId), fetchMaterials(courseId)]);
  };

  const handleGeneratePlan = async () => {
    if (!selectedCourseId) return;
    setLoadingPlan(true);
    try {
      await api.post(`/plans/generate/${selectedCourseId}`);
      const res = await api.get<StudyTask[]>(`/plans/${selectedCourseId}`);
      setTasks(res.data);
    } finally {
      setLoadingPlan(false);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setUploadFile(file);
  };

  const handleUpload = async () => {
    if (!selectedCourseId || !uploadFile) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", uploadFile);
      formData.append("courseId", String(selectedCourseId));

      await api.post("/materials/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const res = await api.get<Material[]>(`/materials/${selectedCourseId}`);
      setMaterials(res.data);
      setUploadFile(null);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteMaterial = async (materialId: string) => {
    if (!selectedCourseId) return;
    if (!confirm("Are you sure you want to delete this PDF file?")) return;

    try {
      await api.delete(`/materials/${materialId}`);
      const res = await api.get<Material[]>(`/materials/${selectedCourseId}`);
      setMaterials(res.data);
      // If we have a study plan, it might need to be regenerated since content changed
      if (tasks.length > 0) {
        const planRes = await api.get<StudyTask[]>(`/plans/${selectedCourseId}`);
        setTasks(planRes.data);
      }
    } catch (err: any) {
      console.error("Error deleting material:", err);
      alert("Failed to delete file. Please try again.");
    }
  };

  const handleDeleteCourse = async (courseId: string) => {
    const course = courses.find((c) => c.id === courseId);
    const courseName = course?.name || "this course";
    if (!confirm(`Are you sure you want to delete "${courseName}"? This will also delete all materials and study plans for this course.`)) {
      return;
    }

    try {
      await api.delete(`/courses/${courseId}`);
      
      // Refresh courses list
      const res = await api.get<Course[]>("/courses");
      setCourses(res.data);
      
      // Clear selection if deleted course was selected
      if (selectedCourseId === courseId) {
        setSelectedCourseId(null);
        setTasks([]);
        setMaterials([]);
      }
    } catch (err: any) {
      console.error("Error deleting course:", err);
      alert("Failed to delete course. Please try again.");
    }
  };

  return (
    <div className={`app-root ${pageTransition ? "page-transition-enter" : ""}`}>
      <div className="app-shell">
        <header className="app-header">
          <div>
            <h1 className="app-title">Learnium</h1>
            <p className="app-subtitle">
              Your intelligent study coach. Set up courses, upload syllabi, and generate structured study sessions across the term.
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            {user && (
              <span style={{ 
                color: "#cbd5e1", 
                fontSize: "14px",
                fontFamily: "var(--font-body)",
                fontWeight: 500,
                letterSpacing: "-0.01em"
              }}>
                {user.name || user.email}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="btn-smooth"
              style={{
                padding: "0.5rem 1rem",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                borderRadius: "6px",
                color: "#cbd5e1",
                fontSize: "14px",
                cursor: "pointer",
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
              }}
            >
              Logout
            </button>
            <div className="app-pill">Beta</div>
          </div>
        </header>

        <main className="app-main app-main-3col">
          {/* Left: course form */}
          <section className="panel panel-form">
            <h2 className="panel-title">Add a course</h2>
            <p className="panel-desc">
              Enter the term and exam dates. The planner uses this window to
              space out your study sessions.
            </p>

            {courseError && (
              <div style={{ 
                padding: "0.75rem", 
                marginBottom: "1rem", 
                backgroundColor: "#fee", 
                border: "1px solid #fcc",
                borderRadius: "6px",
                color: "#c33",
                fontSize: "14px"
              }}>
                {courseError}
              </div>
            )}

            <form className="course-form" onSubmit={handleCreate}>
              <div className="field full">
                <label>Course name</label>
                <input
                  placeholder="CSE 316 – Software Development"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="field">
                <label>Term start</label>
                <input
                  type="date"
                  value={termStart}
                  onChange={(e) => setTermStart(e.target.value)}
                  required
                />
              </div>

              <div className="field">
                <label>Term end</label>
                <input
                  type="date"
                  value={termEnd}
                  onChange={(e) => setTermEnd(e.target.value)}
                  required
                />
              </div>

              <div className="field full">
                <label>Main exam date (optional)</label>
                <input
                  type="date"
                  value={mainExamDate}
                  onChange={(e) => setMainExamDate(e.target.value)}
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={savingCourse}>
                  {savingCourse ? "Saving..." : "Save course"}
                </button>
              </div>
            </form>
          </section>

          {/* Middle: course list */}
          <section className="panel panel-list">
            <div className="panel-header-row">
              <h2 className="panel-title">Your courses</h2>
              {courses.length > 0 && (
                <span className="chip">{courses.length} total</span>
              )}
            </div>

            {loadingCourses ? (
              <p className="muted">Loading courses…</p>
            ) : courses.length === 0 ? (
              <p className="muted">
                No courses yet. Add one on the left to get started.
              </p>
            ) : (
              <div className="course-grid">
                {courses.map((c) => (
                  <article
                    key={c.id}
                    className={
                      "course-card" +
                      (c.id === selectedCourseId
                        ? " course-card-selected"
                        : "")
                    }
                  >
                    <div onClick={() => handleSelectCourse(c.id)} style={{ cursor: "pointer" }}>
                      <div className="course-card-header">
                        <h3 className="course-name">{c.name}</h3>
                        <button
                          type="button"
                          className="course-delete-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteCourse(c.id);
                          }}
                          title="Delete course"
                        >
                          ×
                        </button>
                      </div>
                      <p className="course-dates">
                        <span>
                          {c.termStart} → {c.termEnd}
                        </span>
                        {c.mainExamDate && (
                          <span className="exam-pill">
                            Exam: <strong>{c.mainExamDate}</strong>
                          </span>
                        )}
                      </p>
                      <p className="course-meta">
                        Click to view materials and study plan.
                      </p>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>

          {/* Right: materials + study plan */}
          <section className="panel panel-plan">
            <h2 className="panel-title">Course materials &amp; study plan</h2>
            
            {/* Today's Plan Section */}
            <div style={{ marginBottom: "24px" }}>
              <TodaysPlan />
            </div>

            <hr className="panel-divider" />

            {selectedCourse ? (
              <>
                <p className="panel-desc">
                  {selectedCourse.name} • {selectedCourse.termStart} →{" "}
                  {selectedCourse.termEnd}
                </p>

                {/* Materials upload */}
                <div className="materials-section">
                  <div className="materials-header">
                    <h3>Materials</h3>
                    {loadingMaterials ? (
                      <span className="muted small">Loading…</span>
                    ) : materials.length > 0 ? (
                      <span className="chip chip-soft">
                        {materials.length} file
                        {materials.length > 1 ? "s" : ""}
                      </span>
                    ) : (
                      <span className="muted small">No files yet</span>
                    )}
                  </div>

                  <div className="materials-upload-row">
                    <input
                      type="file"
                      accept="application/pdf"
                      onChange={handleFileChange}
                    />
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={handleUpload}
                      disabled={!uploadFile || uploading}
                    >
                      {uploading ? "Uploading…" : "Upload PDF"}
                    </button>
                  </div>

                  {materials.length > 0 && (
                    <ul className="materials-list">
                      {materials.map((m) => (
                        <li key={m.id} className="materials-item">
                          <span className="materials-name">{m.title}</span>
                          <button
                            type="button"
                            className="materials-delete-btn"
                            onClick={() => handleDeleteMaterial(m.id)}
                            title="Delete file"
                          >
                            ×
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <hr className="panel-divider" />

                {/* Study plan */}
                <div className="plan-header-row">
                  <h3>Study plan</h3>
                  <button
                    className="btn-primary"
                    onClick={handleGeneratePlan}
                    disabled={loadingPlan}
                  >
                    {tasks.length === 0 ? "Generate plan" : "Regenerate plan"}
                  </button>
                </div>

                {loadingPlan ? (
                  <p className="muted">Loading plan…</p>
                ) : tasks.length === 0 ? (
                  <p className="muted">
                    No study sessions yet. Generate a plan to create spaced
                    sessions between your term dates.
                  </p>
                ) : (
                  <ul className="task-list">
                    {tasks.map((t) => (
                      <li key={t.id} className="task-item">
                        <div className="task-date">{t.date}</div>
                        <div className="task-main">
                          <div className="task-title">{t.title}</div>
                          {t.description && (
                            <div className="task-desc">
                              {t.description.split(" • ").map((part, idx, arr) => {
                                // Highlight page references
                                const pageMatch = part.match(/(pages?)\s+(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)/i);
                                const sectionMatch = part.match(/Focus on:\s*(.+)/i);
                                
                                return (
                                  <span key={idx}>
                                    {pageMatch ? (
                                      <span>
                                        <strong className="task-page-ref">{part}</strong>
                                        {idx < arr.length - 1 && " • "}
                                      </span>
                                    ) : sectionMatch ? (
                                      <span>
                                        <strong>{sectionMatch[1]}</strong>
                                        {idx < arr.length - 1 && " • "}
                                      </span>
                                    ) : (
                                      <>
                                        {part}
                                        {idx < arr.length - 1 && " • "}
                                      </>
                                    )}
                                  </span>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </>
            ) : (
              <p className="muted">
                Select a course in the middle column to see its materials and
                study plan.
              </p>
            )}
          </section>
        </main>

        {/* Chatbot with smooth animation */}
        <div
          style={{
            position: "fixed",
            top: 0,
            right: 0,
            bottom: 0,
            width: showChatbot ? "420px" : "0",
            transition: "width 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            pointerEvents: showChatbot ? "auto" : "none",
            zIndex: 1000,
          }}
        >
          {showChatbot && (
            <Chatbot
              courseId={selectedCourseId || undefined}
              onClose={() => setShowChatbot(false)}
            />
          )}
        </div>

        {/* AI Coach Button - Bottom Right */}
        <button
          onClick={() => setShowChatbot(!showChatbot)}
          className="btn-smooth ai-coach-button"
          style={{
            position: "fixed",
            bottom: "24px",
            right: "24px",
            padding: "14px 20px",
            background: showChatbot 
              ? "linear-gradient(135deg, #6366f1, #7c3aed)"
              : "linear-gradient(135deg, #6366f1, #7c3aed)",
            border: "none",
            borderRadius: "50px",
            color: "#fff",
            fontSize: "15px",
            fontWeight: 600,
            fontFamily: "var(--font-body)",
            cursor: "pointer",
            boxShadow: "0 8px 24px rgba(99, 102, 241, 0.4)",
            zIndex: 999,
            display: "flex",
            alignItems: "center",
            gap: "8px",
            transition: "all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "translateY(-2px) scale(1.02)";
            e.currentTarget.style.boxShadow = "0 12px 32px rgba(99, 102, 241, 0.5)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "translateY(0) scale(1)";
            e.currentTarget.style.boxShadow = "0 8px 24px rgba(99, 102, 241, 0.4)";
          }}
        >
          <span>✨</span>
          {showChatbot ? "Close" : "Ask Study Buddy"}
        </button>
      </div>
    </div>
  );
}

export default App;