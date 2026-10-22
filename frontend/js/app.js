/**
 * PrepPilot AI — Main Application Controller
 * Handles SPA navigation, state management, charts, and module integrations.
 */

import { api } from "./api.js";

// Global State
let radarChartInstance = null;
let currentCodingQuestion = null;
let activeInterviewSessionId = null;

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", async () => {
  setupNavigation();
  setupAuth();
  setupResume();
  setupInterview();
  setupCoding();
  setupPlanner();
  setupChat();

  // Check login state
  if (api.isAuthenticated()) {
    try {
      const me = await api.getMe();
      api.setAuth(api.token, me);
      updateAuthUI(me);
    } catch (e) {
      console.warn("Auth token invalid:", e);
      api.setAuth(null, null);
      updateAuthUI(null);
    }
  } else {
    updateAuthUI(null);
  }

  // Initial view load
  switchView("dashboard");
});

// Toast notification helper
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "custom-toast";
  const icon =
    type === "success"
      ? '<i class="fa-solid fa-circle-check text-success"></i>'
      : type === "error"
      ? '<i class="fa-solid fa-circle-xmark text-danger"></i>'
      : '<i class="fa-solid fa-circle-info text-info"></i>';

  toast.innerHTML = `${icon} <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ─────────────────────────────────────────────────────────────
// 1. Navigation & View Routing
// ─────────────────────────────────────────────────────────────
function setupNavigation() {
  const navButtons = document.querySelectorAll(".nav-pill-btn");
  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetView = btn.dataset.view;
      if (targetView) switchView(targetView);
    });
  });

  // Action button routing
  document.querySelectorAll("[data-view]").forEach((el) => {
    if (!el.classList.contains("nav-pill-btn")) {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        const target = el.dataset.view;
        if (target) switchView(target);
      });
    }
  });

  // Brand click -> dashboard
  document.getElementById("nav-brand")?.addEventListener("click", (e) => {
    e.preventDefault();
    switchView("dashboard");
  });
}

function switchView(viewName) {
  // Update nav buttons
  document.querySelectorAll(".nav-pill-btn").forEach((btn) => {
    if (btn.dataset.view === viewName) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Hide all views and show target view
  document.querySelectorAll(".app-view").forEach((view) => {
    view.classList.add("d-none");
  });

  const target = document.getElementById(`view-${viewName}`);
  if (target) {
    target.classList.remove("d-none");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Load view-specific data
  if (viewName === "dashboard") loadDashboard();
  if (viewName === "interview") loadInterviewScreen();
  if (viewName === "coding") loadCodingArena();
  if (viewName === "planner") loadPlanner();
  if (viewName === "leaderboard") loadLeaderboard();
  if (viewName === "admin") loadAdminDashboard();
  if (viewName === "resume") loadResumeHistory();
}

// ─────────────────────────────────────────────────────────────
// 2. Authentication Management
// ─────────────────────────────────────────────────────────────
function setupAuth() {
  const authContainer = document.getElementById("auth-state-container");
  const tabLogin = document.getElementById("tab-btn-login");
  const tabRegister = document.getElementById("tab-btn-register");
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");

  // Tab toggling
  tabLogin?.addEventListener("click", () => {
    tabLogin.classList.add("active");
    tabRegister.classList.remove("active");
    formLogin.classList.remove("d-none");
    formRegister.classList.add("d-none");
  });

  tabRegister?.addEventListener("click", () => {
    tabRegister.classList.add("active");
    tabLogin.classList.remove("active");
    formRegister.classList.remove("d-none");
    formLogin.classList.add("d-none");
  });

  // Login Submit
  formLogin?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    try {
      const data = await api.login(email, password);
      showToast(`Welcome back, ${data.user.full_name}!`, "success");
      bootstrap.Modal.getInstance(document.getElementById("authModal"))?.hide();
      updateAuthUI(data.user);
      loadDashboard();
    } catch (err) {
      showToast(err.message || "Login failed", "error");
    }
  });

  // Register Submit
  formRegister?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const full_name = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;

    try {
      await api.register(full_name, email, password);
      showToast("Account created successfully! Logging you in...", "success");
      const loginData = await api.login(email, password);
      bootstrap.Modal.getInstance(document.getElementById("authModal"))?.hide();
      updateAuthUI(loginData.user);
      loadDashboard();
    } catch (err) {
      showToast(err.message || "Registration failed", "error");
    }
  });

  // Quick 1-Click Demo Admin Button
  document.getElementById("btn-quick-admin-login")?.addEventListener("click", async () => {
    document.getElementById("login-email").value = "admin@preppilot.com";
    document.getElementById("login-password").value = "PrepPilot#2026";
    try {
      const data = await api.login("admin@preppilot.com", "PrepPilot#2026");
      showToast(`Logged in as Administrator (${data.user.full_name})`, "success");
      bootstrap.Modal.getInstance(document.getElementById("authModal"))?.hide();
      updateAuthUI(data.user);
      loadDashboard();
    } catch (err) {
      showToast(err.message || "Quick login failed", "error");
    }
  });
}

function updateAuthUI(user) {
  const container = document.getElementById("auth-state-container");
  const streakPill = document.getElementById("streak-days-val");
  const scorePill = document.getElementById("user-score-val");
  const greeting = document.getElementById("dash-greeting");
  const adminBtn = document.getElementById("nav-btn-admin");

  if (user) {
    if (greeting) greeting.textContent = `Welcome back, ${user.full_name}!`;
    if (streakPill) streakPill.textContent = user.streak_days || 1;
    if (scorePill) scorePill.textContent = user.total_score || 0;

    // Show admin tab if admin
    if (user.is_admin) {
      adminBtn?.classList.remove("d-none");
    } else {
      adminBtn?.classList.add("d-none");
    }

    container.innerHTML = `
      <div class="dropdown">
        <button class="btn btn-outline-custom dropdown-toggle py-1 px-3 d-flex align-items-center gap-2" type="button" data-bs-toggle="dropdown">
          <div style="width:28px; height:28px; border-radius:50%; background: linear-gradient(135deg, var(--primary), var(--secondary)); display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.8rem; color:#fff;">
            ${user.full_name ? user.full_name[0].toUpperCase() : "U"}
          </div>
          <span class="d-none d-sm-inline fw-semibold">${user.full_name.split(" ")[0]}</span>
        </button>
        <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end shadow border-secondary border-opacity-25" style="background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(12px);">
          <li><h6 class="dropdown-header text-muted">${user.email}</h6></li>
          <li><span class="dropdown-item-text small text-secondary">Role: <strong class="text-info">${user.is_admin ? "Administrator" : "Candidate"}</strong></span></li>
          <li><hr class="dropdown-divider border-secondary border-opacity-25"></li>
          <li><a class="dropdown-item text-danger" href="#" id="menu-btn-logout"><i class="fa-solid fa-arrow-right-from-bracket me-2"></i> Logout</a></li>
        </ul>
      </div>
    `;

    document.getElementById("menu-btn-logout")?.addEventListener("click", (e) => {
      e.preventDefault();
      api.logout();
    });
  } else {
    adminBtn?.classList.add("d-none");
    container.innerHTML = `
      <button class="btn-primary-custom" id="btn-open-auth" data-bs-toggle="modal" data-bs-target="#authModal">
        <i class="fa-solid fa-arrow-right-to-bracket"></i> Login / Register
      </button>
    `;
  }
}

// ─────────────────────────────────────────────────────────────
// 3. Dashboard Module
// ─────────────────────────────────────────────────────────────
async function loadDashboard() {
  if (!api.isAuthenticated()) return;

  try {
    const [stats, charts, recs] = await Promise.all([
      api.getDashboardStats(),
      api.getDashboardCharts().catch(() => null),
      api.getDashboardRecommendations().catch(() => null),
    ]);

    // Update Readiness Gauge
    const readinessScore = stats.readiness_score || 70;
    const readinessVal = document.getElementById("dash-readiness-val");
    const gaugeCircle = document.getElementById("readiness-gauge-circle");
    if (readinessVal) readinessVal.textContent = `${Math.round(readinessScore)}%`;

    if (gaugeCircle) {
      const circumference = 2 * Math.PI * 75; // ~471.2
      const offset = circumference - (readinessScore / 100) * circumference;
      gaugeCircle.style.strokeDashoffset = offset;
    }

    // Update Metric Cards
    const resumeScoreEl = document.getElementById("dash-resume-score");
    if (resumeScoreEl) resumeScoreEl.innerHTML = `${stats.ats_score || 0}<span class="fs-6 text-muted">/100</span>`;

    const interviewScoreEl = document.getElementById("dash-interview-score");
    if (interviewScoreEl) interviewScoreEl.innerHTML = `${Math.round(stats.avg_interview_score || 0)}<span class="fs-6 text-muted">%</span>`;

    const interviewCountEl = document.getElementById("dash-interview-count");
    if (interviewCountEl) interviewCountEl.textContent = `${stats.interview_count || 0} Sessions`;

    const problemsSolvedEl = document.getElementById("dash-problems-solved");
    if (problemsSolvedEl) {
      problemsSolvedEl.innerHTML = `${stats.unique_solved || 0}<span class="fs-6 text-muted">/${stats.total_questions || 30}</span>`;
    }

    // Render Radar Chart
    renderCompetencyRadar(charts?.categories);

    // Render Recommendations
    renderRecommendations(recs?.recommendations);
  } catch (err) {
    console.error("Dashboard load failed:", err);
  }
}

function renderCompetencyRadar(categoriesData) {
  const ctx = document.getElementById("competencyRadarChart");
  if (!ctx) return;

  const defaultData = [
    { name: "DSA & Algorithms", score: 75 },
    { name: "System Design", score: 60 },
    { name: "Core CS (OS/DBMS/CN)", score: 80 },
    { name: "Behavioral & STAR", score: 70 },
    { name: "Problem Solving Speed", score: 65 },
  ];

  const labels = categoriesData ? categoriesData.map((c) => c.name) : defaultData.map((d) => d.name);
  const data = categoriesData ? categoriesData.map((c) => c.score) : defaultData.map((d) => d.score);

  if (radarChartInstance) radarChartInstance.destroy();

  radarChartInstance = new Chart(ctx, {
    type: "radar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Your Skill Proficiency",
          data: data,
          backgroundColor: "rgba(99, 102, 241, 0.25)",
          borderColor: "#6366f1",
          borderWidth: 2,
          pointBackgroundColor: "#06b6d4",
          pointBorderColor: "#fff",
          pointHoverRadius: 6,
        },
        {
          label: "Target Benchmark",
          data: [85, 80, 85, 80, 80],
          backgroundColor: "rgba(255, 255, 255, 0.03)",
          borderColor: "rgba(255, 255, 255, 0.2)",
          borderWidth: 1,
          borderDash: [5, 5],
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: "rgba(255, 255, 255, 0.08)" },
          grid: { color: "rgba(255, 255, 255, 0.08)" },
          pointLabels: {
            color: "#94a3b8",
            font: { family: "Plus Jakarta Sans", size: 11, weight: "600" },
          },
          ticks: {
            display: false,
            backdropColor: "transparent",
            stepSize: 20,
            max: 100,
          },
        },
      },
      plugins: {
        legend: {
          labels: { color: "#cbd5e1", font: { family: "Plus Jakarta Sans" } },
        },
      },
    },
  });
}

function renderRecommendations(recs) {
  const container = document.getElementById("dash-recommendations-list");
  if (!container || !recs || !recs.length) return;

  container.innerHTML = recs
    .map(
      (r) => `
    <div class="p-3 rounded border border-secondary border-opacity-25 bg-dark bg-opacity-50">
      <div class="d-flex justify-content-between">
        <span class="badge ${r.priority === "high" ? "bg-danger" : "bg-warning"} bg-opacity-25 ${
        r.priority === "high" ? "text-danger" : "text-warning"
      } mb-1">
          ${r.priority.toUpperCase()} Priority
        </span>
        <span class="text-muted small">${r.type || "Preparation"}</span>
      </div>
      <div class="fw-bold text-light mb-1">${r.title}</div>
      <p class="text-secondary small mb-2">${r.description || r.action}</p>
      <button class="btn btn-sm btn-outline-custom" data-view="${r.action_view || "coding"}">
        ${r.action_text || "Take Action"}
      </button>
    </div>
  `
    )
    .join("");

  container.querySelectorAll("[data-view]").forEach((b) => {
    b.addEventListener("click", () => switchView(b.dataset.view));
  });
}

// ─────────────────────────────────────────────────────────────
// 4. Resume ATS Analyzer Module
// ─────────────────────────────────────────────────────────────
function setupResume() {
  const fileInput = document.getElementById("resume-file-input");
  const fileNameDisplay = document.getElementById("selected-file-name");
  const form = document.getElementById("resume-upload-form");

  fileInput?.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      fileNameDisplay.textContent = `Selected: ${fileInput.files[0].name}`;
    }
  });

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!api.isAuthenticated()) {
      showToast("Please log in to analyze your resume.", "error");
      return;
    }

    if (!fileInput.files.length) {
      showToast("Please choose a PDF or DOCX file to analyze.", "error");
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const submitBtn = document.getElementById("btn-submit-resume");
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing with AI...';

    try {
      const report = await api.uploadResume(formData);
      showToast("Resume analyzed successfully!", "success");
      renderResumeReport(report);
      loadResumeHistory();
    } catch (err) {
      showToast(err.message || "Failed to analyze resume", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze Resume with Gemini AI';
    }
  });
}

function renderResumeReport(report) {
  document.getElementById("resume-empty-placeholder")?.classList.add("d-none");
  const content = document.getElementById("resume-analysis-content");
  content?.classList.remove("d-none");

  document.getElementById("report-resume-filename").textContent = report.filename || "Resume";
  document.getElementById("report-ats-score").textContent = `${report.ats_score || 80}/100`;

  const ratingBadge = document.getElementById("report-rating-badge");
  if (ratingBadge) {
    ratingBadge.textContent = report.rating || "Good Match";
    ratingBadge.className = `badge ${
      report.ats_score >= 80 ? "bg-success text-success" : report.ats_score >= 60 ? "bg-warning text-warning" : "bg-danger text-danger"
    } bg-opacity-25`;
  }

  // Extracted skills
  const skillsContainer = document.getElementById("report-extracted-skills");
  if (skillsContainer) {
    const skills = report.extracted_skills || [];
    skillsContainer.innerHTML = skills.length
      ? skills.map((s) => `<span class="skill-chip skill-chip-found"><i class="fa-solid fa-check"></i> ${s}</span>`).join("")
      : '<span class="text-muted small">No specific technical keywords detected.</span>';
  }

  // Missing skills
  const missingContainer = document.getElementById("report-missing-skills");
  if (missingContainer) {
    const missing = report.missing_skills || [];
    missingContainer.innerHTML = missing.length
      ? missing.map((s) => `<span class="skill-chip skill-chip-missing"><i class="fa-solid fa-plus"></i> ${s}</span>`).join("")
      : '<span class="text-success small">Great job! All critical high-frequency skills included.</span>';
  }

  // Suggestions
  const suggestionsContainer = document.getElementById("report-suggestions-list");
  if (suggestionsContainer) {
    const suggestions = report.suggestions || [];
    suggestionsContainer.innerHTML = suggestions.length
      ? suggestions.map((s) => `<li class="p-2 rounded bg-dark bg-opacity-50"><i class="fa-solid fa-angle-right text-primary me-2"></i>${s}</li>`).join("")
      : '<li class="text-muted">No additional suggestions. Your resume looks strong!</li>';
  }
}

async function loadResumeHistory() {
  if (!api.isAuthenticated()) return;
  const historyList = document.getElementById("resume-history-list");
  if (!historyList) return;

  try {
    const resumes = await api.getResumeHistory();
    if (!resumes || !resumes.length) {
      historyList.innerHTML = '<div class="text-muted small">No past evaluations found.</div>';
      return;
    }

    historyList.innerHTML = resumes
      .slice(0, 5)
      .map(
        (r) => `
      <div class="p-2 rounded border border-secondary border-opacity-25 d-flex justify-content-between align-items-center">
        <div>
          <div class="fw-semibold text-light">${r.filename}</div>
          <div class="text-muted" style="font-size: 0.75rem;">Score: <strong class="text-success">${r.ats_score}/100</strong></div>
        </div>
        <span class="badge bg-secondary bg-opacity-25 text-light">${r.rating || "Evaluated"}</span>
      </div>
    `
      )
      .join("");
  } catch (err) {
    console.warn("Could not load resume history:", err);
  }
}

// ─────────────────────────────────────────────────────────────
// 5. AI Mock Interview Module
// ─────────────────────────────────────────────────────────────
function setupInterview() {
  document.getElementById("btn-end-interview")?.addEventListener("click", async () => {
    if (!activeInterviewSessionId) return;
    try {
      const summary = await api.endInterview(activeInterviewSessionId);
      showToast("Interview ended! Reviewing results...", "info");
      document.getElementById("interview-select-screen")?.classList.remove("d-none");
      document.getElementById("interview-active-room")?.classList.add("d-none");
      activeInterviewSessionId = null;
      loadDashboard();
    } catch (err) {
      showToast(err.message || "Failed to end interview", "error");
    }
  });

  document.getElementById("btn-submit-answer")?.addEventListener("click", async () => {
    const input = document.getElementById("interview-answer-input");
    const answer = input?.value.trim();
    if (!answer || !activeInterviewSessionId) return;

    appendInterviewMessage("user", answer);
    input.value = "";

    const submitBtn = document.getElementById("btn-submit-answer");
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Grading...';

    try {
      const result = await api.submitInterviewAnswer(activeInterviewSessionId, answer);

      // Render rubric feedback
      renderEvaluationFeedback(result.evaluation);

      // Append next AI question
      if (result.next_question) {
        setTimeout(() => {
          appendInterviewMessage("ai", result.next_question);
        }, 600);
      }
    } catch (err) {
      showToast(err.message || "Failed to submit answer", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit Answer';
    }
  });
}

async function loadInterviewScreen() {
  const container = document.getElementById("company-cards-grid");
  if (!container) return;

  try {
    const companies = await api.getCompanies();
    container.innerHTML = companies
      .map(
        (c) => `
      <div class="col-12 col-md-6 col-lg-3">
        <div class="company-card" data-company-id="${c.id}" data-company-name="${c.name}">
          <div>
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div class="company-logo">
                <img src="${c.logo_url || "https://logo.clearbit.com/" + c.slug + ".com"}" alt="${c.name}" onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png';">
              </div>
              <span class="badge-diff-${c.difficulty || "medium"} text-capitalize">${c.difficulty || "Medium"}</span>
            </div>
            <h5 class="fw-bold mb-1">${c.name}</h5>
            <span class="badge bg-secondary bg-opacity-25 text-secondary mb-2">${c.industry}</span>
            <p class="text-secondary small mb-3" style="min-height: 40px;">${c.description?.slice(0, 85)}...</p>
          </div>
          <button class="btn-primary-custom w-100 justify-content-center btn-start-co-interview" data-company-id="${c.id}" data-company-name="${c.name}">
            <i class="fa-solid fa-play"></i> Start Interview
          </button>
        </div>
      </div>
    `
      )
      .join("");

    container.querySelectorAll(".btn-start-co-interview").forEach((b) => {
      b.addEventListener("click", () => startInterviewSession(b.dataset.companyId, b.dataset.companyName));
    });
  } catch (err) {
    container.innerHTML = '<div class="text-danger">Failed to load company list.</div>';
  }
}

async function startInterviewSession(companyId, companyName) {
  if (!api.isAuthenticated()) {
    showToast("Please log in to start an AI mock interview.", "error");
    return;
  }

  try {
    showToast(`Initializing ${companyName} AI interview room...`, "info");
    const session = await api.startInterview(companyId);
    activeInterviewSessionId = session.session_id;

    document.getElementById("interview-select-screen")?.classList.add("d-none");
    const room = document.getElementById("interview-active-room");
    room?.classList.remove("d-none");

    document.getElementById("active-company-name").textContent = `${companyName} Interview Round`;

    const chatLog = document.getElementById("interview-chat-log");
    chatLog.innerHTML = "";
    appendInterviewMessage("ai", session.question);
  } catch (err) {
    showToast(err.message || "Failed to start interview", "error");
  }
}

function appendInterviewMessage(role, text) {
  const log = document.getElementById("interview-chat-log");
  if (!log) return;

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role === "ai" ? "bubble-ai" : "bubble-user"}`;
  bubble.innerHTML = text.replace(/\n/g, "<br>");
  log.appendChild(bubble);
  log.scrollTop = log.scrollHeight;
}

