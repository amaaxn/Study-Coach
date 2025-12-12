import { useState, useEffect } from "react";
import { api } from "../api/client";

interface TodayTask {
  id: string;
  courseId: string;
  courseName: string;
  date: string;
  title: string;
  description: string | null;
  completed: boolean;
}

interface UpcomingTask {
  id: string;
  courseId: string;
  courseName: string;
  date: string;
  title: string;
  daysAhead: number;
}

interface TodaysPlanData {
  today: TodayTask[];
  upcoming: UpcomingTask[];
  date: string;
}

export function TodaysPlan() {
  const [plan, setPlan] = useState<TodaysPlanData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTodaysPlan();
    // Refresh every minute to keep date current
    const interval = setInterval(() => {
      fetchTodaysPlan();
    }, 60000); // 1 minute
    
    return () => clearInterval(interval);
  }, []);

  const fetchTodaysPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get<TodaysPlanData>("/plans/today");
      // Get today's date in user's local timezone
      const todayLocal = getTodayDateString();
      const planData = response.data;
      
      // Filter tasks to only show today's tasks based on local date
      // This ensures timezone correctness - tasks are matched to the user's "today"
      const todayLocalTasks = planData.today.filter(task => {
        const taskDate = task.date.split('T')[0]; // Get just YYYY-MM-DD part if there's a time component
        return taskDate === todayLocal;
      });
      
      // Filter upcoming tasks to only show future dates from today's perspective
      const todayDate = new Date();
      todayDate.setHours(0, 0, 0, 0);
      
      const upcomingLocal = planData.upcoming.filter(task => {
        try {
          const [year, month, day] = task.date.split('-').map(Number);
          const taskDate = new Date(year, month - 1, day);
          taskDate.setHours(0, 0, 0, 0);
          const diffTime = taskDate.getTime() - todayDate.getTime();
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          return diffDays >= 1 && diffDays <= 3;
        } catch {
          return false;
        }
      }).map(task => {
        // Recalculate daysAhead based on local date
        try {
          const [year, month, day] = task.date.split('-').map(Number);
          const taskDate = new Date(year, month - 1, day);
          taskDate.setHours(0, 0, 0, 0);
          const diffTime = taskDate.getTime() - todayDate.getTime();
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          return { ...task, daysAhead: diffDays };
        } catch {
          return task;
        }
      });
      
      setPlan({
        ...planData,
        today: todayLocalTasks,
        upcoming: upcomingLocal,
        date: todayLocal, // Use local date for display
      });
    } catch (err: any) {
      setError("Failed to load today's plan");
      console.error("Error fetching today's plan:", err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      // Handle ISO date string (YYYY-MM-DD) - create date at local midnight
      const [year, month, day] = dateStr.split('-').map(Number);
      const date = new Date(year, month - 1, day); // month is 0-indexed
      
      return date.toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      });
    } catch {
      return dateStr;
    }
  };

  const getTodayDateString = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  if (loading) {
    return (
      <div
        style={{
          padding: "2rem",
          background: "rgba(15, 23, 42, 0.95)",
          borderRadius: "12px",
          border: "1px solid rgba(51, 65, 85, 0.8)",
          textAlign: "center",
        }}
      >
        <div
          className="loading-spinner"
          style={{
            width: "32px",
            height: "32px",
            borderWidth: "3px",
            margin: "0 auto 1rem",
          }}
        ></div>
        <p style={{ color: "#94a3b8", fontSize: "14px" }}>Loading today's plan...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          padding: "2rem",
          background: "rgba(15, 23, 42, 0.95)",
          borderRadius: "12px",
          border: "1px solid rgba(239, 68, 68, 0.5)",
          color: "#ef4444",
          textAlign: "center",
        }}
      >
        {error}
      </div>
    );
  }

  if (!plan) {
    return null;
  }

  return (
    <div
      style={{
        padding: "1.5rem",
        background: "rgba(15, 23, 42, 0.95)",
        borderRadius: "12px",
        border: "1px solid rgba(51, 65, 85, 0.8)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "1.5rem",
        }}
      >
        <div>
          <h2
            style={{
              margin: 0,
              fontSize: "20px",
              fontWeight: 600,
              fontFamily: "var(--font-heading)",
              letterSpacing: "-0.01em",
              color: "#fff",
            }}
          >
            Today's Plan
          </h2>
          <p
            style={{
              margin: "4px 0 0",
              fontSize: "14px",
              color: "#94a3b8",
            }}
          >
            {formatDate(plan.date)}
          </p>
        </div>
      </div>

      {plan.today.length === 0 ? (
        <div
          style={{
            padding: "2rem",
            textAlign: "center",
            color: "#94a3b8",
          }}
        >
          <p style={{ margin: 0, fontSize: "14px" }}>
            No study sessions scheduled for today. Generate a study plan for your courses to get started!
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {plan.today.map((task) => (
            <div
              key={task.id}
              style={{
                padding: "14px",
                background: "rgba(30, 41, 59, 0.6)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                borderRadius: "8px",
                transition: "all 0.2s ease",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "12px",
                }}
              >
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={async () => {
                    try {
                      const response = await api.put(`/plans/task/${task.id}/complete`);
                      setPlan((prev) => {
                        if (!prev) return prev;
                        return {
                          ...prev,
                          today: prev.today.map((t) =>
                            t.id === task.id ? { ...t, completed: response.data.completed } : t
                          ),
                        };
                      });
                    } catch (err) {
                      console.error("Failed to update task:", err);
                    }
                  }}
                  style={{
                    marginTop: "2px",
                    width: "18px",
                    height: "18px",
                    cursor: "pointer",
                  }}
                />
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      fontSize: "13px",
                      color: "#6366f1",
                      fontWeight: 500,
                      marginBottom: "4px",
                    }}
                  >
                    {task.courseName}
                  </div>
                  <div
                    style={{
                      fontSize: "15px",
                      fontWeight: 600,
                      fontFamily: "var(--font-heading)",
                      color: "#fff",
                      marginBottom: "6px",
                    }}
                  >
                    {task.title}
                  </div>
                  {task.description && (
                    <div
                      style={{
                        fontSize: "13px",
                        color: "#94a3b8",
                        lineHeight: "1.5",
                        marginTop: "4px",
                      }}
                    >
                      {task.description}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {plan.upcoming.length > 0 && (
        <div style={{ marginTop: "1.5rem", paddingTop: "1.5rem", borderTop: "1px solid rgba(51, 65, 85, 0.8)" }}>
          <h3
            style={{
              margin: "0 0 12px",
              fontSize: "16px",
              fontWeight: 600,
              fontFamily: "var(--font-heading)",
              color: "#fff",
            }}
          >
            Upcoming
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {plan.upcoming.map((task) => (
              <div
                key={task.id}
                style={{
                  padding: "10px 12px",
                  background: "rgba(30, 41, 59, 0.4)",
                  border: "1px solid rgba(51, 65, 85, 0.6)",
                  borderRadius: "6px",
                  fontSize: "13px",
                  color: "#94a3b8",
                }}
              >
                <span style={{ fontWeight: 500, color: "#fff" }}>
                  {task.courseName}:
                </span>{" "}
                {task.title} (
                {task.daysAhead === 1 ? "tomorrow" : `in ${task.daysAhead} days`})
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
