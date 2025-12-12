import { useState, FormEvent } from "react";
import { api } from "../api/client";

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

      // Notify parent component
      onRegister();
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || "Failed to register. Please try again.";
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
          Create Account
        </h1>
        <p style={{ 
          marginBottom: "2rem",
          color: "#94a3b8",
          fontSize: "14px"
        }}>
          Sign up to get started with Study Coach
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
              Name (optional)
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{
                width: "100%",
                padding: "0.75rem",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                borderRadius: "6px",
                color: "#fff",
                fontSize: "14px"
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

          <div style={{ marginBottom: "1rem" }}>
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

          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{
              display: "block",
              marginBottom: "0.5rem",
              fontSize: "14px",
              fontWeight: 500,
              color: "#cbd5e1"
            }}>
              Confirm Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
            {loading ? "Creating account..." : "Sign up"}
          </button>

          <p style={{
            marginTop: "1.5rem",
            textAlign: "center",
            fontSize: "14px",
            color: "#94a3b8"
          }}>
            Already have an account?{" "}
            <a
              href="/login"
              style={{
                color: "#6366f1",
                textDecoration: "none",
                fontWeight: 500
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