function renderEvaluationFeedback(evalData) {
  const container = document.getElementById("evaluation-feedback-body");
  if (!container || !evalData) return;

  container.innerHTML = `
    <div class="mb-3 text-center p-3 rounded bg-dark bg-opacity-50 border border-secondary border-opacity-25">
      <div class="display-6 fw-bold text-success">${evalData.score || 75}<span class="fs-6 text-muted">/100</span></div>
      <div class="text-light fw-semibold small mt-1">${evalData.feedback_summary || "Good Response"}</div>
    </div>
    
    <div class="mb-3">
      <div class="d-flex justify-content-between small text-secondary mb-1">
        <span>STAR Method Structure</span>
        <span class="text-info fw-bold">${evalData.star_score || 8}/10</span>
      </div>
      <div class="progress" style="height: 6px; background: rgba(255,255,255,0.08);">
        <div class="progress-bar bg-info" style="width: ${(evalData.star_score || 8) * 10}%;"></div>
      </div>
    </div>

    <div class="mb-3">
      <div class="d-flex justify-content-between small text-secondary mb-1">
        <span>Technical Depth</span>
        <span class="text-primary fw-bold">${evalData.tech_depth_score || 7}/10</span>
      </div>
      <div class="progress" style="height: 6px; background: rgba(255,255,255,0.08);">
        <div class="progress-bar bg-primary" style="width: ${(evalData.tech_depth_score || 7) * 10}%;"></div>
      </div>
    </div>

    <div class="p-2 rounded bg-dark bg-opacity-25 border border-secondary border-opacity-25">
      <div class="text-warning small fw-bold mb-1"><i class="fa-solid fa-lightbulb"></i> Improvement Tip:</div>
      <div class="text-light small">${evalData.improvement_tip || "Emphasize quantitative metrics and business impact in your actions."}</div>
    </div>
  `;
}

