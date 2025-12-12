import { useState, useRef, useEffect, FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import { api } from "../api/client";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

interface ChatbotProps {
  courseId?: string;
  onClose?: () => void;
}

export function Chatbot({ courseId, onClose }: ChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
              content: "Hey there! 👋 I'm your Study Buddy. I'm here to help you ace your studies - whether you need help creating study plans, understanding course material, or planning your learning strategy. What can I help you with today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // Build conversation history for context
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await api.post("/chat/message", {
        message: userMessage.content,
        history: history,
        courseId: courseId,
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.response,
        timestamp: response.data.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: Message = {
        role: "assistant",
        content: "I'm sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
      console.error("Chat error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={mounted ? "chatbot-slide-in" : ""}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        background: "rgba(15, 23, 42, 0.98)",
        backdropFilter: "blur(20px)",
        border: "none",
        borderLeft: "1px solid rgba(51, 65, 85, 0.8)",
        boxShadow: "-10px 0 30px rgba(0, 0, 0, 0.3)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* Header with gradient */}
      <div
        style={{
          padding: "20px 24px",
          borderBottom: "1px solid rgba(51, 65, 85, 0.8)",
          background: "linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(124, 58, 237, 0.1))",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          <h3
            style={{
              margin: 0,
              fontSize: "20px",
              fontWeight: 600,
              fontFamily: "var(--font-heading)",
              letterSpacing: "-0.01em",
              background: "linear-gradient(135deg, #818cf8, #a78bfa)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            Study Buddy
          </h3>
          <p
            style={{
              margin: "6px 0 0",
              fontSize: "13px",
              color: "#94a3b8",
              fontFamily: "var(--font-body)",
            }}
          >
            Ask me anything about your studies
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "#94a3b8",
              fontSize: "28px",
              cursor: "pointer",
              padding: "0",
              width: "36px",
              height: "36px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: "8px",
              transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(239, 68, 68, 0.2)";
              e.currentTarget.style.color = "#ef4444";
              e.currentTarget.style.transform = "rotate(90deg)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "#94a3b8";
              e.currentTarget.style.transform = "rotate(0deg)";
            }}
          >
            ×
          </button>
        )}
      </div>

      {/* Messages with smooth scrolling */}
      <div
        ref={messagesContainerRef}
        style={{
          flex: 1,
          overflowY: "auto",
          overflowX: "hidden",
          padding: "24px",
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          scrollBehavior: "smooth",
        }}
        className="messages-container"
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className="message-enter"
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              animation: `messageSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) ${idx * 0.05}s both`,
            }}
          >
            <div
              style={{
                maxWidth: "85%",
                padding: "14px 18px",
                borderRadius: msg.role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                background:
                  msg.role === "user"
                    ? "linear-gradient(135deg, #6366f1, #7c3aed)"
                    : "rgba(30, 41, 59, 0.9)",
                border:
                  msg.role === "assistant"
                    ? "1px solid rgba(51, 65, 85, 0.8)"
                    : "none",
                color: "#fff",
                fontSize: "14px",
                lineHeight: "1.6",
                fontFamily: "var(--font-body)",
                boxShadow: msg.role === "user" 
                  ? "0 4px 12px rgba(99, 102, 241, 0.3)"
                  : "0 2px 8px rgba(0, 0, 0, 0.2)",
                position: "relative",
              }}
            >
              {msg.role === "assistant" ? (
                <div
                  style={{
                    color: "#e2e8f0",
                  }}
                >
                  <ReactMarkdown
                    components={{
                      p: ({ node, ...props }) => (
                        <p style={{ margin: "0 0 10px 0", lineHeight: "1.6" }} {...props} />
                      ),
                      strong: ({ node, ...props }) => (
                        <strong
                          style={{
                            fontWeight: 600,
                            color: "#fff",
                            fontFamily: "var(--font-heading)",
                          }}
                          {...props}
                        />
                      ),
                      em: ({ node, ...props }) => (
                        <em style={{ fontStyle: "italic", opacity: 0.9 }} {...props} />
                      ),
                      ul: ({ node, ...props }) => (
                        <ul
                          style={{
                            margin: "8px 0",
                            paddingLeft: "20px",
                            listStyleType: "disc",
                          }}
                          {...props}
                        />
                      ),
                      ol: ({ node, ...props }) => (
                        <ol
                          style={{
                            margin: "8px 0",
                            paddingLeft: "20px",
                            listStyleType: "decimal",
                          }}
                          {...props}
                        />
                      ),
                      li: ({ node, ...props }) => (
                        <li style={{ margin: "4px 0", lineHeight: "1.6" }} {...props} />
                      ),
                      h1: ({ node, ...props }) => (
                        <h1
                          style={{
                            fontSize: "18px",
                            fontWeight: 600,
                            margin: "12px 0 8px 0",
                            fontFamily: "var(--font-heading)",
                            color: "#fff",
                          }}
                          {...props}
                        />
                      ),
                      h2: ({ node, ...props }) => (
                        <h2
                          style={{
                            fontSize: "16px",
                            fontWeight: 600,
                            margin: "10px 0 6px 0",
                            fontFamily: "var(--font-heading)",
                            color: "#fff",
                          }}
                          {...props}
                        />
                      ),
                      h3: ({ node, ...props }) => (
                        <h3
                          style={{
                            fontSize: "15px",
                            fontWeight: 600,
                            margin: "8px 0 4px 0",
                            fontFamily: "var(--font-heading)",
                            color: "#fff",
                          }}
                          {...props}
                        />
                      ),
                      code: ({ node, inline, ...props }: any) =>
                        inline ? (
                          <code
                            style={{
                              background: "rgba(0, 0, 0, 0.3)",
                              padding: "2px 6px",
                              borderRadius: "4px",
                              fontSize: "13px",
                              fontFamily: "ui-monospace, monospace",
                            }}
                            {...props}
                          />
                        ) : (
                          <code
                            style={{
                              background: "rgba(0, 0, 0, 0.3)",
                              padding: "8px",
                              borderRadius: "6px",
                              display: "block",
                              fontSize: "13px",
                              fontFamily: "ui-monospace, monospace",
                              margin: "8px 0",
                            }}
                            {...props}
                          />
                        ),
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <div>{msg.content}</div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div
            className="loading-message-enter"
            style={{
              display: "flex",
              justifyContent: "flex-start",
              animation: "fadeIn 0.3s ease",
            }}
          >
            <div
              style={{
                padding: "14px 18px",
                borderRadius: "18px 18px 18px 4px",
                background: "rgba(30, 41, 59, 0.9)",
                border: "1px solid rgba(51, 65, 85, 0.8)",
                display: "flex",
                alignItems: "center",
                gap: "10px",
              }}
            >
              <div
                className="loading-spinner"
                style={{
                  width: "16px",
                  height: "16px",
                  borderWidth: "2px",
                  borderColor: "#6366f1 transparent transparent transparent",
                }}
              ></div>
              <span style={{ fontSize: "13px", color: "#94a3b8" }}>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input with better styling */}
      <form
        onSubmit={handleSend}
        style={{
          padding: "20px 24px",
          borderTop: "1px solid rgba(51, 65, 85, 0.8)",
          background: "rgba(15, 23, 42, 0.95)",
        }}
      >
        <div style={{ display: "flex", gap: "10px", alignItems: "flex-end" }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything..."
            disabled={loading}
            className="input-smooth"
            style={{
              flex: 1,
              padding: "12px 16px",
              background: "rgba(30, 41, 59, 0.9)",
              border: "1px solid rgba(51, 65, 85, 0.8)",
              borderRadius: "12px",
              color: "#fff",
              fontSize: "14px",
              fontFamily: "var(--font-body)",
              outline: "none",
              transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = "#6366f1";
              e.currentTarget.style.boxShadow = "0 0 0 3px rgba(99, 102, 241, 0.1)";
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = "rgba(51, 65, 85, 0.8)";
              e.currentTarget.style.boxShadow = "none";
            }}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="btn-smooth"
            style={{
              padding: "12px 24px",
              background:
                loading || !input.trim()
                  ? "#475569"
                  : "linear-gradient(135deg, #6366f1, #7c3aed)",
              border: "none",
              borderRadius: "12px",
              color: "#fff",
              fontSize: "14px",
              fontWeight: 600,
              fontFamily: "var(--font-body)",
              cursor: loading || !input.trim() ? "not-allowed" : "pointer",
              opacity: loading || !input.trim() ? 0.6 : 1,
              transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
              boxShadow:
                loading || !input.trim()
                  ? "none"
                  : "0 4px 12px rgba(99, 102, 241, 0.3)",
            }}
            onMouseEnter={(e) => {
              if (!loading && input.trim()) {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "0 6px 16px rgba(99, 102, 241, 0.4)";
              }
            }}
            onMouseLeave={(e) => {
              if (!loading && input.trim()) {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(99, 102, 241, 0.3)";
              }
            }}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
