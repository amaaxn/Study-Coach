import { useState, FormEvent } from "react";
import { api } from "../api/client";

interface LoginProps {
  onLogin: () => void;
}

export function Login({ onLogin }: LoginProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await api.post("/auth/login", { email, password });
      const { access_token, user } = response.data;

      // Store token and user info
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      // Notify parent component
      onLogin();
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || "Failed to login. Please try again.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "center",
      background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"
    }}>
      <div style={{
        width: "100%",
        maxWidth: "400px",
        padding: "2rem",
        background: "rgba(15, 23, 42, 0.9)",
        borderRadius: "12px",
        border: "1px solid rgba(51, 65, 85, 0.8)",
        boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3)"
      }}>
        <h1 style={{ 
          marginBottom: "0.5rem",
          fontSize: "24px",
          fontWeight: 600,
          color: "#fff"
        }}>
          Study Coach
        </h1>
        <p style={{ 
          marginBottom: "2rem",
          color: "#94a3b8",
          fontSize: "14px"
        }}>
          Sign in to your account
        </p>

        {error && (
          <div style={{
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
              color: "#cbd5e1"
            }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "0.75rem",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "14px"
              }}
              placeholder="you@example.com"
            />
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{
              display: "block",
              marginBottom: "0.5rem",
              fontSize: "14px",
              fontWeight: 500,
              color: "#cbd5e1"
            }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "0.75rem",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "14px"
              }}
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "0.75rem",
              background: loading ? "#475569" : "linear-gradient(135deg, #4f46e5, #7c3aed)",
              border: "none",
              borderRadius: "6px",
              color: "#fff",
              fontSize: "14px",
              fontWeight: 500,
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>

          <p style={{
            marginTop: "1.5rem",
            textAlign: "center",
            fontSize: "14px",
            color: "#94a3b8"
          }}>
            Don't have an account?{" "}
            <a
              href="/register"
              style={{
                color: "#6366f1",
                textDecoration: "none",
                fontWeight: 500
              }}
            >
              Sign up
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