// ─────────────────────────────────────────────────────────────
// 6. Coding Practice Arena Module
// ─────────────────────────────────────────────────────────────
function setupCoding() {
  document.getElementById("coding-filter-difficulty")?.addEventListener("change", loadCodingQuestions);
  document.getElementById("coding-filter-category")?.addEventListener("change", loadCodingQuestions);

  // Run Code
  document.getElementById("btn-run-code")?.addEventListener("click", async () => {
    const code = document.getElementById("code-editor").value;
    const outputConsole = document.getElementById("code-console-output");
    outputConsole.innerHTML = '<span class="text-info"><i class="fa-solid fa-spinner fa-spin"></i> Running in Python sandbox...</span>';

    try {
      const res = await api.runCode(code);
      if (res.success) {
        outputConsole.innerHTML = `<span class="text-success"><i class="fa-solid fa-check"></i> Output:</span>\n${res.output || "(Process finished with no output)"}`;
      } else {
        outputConsole.innerHTML = `<span class="text-danger"><i class="fa-solid fa-xmark"></i> Error:</span>\n${res.error || res.output}`;
      }
    } catch (err) {
      outputConsole.innerHTML = `<span class="text-danger">Failed to run code: ${err.message}</span>`;
    }
  });

  // Submit Code
  document.getElementById("btn-submit-code")?.addEventListener("click", async () => {
    if (!currentCodingQuestion) return;
    const code = document.getElementById("code-editor").value;
    const outputConsole = document.getElementById("code-console-output");
    outputConsole.innerHTML = '<span class="text-warning"><i class="fa-solid fa-spinner fa-spin"></i> Evaluating test cases...</span>';

    try {
      const res = await api.submitCode(currentCodingQuestion.id, code);
      if (res.status === "passed") {
        outputConsole.innerHTML = `
          <div class="text-success fw-bold mb-2"><i class="fa-solid fa-circle-check"></i> Accepted (${res.passed}/${res.total} test cases passed)</div>
          <div class="text-secondary small">Runtime: ${res.runtime_ms} ms | Points Awarded!</div>
        `;
        showToast("Solution Accepted! +Points added to your profile.", "success");
        loadDashboard();
      } else {
        outputConsole.innerHTML = `
          <div class="text-danger fw-bold mb-2"><i class="fa-solid fa-circle-xmark"></i> Wrong Answer (${res.passed}/${res.total} test cases passed)</div>
        `;
        showToast("Some test cases failed. Check your logic and try again.", "error");
      }
    } catch (err) {
      outputConsole.innerHTML = `<span class="text-danger">Submission error: ${err.message}</span>`;
    }
  });

  // Bookmark toggle
  document.getElementById("btn-bookmark-question")?.addEventListener("click", async () => {
    if (!currentCodingQuestion) return;
    try {
      const res = await api.toggleBookmark(currentCodingQuestion.id);
      showToast(res.is_bookmarked ? "Question bookmarked!" : "Bookmark removed", "info");
      loadCodingQuestions();
    } catch (err) {
      showToast(err.message || "Failed to bookmark", "error");
    }
  });
}

