import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Course {
  id: number;
  name: string;
  termStart: string;
  termEnd: string;
  mainExamDate: string | null;
}

export function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [name, setName] = useState("");
  const [termStart, setTermStart] = useState("");
  const [termEnd, setTermEnd] = useState("");
  const [mainExamDate, setMainExamDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get<Course[]>("/courses")
      .then((res) => setCourses(res.data))
      .catch((err) => {
        console.error("Failed to load courses:", err);
        setError("Failed to load courses");
      });
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      await api.post("/courses", {
        name,
        termStart,
        termEnd,
        mainExamDate: mainExamDate || null,
      });
      const res = await api.get<Course[]>("/courses");
      setCourses(res.data);
      setName("");
      setTermStart("");
      setTermEnd("");
      setMainExamDate("");
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || "Failed to save course";
      setError(errorMessage);
      console.error("Failed to save course:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>My Courses</h1>

      {error && (
        <div style={{ 
          padding: "1rem", 
          marginBottom: "1rem", 
          backgroundColor: "#fee", 
          border: "1px solid #fcc",
          borderRadius: "4px",
          color: "#c33"
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleCreate} style={{ marginBottom: "1.5rem" }}>
        <input
          placeholder="Course name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="date"
          value={termStart}
          onChange={(e) => setTermStart(e.target.value)}
          required
        />
        <input
          type="date"
          value={termEnd}
          onChange={(e) => setTermEnd(e.target.value)}
          required
        />
        <input
          type="date"
          value={mainExamDate}
          onChange={(e) => setMainExamDate(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Add course"}
        </button>
      </form>

      <ul>
        {courses.map((c) => (
          <li key={c.id}>
            {c.name} ({c.termStart} → {c.termEnd})
          </li>
        ))}
      </ul>
    </div>
  );
}