/**
 * PrepPilot AI — API Client Module
 * Handles all REST API communications with the FastAPI backend.
 */

const API_BASE = window.PREPPILOT_API_URL || 
  (window.location.origin.includes(":3000") || window.location.origin.includes("lovable.app") 
    ? "http://127.0.0.1:8000" 
    : window.location.origin);

class ApiClient {
  constructor() {
    this.token = localStorage.getItem("preppilot_token") || null;
    this.user = JSON.parse(localStorage.getItem("preppilot_user") || "null");
  }

  setAuth(token, user) {
    this.token = token;
    this.user = user;
    if (token) {
      localStorage.setItem("preppilot_token", token);
      localStorage.setItem("preppilot_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("preppilot_token");
      localStorage.removeItem("preppilot_user");
    }
  }

  isAuthenticated() {
    return !!this.token;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = options.headers || {};

    if (this.token && !headers["Authorization"]) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    try {
      const response = await fetch(url, { ...options, headers });

      if (response.status === 401) {
        // Token expired or invalid
        this.setAuth(null, null);
        window.dispatchEvent(new CustomEvent("auth:expired"));
        throw new Error("Session expired. Please log in again.");
      }

      if (!response.ok) {
        let errorMsg = `Error ${response.status}: ${response.statusText}`;
        try {
          const errData = await response.json();
          if (errData.detail) {
            errorMsg = Array.isArray(errData.detail)
              ? errData.detail.map((d) => d.msg || JSON.stringify(d)).join(", ")
              : errData.detail;
          }
        } catch (_) {}
        throw new Error(errorMsg);
      }

      return await response.json();
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }

  // ── Auth Endpoints ──
  async login(email, password) {
    const data = await this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setAuth(data.access_token, data.user);
    return data;
  }

  async register(full_name, email, password) {
    return await this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name, email, password }),
    });
  }

  async getMe() {
    return await this.request("/api/auth/me");
  }

  logout() {
    this.setAuth(null, null);
    window.location.reload();
  }

  // ── Dashboard Endpoints ──
  async getDashboardStats() {
    return await this.request("/api/dashboard/stats");
  }

  async getDashboardCharts() {
    return await this.request("/api/dashboard/charts");
  }

  async getDashboardHeatmap() {
    return await this.request("/api/dashboard/heatmap");
  }

  async getDashboardRecommendations() {
    return await this.request("/api/dashboard/recommendations");
  }

  // ── Resume Endpoints ──
  async uploadResume(formData) {
    return await this.request("/api/resume/upload", {
      method: "POST",
      body: formData,
    });
  }

  async getResumeHistory() {
    return await this.request("/api/resume/history");
  }

  // ── Interview Endpoints ──
  async getCompanies() {
    return await this.request("/api/interview/companies");
  }

  async startInterview(company_id) {
    return await this.request("/api/interview/start", {
      method: "POST",
      body: JSON.stringify({ company_id }),
    });
  }

  async submitInterviewAnswer(sessionId, answer) {
    return await this.request(`/api/interview/${sessionId}/answer`, {
      method: "POST",
      body: JSON.stringify({ answer }),
    });
  }

  async endInterview(sessionId) {
    return await this.request(`/api/interview/${sessionId}/end`, {
      method: "POST",
    });
  }

  async getInterviewHistory() {
    return await this.request("/api/interview/history");
  }

  // ── Coding Endpoints ──
  async getCodingQuestions(difficulty = "", category = "", company = "") {
    let url = "/api/coding/questions?";
    if (difficulty) url += `difficulty=${encodeURIComponent(difficulty)}&`;
    if (category) url += `category=${encodeURIComponent(category)}&`;
    if (company && company.toLowerCase() !== "all") url += `company=${encodeURIComponent(company)}&`;
    return await this.request(url);
  }

  async getCodingQuestion(id) {
    return await this.request(`/api/coding/questions/${id}`);
  }

  async runCode(code, language = "python") {
    return await this.request("/api/coding/run", {
      method: "POST",
      body: JSON.stringify({ code, language }),
    });
  }

  async submitCode(questionId, code, language = "python") {
    return await this.request(`/api/coding/questions/${questionId}/submit`, {
      method: "POST",
      body: JSON.stringify({ code, language }),
    });
  }

  async toggleBookmark(question_id) {
    return await this.request("/api/coding/bookmark", {
      method: "POST",
      body: JSON.stringify({ question_id }),
    });
  }

  async getLeaderboard() {
    return await this.request("/api/coding/leaderboard");
  }

  // ── Planner Endpoints ──
  async generateStudyPlan(preferences) {
    return await this.request("/api/planner/generate", {
      method: "POST",
      body: JSON.stringify({ preferences }),
    });
  }

  async getPlans() {
    return await this.request("/api/planner/plans");
  }

  async getTasks(planId = null) {
    const url = planId ? `/api/planner/tasks?plan_id=${planId}` : "/api/planner/tasks";
    return await this.request(url);
  }

  async toggleTask(taskId, is_completed) {
    return await this.request(`/api/planner/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify({ is_completed }),
    });
  }

  // ── AI Mentor Chat Endpoints ──
  async sendChatMessage(message, mode = "placement", session_id = null) {
    let url = "/api/chat/send";
    if (session_id) url += `?session_id=${session_id}`;
    return await this.request(url, {
      method: "POST",
      body: JSON.stringify({ message, mode }),
    });
  }

  async getChatSessions() {
    return await this.request("/api/chat/sessions");
  }

  async getChatSession(id) {
    return await this.request(`/api/chat/sessions/${id}`);
  }

  // ── Admin Endpoints ──
  async getAdminStats() {
    return await this.request("/api/admin/stats");
  }

  async getAdminUsers() {
    return await this.request("/api/admin/users");
  }

  async getAdminCompanies() {
    return await this.request("/api/admin/companies");
  }

  async getAdminQuestions() {
    return await this.request("/api/admin/questions");
  }

  async addAdminCompany(companyData) {
    return await this.request("/api/admin/companies", {
      method: "POST",
      body: JSON.stringify(companyData),
    });
  }

  async addAdminQuestion(questionData) {
    return await this.request("/api/admin/questions", {
      method: "POST",
      body: JSON.stringify(questionData),
    });
  }
}

export const api = new ApiClient();
