import axios from "axios";

// Use environment variable for API URL in production, or default to /api for dev
// If VITE_API_URL is set, use it directly. Otherwise use /api (relative to frontend domain)
// NOTE: VITE_API_URL should include /api suffix (e.g., https://backend.com/api)
let API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

// Ensure API_BASE_URL ends with /api if it's a full URL without it
if (API_BASE_URL.startsWith("http") && !API_BASE_URL.endsWith("/api")) {
    API_BASE_URL = API_BASE_URL.endsWith("/") ? API_BASE_URL + "api" : API_BASE_URL + "/api";
}

console.log("🌐 API Base URL:", API_BASE_URL);

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors (unauthorized) - token expired or invalid
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.status, error.response?.data || error.message);
    
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      // Redirect to login if not already there
      if (!window.location.pathname.includes("/login") && !window.location.pathname.includes("/register")) {
        window.location.href = "/login";
      }
    }
    
    // Log network errors
    if (!error.response) {
      console.error("Network error - is backend accessible?", API_BASE_URL);
    }
    
    return Promise.reject(error);
  }
);

export default api;
