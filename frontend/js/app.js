/**
 * PrepPilot AI — Main Application Controller
 * Handles SPA navigation, state management, charts, and module integrations.
 */

import { api } from "./api.js";

// Global State
let radarChartInstance = null;
let currentCodingQuestion = null;
let activeInterviewSessionId = null;
let selectedCompanyFilter = "all";

// Company badge styling map
function getCompanyBadgeClass(companyName) {
  const norm = (companyName || "").toLowerCase();
  if (norm.includes("google")) return "badge-company-google";
  if (norm.includes("amazon")) return "badge-company-amazon";
  if (norm.includes("microsoft")) return "badge-company-microsoft";
  if (norm.includes("meta") || norm.includes("facebook")) return "badge-company-meta";
  if (norm.includes("apple")) return "badge-company-apple";
  if (norm.includes("netflix")) return "badge-company-netflix";
  if (norm.includes("goldman")) return "badge-company-goldman";
  if (norm.includes("uber")) return "badge-company-uber";
  if (norm.includes("adobe")) return "badge-company-adobe";
  if (norm.includes("atlassian")) return "badge-company-atlassian";
  if (norm.includes("oracle")) return "badge-company-oracle";
  if (norm.includes("walmart")) return "badge-company-walmart";
  if (norm.includes("deloitte")) return "badge-company-deloitte";
  if (norm.includes("accenture")) return "badge-company-accenture";
  if (norm.includes("tcs")) return "badge-company-tcs";
  if (norm.includes("infosys")) return "badge-company-infosys";
  return "badge-company-general";
}

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
    if (!el.classList.contains(".nav-pill-btn")) {
      el.addEventListener("click", (e) => {
        const target = el.dataset.view;
        if (target) {
          e.preventDefault();
          switchView(target);
        }
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
// 2. Authentication Management (Navbar & Dashboard Hero)
// ─────────────────────────────────────────────────────────────
function setupAuth() {
  // Modal Tab switching
  const tabLogin = document.getElementById("tab-btn-login");
  const tabRegister = document.getElementById("tab-btn-register");
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");

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

  // Dashboard Hero Tab switching
  const heroTabLogin = document.getElementById("hero-tab-login");
  const heroTabRegister = document.getElementById("hero-tab-register");
  const heroFormLogin = document.getElementById("hero-form-login");
  const heroFormRegister = document.getElementById("hero-form-register");

  heroTabLogin?.addEventListener("click", () => {
    heroTabLogin.classList.add("active");
    heroTabRegister.classList.remove("active");
    heroFormLogin.classList.remove("d-none");
    heroFormRegister.classList.add("d-none");
  });

  heroTabRegister?.addEventListener("click", () => {
    heroTabRegister.classList.add("active");
    heroTabLogin.classList.remove("active");
    heroFormRegister.classList.remove("d-none");
    heroFormLogin.classList.add("d-none");
  });

  // Navbar button openers
  document.getElementById("btn-open-login")?.addEventListener("click", () => {
    tabLogin?.click();
  });
  document.getElementById("btn-open-register")?.addEventListener("click", () => {
    tabRegister?.click();
  });

  // Modal Login Submit
  formLogin?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    await doLogin(email, password, true);
  });

  // Hero Login Submit
  heroFormLogin?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("hero-login-email").value.trim();
    const password = document.getElementById("hero-login-password").value;
    await doLogin(email, password, false);
  });

  // Modal Register Submit
  formRegister?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    await doRegister(name, email, password, true);
  });

  // Hero Register Submit
  heroFormRegister?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("hero-reg-name").value.trim();
    const email = document.getElementById("hero-reg-email").value.trim();
    const password = document.getElementById("hero-reg-password").value;
    await doRegister(name, email, password, false);
  });

  // 1-Click Demo Buttons
  const handleDemoStudent = async () => {
    await doLogin("student@preppilot.com", "Student#2026", true);
  };
  const handleDemoAdmin = async () => {
    await doLogin("admin@preppilot.com", "PrepPilot#2026", true);
  };

  document.getElementById("btn-quick-student-login")?.addEventListener("click", handleDemoStudent);
  document.getElementById("hero-quick-student-login")?.addEventListener("click", handleDemoStudent);

  document.getElementById("btn-quick-admin-login")?.addEventListener("click", handleDemoAdmin);
  document.getElementById("hero-quick-admin-login")?.addEventListener("click", handleDemoAdmin);
}

async function doLogin(email, password, closeModal = false) {
  try {
    const data = await api.login(email, password);
    showToast(`Welcome back, ${data.user.full_name}!`, "success");
    if (closeModal) {
      bootstrap.Modal.getInstance(document.getElementById("authModal"))?.hide();
    }
    updateAuthUI(data.user);
    loadDashboard();
  } catch (err) {
    showToast(err.message || "Login failed", "error");
  }
}