async function loadCodingArena() {
  await loadCodingQuestions();
}

async function loadCodingQuestions() {
  const listContainer = document.getElementById("coding-questions-list");
  const countBadge = document.getElementById("coding-question-count");
  if (!listContainer) return;

  const diff = document.getElementById("coding-filter-difficulty")?.value;
  const cat = document.getElementById("coding-filter-category")?.value;

  try {
    const data = await api.getCodingQuestions(diff, cat);
    const questions = data.questions || [];
    if (countBadge) countBadge.textContent = `${questions.length} Problems`;

    if (!questions.length) {
      listContainer.innerHTML = '<div class="text-muted small p-2">No problems match filter.</div>';
      return;
    }

    listContainer.innerHTML = questions
      .map(
        (q) => `
      <div class="p-2 rounded border border-secondary border-opacity-25 d-flex justify-content-between align-items-center cursor-pointer question-item-row" data-id="${q.id}" style="cursor: pointer; background: rgba(255,255,255,0.02);">
        <div class="d-flex align-items-center gap-2">
          ${q.status === "passed" ? '<i class="fa-solid fa-circle-check text-success"></i>' : '<i class="fa-regular fa-circle text-muted"></i>'}
          <span class="text-light small fw-semibold">${q.title}</span>
        </div>
        <span class="badge-diff-${q.difficulty}">${q.difficulty}</span>
      </div>
    `
      )
      .join("");

    listContainer.querySelectorAll(".question-item-row").forEach((row) => {
      row.addEventListener("click", () => selectQuestion(row.dataset.id));
    });

    // Select first question if none selected
    if (!currentCodingQuestion && questions.length > 0) {
      selectQuestion(questions[0].id);
    }
  } catch (err) {
    listContainer.innerHTML = '<div class="text-danger small p-2">Failed to load questions.</div>';
  }
}

