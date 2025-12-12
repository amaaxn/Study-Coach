import { useState, useEffect, type FormEvent } from "react";
import { api } from "../api/client";
import "../animations.css";

interface RegisterProps {
  onRegister: () => void;
}

export function Register({ onRegister }: RegisterProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [registering, setRegistering] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/auth/register", { email, password, name });
      const { access_token, user } = response.data;

      // Store token and user info
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      // Start registration animation
      setRegistering(true);
      
      // Wait for animation before calling onRegister
      setTimeout(() => {
        onRegister();
      }, 300);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || "Failed to register. Please try again.";
      setError(errorMessage);
      setLoading(false);
    }
  };

  if (registering) {
    return (
      <div className="logout-overlay">
        <div className="logout-content" style={{ textAlign: "center", color: "#fff" }}>
          <div className="loading-spinner" style={{ width: "48px", height: "48px", borderWidth: "4px", margin: "0 auto 1rem" }}></div>
          <p style={{ fontSize: "18px", fontFamily: "var(--font-body)", fontWeight: 600, letterSpacing: "-0.01em" }}>Creating your account...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={mounted ? "gradient-animated" : ""} style={{ 
      minHeight: "100vh", 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center",
      background: mounted ? undefined : "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
      transition: "background 0.5s ease"
    }}>
      <div 
        className={mounted ? "card-enter" : ""}
        style={{
          width: "100%",
          maxWidth: "400px",
          padding: "2rem",
          background: "rgba(15, 23, 42, 0.95)",
          backdropFilter: "blur(10px)",
          borderRadius: "12px",
          border: "1px solid rgba(51, 65, 85, 0.8)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3)"
        }}>
        <h1 style={{ 
          marginBottom: "0.5rem",
          fontSize: "32px",
          fontWeight: 700,
          fontFamily: "var(--font-heading)",
          letterSpacing: "-0.03em",
          lineHeight: "1.2",
          color: "#fff"
        }}>
          Create Account
        </h1>
        <p style={{ 
          marginBottom: "2rem",
          color: "#94a3b8",
          fontSize: "16px",
          fontWeight: 400,
          letterSpacing: "-0.01em",
          lineHeight: "1.5"
        }}>
          Sign up to get started with Learnium
        </p>

        {error && (
          <div 
            className="error-shake"
            style={{
              padding: "0.75rem",
              marginBottom: "1rem",
              backgroundColor: "#fee",
              border: "1px solid #fcc",
              borderRadius: "6px",
              color: "#c33",
              fontSize: "14px"
            }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "1rem" }}>
            <label style={{
              display: "block",
              marginBottom: "0.5rem",
              fontSize: "14px",
              fontWeight: 500,
              fontFamily: "var(--font-body)",
              letterSpacing: "-0.01em",
              color: "#cbd5e1"
            }}>
              Name (optional)
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input-smooth"
              style={{
                width: "100%",
                padding: "0.75rem",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "16px",
                fontFamily: "var(--font-body)",
                fontWeight: 400,
                letterSpacing: "-0.01em",
                outline: "none"
              }}
              placeholder="Your name"
            />
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label style={{
              display: "block",
              marginBottom: "0.5rem",
              fontSize: "14px",
              fontWeight: 500,
              fontFamily: "var(--font-body)",
              letterSpacing: "-0.01em",
              color: "#cbd5e1"
            }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input-smooth"
              style={{
                width: "100%",
                padding: "0.75rem",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "16px",
                fontFamily: "var(--font-body)",
                fontWeight: 400,
                letterSpacing: "-0.01em",
                outline: "none"
              }}
              placeholder="you@example.com"
            />
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label style={{
              display: "block",
              marginBottom: "0.5rem",
              fontSize: "14px",
              fontWeight: 500,
              fontFamily: "var(--font-body)",
              letterSpacing: "-0.01em",
              color: "#cbd5e1"
            }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="input-smooth"
              style={{
                width: "100%",
                padding: "0.75rem",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "16px",
                fontFamily: "var(--font-body)",
                fontWeight: 400,
                letterSpacing: "-0.01em",
                outline: "none"
              }}
              placeholder="••••••••"
            />
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{
              display: "block",
              marginBottom: "0.5rem",
              fontSize: "14px",
              fontWeight: 500,
              fontFamily: "var(--font-body)",
              letterSpacing: "-0.01em",
              color: "#cbd5e1"
            }}>
              Confirm Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="input-smooth"
              style={{
                width: "100%",
                padding: "0.75rem",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "16px",
                fontFamily: "var(--font-body)",
                fontWeight: 400,
                letterSpacing: "-0.01em",
                outline: "none"
              }}
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-smooth"
            style={{
              width: "100%",
              padding: "0.75rem",
              background: loading ? "#475569" : "linear-gradient(135deg, #4f46e5, #7c3aed)",
              border: "none",
              borderRadius: "6px",
              color: "#fff",
              fontSize: "16px",
              fontFamily: "var(--font-body)",
              fontWeight: 600,
              letterSpacing: "-0.01em",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.7 : 1,
              position: "relative",
              overflow: "hidden"
            }}
          >
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}>
                <span className="loading-spinner"></span>
                Creating account...
              </span>
            ) : (
              "Sign up"
            )}
          </button>

          <p style={{
            marginTop: "1.5rem",
            textAlign: "center",
            fontSize: "14px",
            fontFamily: "var(--font-body)",
            fontWeight: 400,
            letterSpacing: "-0.01em",
            color: "#94a3b8"
          }}>
            Already have an account?{" "}
            <a
              href="/login"
              onClick={(e) => {
                e.preventDefault();
                window.location.href = "/login";
              }}
              style={{
                color: "#6366f1",
                textDecoration: "none",
                fontWeight: 500,
                transition: "all 0.2s ease"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = "0.8";
                e.currentTarget.style.transform = "scale(1.05)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = "1";
                e.currentTarget.style.transform = "scale(1)";
              }}
            >
              Sign in
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