async function doRegister(name, email, password, closeModal = false) {
  try {
    await api.register(name, email, password);
    showToast("Account created successfully! Logging you in...", "success");
    await doLogin(email, password, closeModal);
  } catch (err) {
    showToast(err.message || "Registration failed", "error");
  }
}

function updateAuthUI(user) {
  const container = document.getElementById("auth-state-container");
  const heroCard = document.getElementById("dash-auth-hero");
  const loggedInBanner = document.getElementById("dash-logged-in-banner");
  const streakPill = document.getElementById("streak-days-val");
  const scorePill = document.getElementById("user-score-val");
  const greeting = document.getElementById("dash-greeting");
  const adminBtn = document.getElementById("nav-btn-admin");

  if (user) {
    // Show logged-in elements
    if (heroCard) heroCard.classList.add("d-none");
    if (loggedInBanner) {
      loggedInBanner.classList.remove("d-none");
      loggedInBanner.classList.add("d-flex");
    }
    if (greeting) greeting.textContent = `Welcome back, ${user.full_name}!`;
    if (streakPill) streakPill.textContent = user.streak_days || 5;
    if (scorePill) scorePill.textContent = user.total_score || 180;

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
    // Show unauthenticated hero card on dashboard
    if (heroCard) heroCard.classList.remove("d-none");
    if (loggedInBanner) {
      loggedInBanner.classList.add("d-none");
      loggedInBanner.classList.remove("d-flex");
    }
    adminBtn?.classList.add("d-none");

    container.innerHTML = `
      <button class="btn btn-sm btn-outline-custom" id="btn-open-login" data-bs-toggle="modal" data-bs-target="#authModal" data-auth-tab="login">
        <i class="fa-solid fa-arrow-right-to-bracket"></i> Sign In
      </button>
      <button class="btn-primary-custom btn-sm py-2 px-3" id="btn-open-register" data-bs-toggle="modal" data-bs-target="#authModal" data-auth-tab="register">
        <i class="fa-solid fa-user-plus"></i> Register
      </button>
    `;

    document.getElementById("btn-open-login")?.addEventListener("click", () => {
      document.getElementById("tab-btn-login")?.click();
    });
    document.getElementById("btn-open-register")?.addEventListener("click", () => {
      document.getElementById("tab-btn-register")?.click();
    });
  }
}