async function selectQuestion(id) {
  try {
    const q = await api.getCodingQuestion(id);
    currentCodingQuestion = q;

    document.getElementById("problem-title").textContent = q.title;
    document.getElementById("problem-difficulty-badge").textContent = q.difficulty;
    document.getElementById("problem-difficulty-badge").className = `badge-diff-${q.difficulty}`;
    document.getElementById("problem-category-badge").textContent = q.category;
    document.getElementById("problem-description").innerHTML = q.description.replace(/\n/g, "<br>");
    document.getElementById("problem-constraints").textContent = q.constraints ? `Constraints: ${q.constraints}` : "";

    const editor = document.getElementById("code-editor");
    editor.value = q.starter_code || "def solution():\n    # Write your solution here\n    pass\n";

    document.getElementById("code-console-output").innerHTML = '<div class="text-muted">Console output will appear here after running your code...</div>';
  } catch (err) {
    showToast("Failed to load problem details", "error");
  }
}

// ─────────────────────────────────────────────────────────────
// 7. Study Planner Module
// ─────────────────────────────────────────────────────────────
function setupPlanner() {
  document.getElementById("plan-generator-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!api.isAuthenticated()) {
      showToast("Please log in to generate an AI study plan.", "error");
      return;
    }

    const pref = document.getElementById("plan-preferences-input").value.trim();
    const btn = document.getElementById("btn-generate-plan");
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating with Gemini AI...';

    try {
      const plan = await api.generateStudyPlan(pref || "balanced placement roadmap");
      showToast("AI Study Roadmap generated!", "success");
      loadPlanner();
    } catch (err) {
      showToast(err.message || "Failed to generate plan", "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Generate AI Placement Roadmap';
    }
  });
}

async function loadPlanner() {
  if (!api.isAuthenticated()) return;
  const taskContainer = document.getElementById("planner-tasks-container");
  const plansContainer = document.getElementById("planner-saved-plans-list");

  try {
    const plans = await api.getPlans();
    if (!plans || !plans.length) return;

    if (plansContainer) {
      plansContainer.innerHTML = plans
        .map(
          (p) => `
        <div class="p-2 rounded border border-secondary border-opacity-25 d-flex justify-content-between align-items-center">
          <span class="text-light">${p.title}</span>
          <span class="badge bg-secondary">${p.is_active ? "Active" : "Archived"}</span>
        </div>
      `
        )
        .join("");
    }

    const activePlan = plans[0];
    document.getElementById("active-plan-title").textContent = activePlan.title;

    const tasks = await api.getTasks(activePlan.id);
    if (!tasks || !tasks.length) {
      taskContainer.innerHTML = '<div class="text-muted text-center py-4">No tasks in this plan.</div>';
      return;
    }

    const completedCount = tasks.filter((t) => t.is_completed).length;
    const pct = Math.round((completedCount / tasks.length) * 100);
    document.getElementById("active-plan-progress").textContent = `${pct}% Completed`;

    taskContainer.innerHTML = tasks
      .map(
        (t) => `
      <div class="task-item ${t.is_completed ? "completed" : ""}">
        <div class="d-flex align-items-center gap-3">
          <input type="checkbox" class="task-checkbox" data-task-id="${t.id}" ${t.is_completed ? "checked" : ""}>
          <div>
            <div class="text-light fw-semibold small">${t.title}</div>
            <div class="text-muted" style="font-size:0.75rem;"><span class="badge bg-secondary bg-opacity-25 text-light">${t.category}</span> ${t.description || ""}</div>
          </div>
        </div>
        <span class="badge ${t.priority === "high" ? "bg-danger" : "bg-secondary"} bg-opacity-25 text-light small">${t.priority}</span>
      </div>
    `
      )
      .join("");

    taskContainer.querySelectorAll(".task-checkbox").forEach((cb) => {
      cb.addEventListener("change", async () => {
        try {
          await api.toggleTask(cb.dataset.taskId, cb.checked);
          loadPlanner();
        } catch (err) {
          showToast("Failed to update task", "error");
        }
      });
    });
  } catch (err) {
    console.warn("Planner load error:", err);
  }
}