// ─────────────────────────────────────────────────────────────
// 3. Dashboard Module
// ─────────────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const [stats, charts, recs] = await Promise.all([
      api.getDashboardStats().catch(() => ({
        readiness_score: 72,
        ats_score: 82,
        avg_interview_score: 78,
        unique_solved: 14,
        total_questions: 26,
      })),
      api.getDashboardCharts().catch(() => null),
      api.getDashboardRecommendations().catch(() => null),
    ]);

    // Update Readiness Gauge
    const readinessScore = stats.readiness_score || 72;
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
    if (resumeScoreEl) resumeScoreEl.innerHTML = `${stats.ats_score || 82}<span class="fs-6 text-muted">/100</span>`;

    const interviewScoreEl = document.getElementById("dash-interview-score");
    if (interviewScoreEl) interviewScoreEl.innerHTML = `${Math.round(stats.avg_interview_score || 78)}<span class="fs-6 text-muted">%</span>`;

    const problemsSolvedEl = document.getElementById("dash-problems-solved");
    if (problemsSolvedEl) {
      problemsSolvedEl.innerHTML = `${stats.unique_solved || 14}<span class="fs-6 text-muted">/${stats.total_questions || 26}</span>`;
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
    { name: "DSA & Algorithms", score: 78 },
    { name: "System Design", score: 65 },
    { name: "Core CS (OS/DBMS/CN)", score: 82 },
    { name: "Behavioral & STAR", score: 75 },
    { name: "Problem Solving Speed", score: 70 },
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
  if (!container) return;

  const list = recs && recs.length ? recs : [
    {
      priority: "high",
      type: "Google Track",
      title: "Master Google DSA: Two Sum & Median of Two Arrays",
      description: "Top tested algorithmic problem on Google campus interview rounds.",
      action_view: "coding",
      action_text: "Practice Google Track",
    },
    {
      priority: "high",
      type: "Amazon Track",
      title: "Practice Amazon Knapsack & Maximum Subarray",
      description: "Essential Dynamic Programming questions frequently asked in AWS OA.",
      action_view: "coding",
      action_text: "Practice Amazon Track",
    },
    {
      priority: "medium",
      type: "Resume ATS",
      title: "Analyze Resume for ATS Keyword Fit",
      description: "Extract missing technical keywords for Deloitte, TCS, and Microsoft roles.",
      action_view: "resume",
      action_text: "Scan Resume",
    },
  ];

  container.innerHTML = list
    .map(
      (r) => `
    <div class="p-3 rounded border border-secondary border-opacity-25 bg-dark bg-opacity-50">
      <div class="d-flex justify-content-between">
        <span class="badge ${r.priority === "high" ? "bg-danger" : "bg-warning"} bg-opacity-25 ${
        r.priority === "high" ? "text-danger" : "text-warning"
      } mb-1">
          ${(r.priority || "high").toUpperCase()} Priority
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
      showToast("Analyzing in Guest Mode. Log in anytime to save this report to your profile.", "info");
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
  document.getElementById("report-ats-score").textContent = `${report.ats_score || 85}/100`;

  const ratingBadge = document.getElementById("report-rating-badge");
  if (ratingBadge) {
    ratingBadge.textContent = report.rating || "Strong Fit";
    ratingBadge.className = `badge ${
      report.ats_score >= 80 ? "bg-success text-success" : report.ats_score >= 60 ? "bg-warning text-warning" : "bg-danger text-danger"
    } bg-opacity-25`;
  }

  // Extracted skills
  const skillsContainer = document.getElementById("report-extracted-skills");
  if (skillsContainer) {
    const skills = (report.skills && report.skills.length ? report.skills : report.extracted_skills) || ["Python", "FastAPI", "SQL", "Docker", "Git", "Algorithms"];
    skillsContainer.innerHTML = skills
      .map((s) => `<span class="skill-chip skill-chip-found"><i class="fa-solid fa-check"></i> ${s}</span>`)
      .join("");
  }

  // Missing skills
  const missingContainer = document.getElementById("report-missing-skills");
  if (missingContainer) {
    const missing = report.missing_skills || ["Kubernetes", "Redis", "System Design Metrics"];
    missingContainer.innerHTML = missing
      .map((s) => `<span class="skill-chip skill-chip-missing"><i class="fa-solid fa-plus"></i> ${s}</span>`)
      .join("");
  }

  // Suggestions
  const suggestionsContainer = document.getElementById("report-suggestions-list");
  if (suggestionsContainer) {
    const suggestions = report.suggestions || [
      "Quantify your accomplishments (e.g. 'Reduced API latency by 35% using caching').",
      "Include cloud deployment keywords (AWS, Docker, CI/CD).",
      "Ensure bullet points follow the Google XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]'.",
    ];
    suggestionsContainer.innerHTML = suggestions
      .map((s) => `<li class="p-2 rounded bg-dark bg-opacity-50"><i class="fa-solid fa-angle-right text-primary me-2"></i>${s}</li>`)
      .join("");
  }
}

async function loadResumeHistory() {
  const historyList = document.getElementById("resume-history-list");
  if (!historyList) return;

  try {
    const resumes = await api.getResumeHistory();
    if (!resumes || !resumes.length) {
      historyList.innerHTML = '<div class="text-muted small">No past evaluations found. Upload above to scan!</div>';
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
    historyList.innerHTML = '<div class="text-muted small">Log in to view past resume scans.</div>';
  }
}

// ─────────────────────────────────────────────────────────────
// 5. AI Mock Interview Module
// ─────────────────────────────────────────────────────────────
function setupInterview() {
  document.getElementById("btn-end-interview")?.addEventListener("click", async () => {
    if (!activeInterviewSessionId) return;
    try {
      await api.endInterview(activeInterviewSessionId);
      showToast("Interview round completed! Reviewing evaluation report...", "info");
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
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Evaluating...';

    try {
      const result = await api.submitInterviewAnswer(activeInterviewSessionId, answer);
      renderEvaluationFeedback(result.evaluation);

      if (result.next_question) {
        setTimeout(() => {
          appendInterviewMessage("ai", result.next_question);
        }, 500);
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
    showToast("Please sign in or use Demo Student to start an interview session.", "error");
    document.getElementById("btn-open-login")?.click();
    return;
  }

  try {
    showToast(`Initializing ${companyName} AI interview room...`, "info");
    const session = await api.startInterview(companyId);
    activeInterviewSessionId = session.session_id;

    document.getElementById("interview-select-screen")?.classList.add("d-none");
    const room = document.getElementById("interview-active-room");
    room?.classList.remove("d-none");

    document.getElementById("active-company-name").textContent = `${companyName} Live Technical & HR Round`;

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
      <div class="display-6 fw-bold text-success">${evalData.score || 78}<span class="fs-6 text-muted">/100</span></div>
      <div class="text-light fw-semibold small mt-1">${evalData.feedback_summary || "Good Structured Response"}</div>
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
      <div class="text-light small">${evalData.improvement_tip || "Emphasize quantitative business metrics in your Result section."}</div>
    </div>
  `;
}

// ─────────────────────────────────────────────────────────────
// 6. Coding Practice Arena Module (Multi-Language LeetCode-style)
// ─────────────────────────────────────────────────────────────
const LANGUAGE_BOILERPLATES = {
  python: `# Python 3 Solution
import sys

def main():
    input_data = sys.stdin.read().strip()
    if not input_data:
        return
    # Write your solution logic here

if __name__ == '__main__':
    main()
`,
  javascript: `// JavaScript (Node.js) Solution
const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8').trim();
    if (!input) return;
    // Write your solution logic here
}

main();
`,
  cpp: `// C++ (g++ 17) Solution
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    // Write your solution logic here
    return 0;
}
`,
  c: `/* C (gcc 11) Solution */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // Read input and output result
    return 0;
}
`,
  java: `// Java (OpenJDK) Solution
import java.util.*;
import java.io.*;

public class Solution {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        // Write your solution logic here
    }
}
`,
  php: `<?php
// PHP Solution
$input = trim(file_get_contents("php://stdin"));
// Write your solution logic here
`,
};

function setupCoding() {
  // Company pills listener
  const pills = document.querySelectorAll("#coding-company-pills .company-pill");
  pills.forEach((pill) => {
    pill.addEventListener("click", () => {
      pills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      selectedCompanyFilter = pill.dataset.company || "all";
      const label = document.getElementById("current-company-filter-label");
      if (label) label.textContent = selectedCompanyFilter === "all" ? "All Companies" : selectedCompanyFilter;
      loadCodingQuestions();
    });
  });

  // Dropdown filters
  document.getElementById("coding-filter-difficulty")?.addEventListener("change", loadCodingQuestions);
  document.getElementById("coding-filter-category")?.addEventListener("change", loadCodingQuestions);

  // Language selector
  const langSelect = document.getElementById("code-language-select");
  if (langSelect) {
    langSelect.addEventListener("change", () => {
      const selectedLang = langSelect.value;
      const editor = document.getElementById("code-editor");
      if (editor) {
        if (selectedLang === "python" && currentCodingQuestion?.starter_code) {
          editor.value = currentCodingQuestion.starter_code;
        } else {
          editor.value = LANGUAGE_BOILERPLATES[selectedLang] || "";
        }
      }
      showToast(`Switched editor to ${langSelect.options[langSelect.selectedIndex].text}`, "info");
    });
  }

  // Reset code button
  document.getElementById("btn-reset-code")?.addEventListener("click", () => {
    const lang = document.getElementById("code-language-select")?.value || "python";
    const editor = document.getElementById("code-editor");
    if (editor) {
      if (lang === "python" && currentCodingQuestion?.starter_code) {
        editor.value = currentCodingQuestion.starter_code;
      } else {
        editor.value = LANGUAGE_BOILERPLATES[lang] || "";
      }
      showToast("Starter code reset", "info");
    }
  });

  // Tab key indentation support for code editor
  const codeEditor = document.getElementById("code-editor");
  if (codeEditor) {
    codeEditor.addEventListener("keydown", (e) => {
      if (e.key === "Tab") {
        e.preventDefault();
        const start = codeEditor.selectionStart;
        const end = codeEditor.selectionEnd;
        codeEditor.value = codeEditor.value.substring(0, start) + "    " + codeEditor.value.substring(end);
        codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
      }
    });
  }

  // Run Code
  document.getElementById("btn-run-code")?.addEventListener("click", async () => {
    const code = document.getElementById("code-editor").value;
    const lang = document.getElementById("code-language-select")?.value || "python";
    const outputConsole = document.getElementById("code-console-output");
    outputConsole.innerHTML = `<span class="text-info"><i class="fa-solid fa-spinner fa-spin"></i> Executing in ${lang.toUpperCase()} sandbox...</span>`;

    try {
      const res = await api.runCode(code, lang);
      if (res.success) {
        outputConsole.innerHTML = `
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="text-success fw-bold"><i class="fa-solid fa-check"></i> Finished Successfully</span>
            <span class="badge bg-secondary">${res.runtime_ms} ms</span>
          </div>
          <pre class="mb-0 text-light" style="font-family: var(--font-code); white-space: pre-wrap;">${res.output || "(Process exited cleanly with no output)"}</pre>
        `;
      } else {
        outputConsole.innerHTML = `
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="text-danger fw-bold"><i class="fa-solid fa-xmark"></i> Runtime/Execution Error</span>
            <span class="badge bg-danger">${res.runtime_ms} ms</span>
          </div>
          <pre class="mb-0 text-danger" style="font-family: var(--font-code); white-space: pre-wrap;">${res.error || res.output || "Execution failed"}</pre>
        `;
      }
    } catch (err) {
      outputConsole.innerHTML = `<span class="text-danger">Failed to run code: ${err.message}</span>`;
    }
  });

  // Submit Code
  document.getElementById("btn-submit-code")?.addEventListener("click", async () => {
    if (!currentCodingQuestion) return;

    const code = document.getElementById("code-editor").value;
    const lang = document.getElementById("code-language-select")?.value || "python";
    const outputConsole = document.getElementById("code-console-output");
    outputConsole.innerHTML = `<span class="text-warning"><i class="fa-solid fa-spinner fa-spin"></i> Running ${lang.toUpperCase()} against test suite...</span>`;

    try {
      const res = await api.submitCode(currentCodingQuestion.id, code, lang);
      
      let testcaseHtml = "";
      if (res.results && res.results.length) {
        testcaseHtml = `
          <div class="mt-3 border-top border-secondary border-opacity-25 pt-2">
            <div class="small fw-bold text-muted mb-2">Test Case Results:</div>
            <div class="d-flex flex-column gap-2">
              ${res.results.map((tc) => `
                <div class="p-2 rounded bg-dark bg-opacity-75 border ${tc.passed ? "border-success border-opacity-50" : "border-danger border-opacity-50"} small">
                  <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="fw-bold ${tc.passed ? "text-success" : "text-danger"}">
                      <i class="fa-solid ${tc.passed ? "fa-circle-check" : "fa-circle-xmark"}"></i> Test Case #${tc.test_case}
                    </span>
                    <span class="text-muted">${tc.runtime_ms} ms</span>
                  </div>
                  <div class="text-secondary"><strong>Input:</strong> <code>${tc.input || "none"}</code></div>
                  <div class="text-secondary"><strong>Expected:</strong> <code>${tc.expected}</code></div>
                  <div class="${tc.passed ? "text-success" : "text-danger"}"><strong>Actual:</strong> <code>${tc.actual || "(empty)"}</code></div>
                  ${tc.error ? `<div class="text-danger mt-1"><strong>Error:</strong> <code>${tc.error}</code></div>` : ""}
                </div>
              `).join("")}
            </div>
          </div>
        `;
      }

      if (res.status === "passed") {
        outputConsole.innerHTML = `
          <div class="d-flex justify-content-between align-items-center mb-2">
            <div class="text-success fw-bold fs-6"><i class="fa-solid fa-circle-check"></i> Accepted (${res.passed}/${res.total} Test Cases Passed)</div>
            <span class="badge bg-success bg-opacity-25 text-success">Total: ${res.runtime_ms} ms</span>
          </div>
          <div class="text-secondary small">Language: <span class="text-info fw-semibold">${lang.toUpperCase()}</span> | Points Awarded to your profile!</div>
          ${testcaseHtml}
        `;
        showToast("Solution Accepted! Great job!", "success");
        loadDashboard();
        loadCodingQuestions();
        loadLeaderboard();
      } else {
        outputConsole.innerHTML = `
          <div class="d-flex justify-content-between align-items-center mb-2">
            <div class="text-danger fw-bold fs-6"><i class="fa-solid fa-circle-xmark"></i> Wrong Answer (${res.passed}/${res.total} Passed)</div>
            <span class="badge bg-danger bg-opacity-25 text-danger">Total: ${res.runtime_ms} ms</span>
          </div>
          <div class="text-secondary small">Language: <span class="text-warning fw-semibold">${lang.toUpperCase()}</span> &bull; Check output below:</div>
          ${testcaseHtml}
        `;
        showToast("Some test cases failed. Inspect details in the console.", "error");
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
    const data = await api.getCodingQuestions(diff, cat, selectedCompanyFilter);
    const questions = data.questions || [];
    if (countBadge) countBadge.textContent = `${questions.length} Problems`;

    if (!questions.length) {
      listContainer.innerHTML = `
        <div class="text-center py-4 text-muted small">
          <i class="fa-solid fa-filter-circle-xmark fs-4 mb-2"></i>
          <div>No problems match the current filter.</div>
          <button class="btn btn-sm btn-outline-custom mt-2" onclick="document.querySelector('#coding-company-pills .company-pill').click()">Reset Filters</button>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = questions
      .map(
        (q) => `
      <div class="p-2 rounded border border-secondary border-opacity-25 d-flex justify-content-between align-items-center cursor-pointer question-item-row" data-id="${q.id}" style="cursor: pointer; background: rgba(255,255,255,0.02);">
        <div class="d-flex align-items-center gap-2" style="max-width: 65%;">
          ${q.solved ? '<i class="fa-solid fa-circle-check text-success"></i>' : '<i class="fa-regular fa-circle text-muted"></i>'}
          <span class="text-light small fw-semibold text-truncate">${q.title}</span>
        </div>
        <div class="d-flex align-items-center gap-1">
          <span class="badge-company ${getCompanyBadgeClass(q.company)}">${q.company || "General"}</span>
          <span class="badge-diff-${q.difficulty}">${q.difficulty}</span>
        </div>
      </div>
    `
      )
      .join("");

    listContainer.querySelectorAll(".question-item-row").forEach((row) => {
      row.addEventListener("click", () => selectQuestion(row.dataset.id));
    });

    // Select first question if none selected or if current question isn't in filtered list
    if (questions.length > 0) {
      if (!currentCodingQuestion || !questions.some((q) => q.id === currentCodingQuestion.id)) {
        selectQuestion(questions[0].id);
      }
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
    
    // Company badge
    const coBadge = document.getElementById("problem-company-badge");
    if (coBadge) {
      coBadge.textContent = q.company || "General";
      coBadge.className = `badge-company ${getCompanyBadgeClass(q.company)}`;
    }

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
      showToast("Please sign in to generate and save your AI study plan.", "error");
      document.getElementById("btn-open-login")?.click();
      return;
    }

    const pref = document.getElementById("plan-preferences-input").value.trim();
    const btn = document.getElementById("btn-generate-plan");
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating Roadmap with Gemini AI...';

    try {
      await api.generateStudyPlan(pref || "balanced placement roadmap for Google and Amazon");
      showToast("AI Study Roadmap generated successfully!", "success");
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
  const taskContainer = document.getElementById("planner-tasks-container");
  const plansContainer = document.getElementById("planner-saved-plans-list");

  try {
    const plans = await api.getPlans();
    if (!plans || !plans.length) {
      // Show default preview tasks
      renderDefaultPlannerTasks();
      return;
    }

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
      renderDefaultPlannerTasks();
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
    renderDefaultPlannerTasks();
  }
}

function renderDefaultPlannerTasks() {
  const taskContainer = document.getElementById("planner-tasks-container");
  if (!taskContainer) return;

  const defaultTasks = [
    { title: "Day 1: Solve Google Two Sum and Amazon Kadane's Algorithm", category: "DSA", priority: "high", completed: true },
    { title: "Day 2: Review STAR Method for Behavioral Rounds (Amazon LP)", category: "HR", priority: "medium", completed: true },
    { title: "Day 3: Practice Valid Parentheses & Linked List Reversal (Microsoft)", category: "DSA", priority: "high", completed: true },
    { title: "Day 4: Run AI Mock Interview simulation for Google L4", category: "Interview", priority: "high", completed: true },
    { title: "Day 5: 0/1 Knapsack Problem & Dynamic Programming Patterns", category: "DSA", priority: "high", completed: false },
    { title: "Day 6: Scan Resume via ATS Analyzer and incorporate keywords", category: "Resume", priority: "medium", completed: false },
    { title: "Day 7: Final Comprehensive Mock Assessment & Speed Practice", category: "DSA", priority: "high", completed: false },
  ];

  taskContainer.innerHTML = defaultTasks
    .map(
      (t) => `
    <div class="task-item ${t.completed ? "completed" : ""}">
      <div class="d-flex align-items-center gap-3">
        <input type="checkbox" class="task-checkbox" ${t.completed ? "checked" : ""}>
        <div>
          <div class="text-light fw-semibold small">${t.title}</div>
          <div class="text-muted" style="font-size:0.75rem;"><span class="badge bg-secondary bg-opacity-25 text-light">${t.category}</span> Recommended placement sprint task</div>
        </div>
      </div>
      <span class="badge ${t.priority === "high" ? "bg-danger" : "bg-secondary"} bg-opacity-25 text-light small">${t.priority}</span>
    </div>
  `
    )
    .join("");
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
      appendMentorMessage("ai", `Error: ${err.message || "Failed to reach AI mentor. Please check your Gemini API key in .env"}`);
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
// 9. Leaderboard Module (Podium + Gamified Rankings + Filters)
// ─────────────────────────────────────────────────────────────
let leaderboardCache = [];

async function loadLeaderboard() {
  const tbody = document.getElementById("leaderboard-table-body");
  const podium = document.getElementById("leaderboard-podium");
  if (!tbody) return;

  try {
    const users = await api.getLeaderboard();
    leaderboardCache = users || [];

    // Setup filter listeners once
    setupLeaderboardFilters();

    // Render podium
    renderLeaderboardPodium(leaderboardCache.slice(0, 3));

    // Render my rank banner
    renderMyRankBanner(leaderboardCache);

    // Render table
    renderLeaderboardTable(leaderboardCache);

    // Update header stats
    const topScoreEl = document.getElementById("lb-top-score");
    if (topScoreEl && leaderboardCache.length > 0) {
      topScoreEl.textContent = `${leaderboardCache[0].total_score} pts`;
    }
    const contendersEl = document.getElementById("lb-total-contenders");
    if (contendersEl) {
      contendersEl.textContent = `${leaderboardCache.length}+`;
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-muted text-center py-3">Could not load leaderboard data.</td></tr>';
  }
}

function renderLeaderboardPodium(top3) {
  const podium = document.getElementById("leaderboard-podium");
  if (!podium || !top3.length) return;

  const first = top3[0];
  const second = top3.length > 1 ? top3[1] : null;
  const third = top3.length > 2 ? top3[2] : null;

  let html = "";

  // Rank 2 (Silver)
  if (second) {
    html += `
      <div class="podium-card rank-2">
        <div class="podium-avatar-wrapper">
          <div class="podium-avatar">${second.full_name ? second.full_name[0] : "2"}</div>
          <span class="podium-badge">🥈 2nd</span>
        </div>
        <div class="fw-bold text-light text-truncate">${second.full_name}</div>
        <div class="text-muted small">${second.college || "Campus Leader"}</div>
        <div class="podium-score">${second.total_score} pts</div>
        <div class="small text-secondary mt-1">
          <i class="fa-solid fa-fire text-warning"></i> ${second.streak_days}d streak &bull; ${second.solved_count} solved
        </div>
      </div>
    `;
  }

  // Rank 1 (Gold Champion)
  if (first) {
    html += `
      <div class="podium-card rank-1">
        <div class="podium-crown"><i class="fa-solid fa-crown text-warning"></i></div>
        <div class="podium-avatar-wrapper">
          <div class="podium-avatar">${first.full_name ? first.full_name[0] : "1"}</div>
          <span class="podium-badge">🥇 Champion</span>
        </div>
        <div class="fw-bold text-light fs-5 text-truncate">${first.full_name}</div>
        <div class="text-warning small fw-semibold">${first.college || "Campus Champion"}</div>
        <div class="podium-score">${first.total_score} pts</div>
        <div class="small text-secondary mt-1">
          <i class="fa-solid fa-fire text-danger"></i> ${first.streak_days}d streak &bull; ${first.solved_count} solved
        </div>
      </div>
    `;
  }

  // Rank 3 (Bronze)
  if (third) {
    html += `
      <div class="podium-card rank-3">
        <div class="podium-avatar-wrapper">
          <div class="podium-avatar">${third.full_name ? third.full_name[0] : "3"}</div>
          <span class="podium-badge">🥉 3rd</span>
        </div>
        <div class="fw-bold text-light text-truncate">${third.full_name}</div>
        <div class="text-muted small">${third.college || "Campus Contender"}</div>
        <div class="podium-score">${third.total_score} pts</div>
        <div class="small text-secondary mt-1">
          <i class="fa-solid fa-fire text-warning"></i> ${third.streak_days}d streak &bull; ${third.solved_count} solved
        </div>
      </div>
    `;
  }

  podium.innerHTML = html;
}

function renderMyRankBanner(users) {
  const banner = document.getElementById("leaderboard-my-rank");
  if (!banner) return;

  const currentEmail = api.user?.email || "student@preppilot.com";
  let myEntry = users.find((u) => u.email === currentEmail) || users[1] || users[0];

  if (!myEntry) return;

  banner.innerHTML = `
    <div class="d-flex align-items-center gap-3">
      <div style="width:44px; height:44px; border-radius:50%; background: linear-gradient(135deg, #6366f1, #06b6d4); display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.15rem; color:#fff;">
        ${myEntry.full_name ? myEntry.full_name[0] : "U"}
      </div>
      <div>
        <div class="fw-bold text-light">${myEntry.full_name} <span class="badge bg-primary bg-opacity-25 text-primary ms-1">You</span></div>
        <div class="text-muted small">${myEntry.college || "Engineering Campus"} &bull; Target: <span class="text-info">${myEntry.target_company || "Google"}</span></div>
      </div>
    </div>
    <div class="d-flex align-items-center gap-3">
      <span class="tier-badge ${getTierBadgeClass(myEntry.tier)}">${myEntry.badge || "⚔️ Diamond"}</span>
      <div class="text-end">
        <div class="text-info fw-bold fs-6">${myEntry.total_score} pts</div>
        <div class="text-muted small">Rank #${myEntry.rank} Global</div>
      </div>
    </div>
  `;
}

function getTierBadgeClass(tier) {
  const norm = (tier || "").toLowerCase();
  if (norm.includes("grandmaster")) return "tier-grandmaster";
  if (norm.includes("master")) return "tier-master";
  if (norm.includes("diamond")) return "tier-diamond";
  if (norm.includes("expert")) return "tier-expert";
  return "tier-rising";
}

function setupLeaderboardFilters() {
  const searchInput = document.getElementById("leaderboard-search");
  const tierFilter = document.getElementById("leaderboard-tier-filter");
  const sortFilter = document.getElementById("leaderboard-sort-filter");

  const applyFilters = () => {
    let filtered = [...leaderboardCache];
    const query = (searchInput?.value || "").toLowerCase().trim();
    const tier = tierFilter?.value || "all";
    const sort = sortFilter?.value || "score";

    if (query) {
      filtered = filtered.filter(
        (u) =>
          u.full_name.toLowerCase().includes(query) ||
          (u.college && u.college.toLowerCase().includes(query)) ||
          (u.target_company && u.target_company.toLowerCase().includes(query))
      );
    }

    if (tier !== "all") {
      filtered = filtered.filter((u) => u.tier === tier);
    }

    if (sort === "streak") {
      filtered.sort((a, b) => b.streak_days - a.streak_days);
    } else if (sort === "solved") {
      filtered.sort((a, b) => b.solved_count - a.solved_count);
    } else {
      filtered.sort((a, b) => b.total_score - a.total_score);
    }

    renderLeaderboardTable(filtered);
  };

  searchInput?.addEventListener("input", applyFilters);
  tierFilter?.addEventListener("change", applyFilters);
  sortFilter?.addEventListener("change", applyFilters);
}

function renderLeaderboardTable(users) {
  const tbody = document.getElementById("leaderboard-table-body");
  if (!tbody) return;

  if (!users || !users.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-muted text-center py-4">No candidates found matching your filter criteria.</td></tr>';
    return;
  }

  tbody.innerHTML = users
    .map(
      (u, idx) => `
    <tr>
      <td class="fw-bold text-center" style="width: 70px;">
        ${u.rank === 1 ? '<span class="fs-5">🥇</span>' : u.rank === 2 ? '<span class="fs-5">🥈</span>' : u.rank === 3 ? '<span class="fs-5">🥉</span>' : `<span class="badge rounded-pill bg-dark border border-secondary border-opacity-50 text-light">#${u.rank}</span>`}
      </td>
      <td>
        <div class="d-flex align-items-center gap-2">
          <div style="width:34px; height:34px; border-radius:50%; background: #1e293b; border: 1px solid rgba(255,255,255,0.1); display:flex; align-items:center; justify-content:center; font-size:0.85rem; font-weight:700; color:#38bdf8;">
            ${u.full_name ? u.full_name[0].toUpperCase() : "U"}
          </div>
          <div>
            <div class="fw-semibold text-light">${u.full_name}</div>
            <div class="text-muted small d-flex align-items-center gap-1">
              <span>${u.college || "Campus"}</span> &bull; 
              <span class="badge-company ${getCompanyBadgeClass(u.target_company)} py-0 px-1" style="font-size:0.65rem;">${u.target_company || "General"}</span>
            </div>
          </div>
        </div>
      </td>
      <td>
        <span class="tier-badge ${getTierBadgeClass(u.tier)}">${u.badge || u.tier}</span>
      </td>
      <td>
        <span class="text-info fw-bold">${u.total_score || 0} pts</span>
      </td>
      <td>
        <div class="d-flex align-items-center gap-1">
          <span class="fw-bold text-light">${u.solved_count || 0}</span>
          <span class="small text-muted">(${u.easy_solved || 0}E / ${u.med_solved || 0}M / ${u.hard_solved || 0}H)</span>
        </div>
      </td>
      <td>
        <span class="text-light small">
          <i class="fa-solid fa-fire text-danger me-1"></i> ${u.streak_days || 1}d
        </span>
      </td>
      <td>
        <span class="badge ${
          (u.total_score || 0) >= 200 ? "bg-success text-success" : (u.total_score || 0) >= 100 ? "bg-info text-info" : "bg-secondary text-secondary"
        } bg-opacity-25">
          ${(u.total_score || 0) >= 200 ? "Placement Ready" : (u.total_score || 0) >= 100 ? "In High Gear" : "In Training"}
        </span>
      </td>
    </tr>
  `
    )
    .join("");
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
            <div class="stat-value text-info">${stats.total_companies || 8}</div>
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