// ─────────────────────────────────────────────────────────────
// 8. AI Mentor Chat Module
// ─────────────────────────────────────────────────────────────
function setupChat() {
  const sendBtn = document.getElementById("btn-send-mentor-chat");
  const input = document.getElementById("mentor-chat-input");
  const modeSelect = document.getElementById("chat-mode-selector");

  const send = async () => {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";

    appendMentorMessage("user", text);

    const typingBubble = appendTypingIndicator();

    try {
      const mode = modeSelect?.value || "placement";
      const reply = await api.sendChatMessage(text, mode);
      typingBubble.remove();
      appendMentorMessage("ai", reply.response || reply.message || "I am here to guide your placement journey.");
    } catch (err) {
      typingBubble.remove();
      appendMentorMessage("ai", `Error: ${err.message || "Failed to reach AI mentor. Check Gemini API key in .env"}`);
    }
  };

  sendBtn?.addEventListener("click", send);
  input?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") send();
  });

  // Quick prompt chips
  document.querySelectorAll(".quick-prompt-btn").forEach((b) => {
    b.addEventListener("click", () => {
      input.value = b.dataset.prompt;
      send();
    });
  });
}

function appendMentorMessage(role, text) {
  const log = document.getElementById("mentor-chat-log");
  if (!log) return;

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role === "ai" ? "bubble-ai" : "bubble-user"}`;
  bubble.innerHTML = text.replace(/\n/g, "<br>");
  log.appendChild(bubble);
  log.scrollTop = log.scrollHeight;
}

function appendTypingIndicator() {
  const log = document.getElementById("mentor-chat-log");
  const bubble = document.createElement("div");
  bubble.className = "chat-bubble bubble-ai";
  bubble.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> Gemini AI is typing...';
  log.appendChild(bubble);
  log.scrollTop = log.scrollHeight;
  return bubble;
}

// ─────────────────────────────────────────────────────────────
// 9. Leaderboard Module
// ─────────────────────────────────────────────────────────────
async function loadLeaderboard() {
  const tbody = document.getElementById("leaderboard-table-body");
  if (!tbody) return;

  try {
    const users = await api.getLeaderboard();
    tbody.innerHTML = (users || [])
      .map(
        (u, idx) => `
      <tr>
        <td class="fw-bold text-center" style="width: 60px;">
          ${idx === 0 ? "🥇" : idx === 1 ? "🥈" : idx === 2 ? "🥉" : `#${idx + 1}`}
        </td>
        <td>
          <div class="d-flex align-items-center gap-2">
            <div style="width:28px; height:28px; border-radius:50%; background: #334155; display:flex; align-items:center; justify-content:center; font-size:0.8rem; font-weight:700;">
              ${u.full_name ? u.full_name[0].toUpperCase() : "U"}
            </div>
            <span class="fw-semibold text-light">${u.full_name}</span>
          </div>
        </td>
        <td class="text-info fw-bold">${u.total_score || 0} pts</td>
        <td>${u.solved_count || 0}</td>
        <td><i class="fa-solid fa-fire text-warning me-1"></i> ${u.streak_days || 1}d</td>
        <td>
          <span class="badge bg-success bg-opacity-25 text-success">
            ${(u.total_score || 0) > 100 ? "Ready for L4" : "In Training"}
          </span>
        </td>
      </tr>
    `
      )
      .join("");
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-muted text-center py-3">Could not load leaderboard.</td></tr>';
  }
}

// ─────────────────────────────────────────────────────────────
// 10. Admin Dashboard Module
// ─────────────────────────────────────────────────────────────
async function loadAdminDashboard() {
  const statsRow = document.getElementById("admin-stats-row");
  const usersTbody = document.getElementById("admin-users-table");
  const companiesTbody = document.getElementById("admin-companies-table");

  try {
    const [stats, users, companies] = await Promise.all([
      api.getAdminStats(),
      api.getAdminUsers(),
      api.getAdminCompanies(),
    ]);

    if (statsRow) {
      statsRow.innerHTML = `
        <div class="col-6 col-md-3">
          <div class="glass-panel p-3 text-center">
            <div class="stat-value text-primary">${stats.total_users || 0}</div>
            <div class="stat-label">Total Users</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="glass-panel p-3 text-center">
            <div class="stat-value text-success">${stats.total_submissions || 0}</div>
            <div class="stat-label">Code Submissions</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="glass-panel p-3 text-center">
            <div class="stat-value text-warning">${stats.total_interviews || 0}</div>
            <div class="stat-label">Mock Interviews</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="glass-panel p-3 text-center">
            <div class="stat-value text-info">${stats.total_companies || 0}</div>
            <div class="stat-label">Active Companies</div>
          </div>
        </div>
      `;
    }

    if (usersTbody) {
      usersTbody.innerHTML = (users || [])
        .map(
          (u) => `
        <tr>
          <td class="text-light">${u.full_name}</td>
          <td class="text-secondary">${u.email}</td>
          <td><span class="badge ${u.is_admin ? "bg-danger" : "bg-primary"} bg-opacity-25 ${u.is_admin ? "text-danger" : "text-primary"}">${u.is_admin ? "Admin" : "Student"}</span></td>
          <td class="text-info">${u.total_score || 0}</td>
        </tr>
      `
        )
        .join("");
    }

    if (companiesTbody) {
      companiesTbody.innerHTML = (companies || [])
        .map(
          (c) => `
        <tr>
          <td class="text-light fw-semibold">${c.name}</td>
          <td class="text-secondary">${c.industry}</td>
          <td><span class="badge-diff-${c.difficulty}">${c.difficulty}</span></td>
        </tr>
      `
        )
        .join("");
    }
  } catch (err) {
    console.error("Admin portal load error:", err);
  }
}
