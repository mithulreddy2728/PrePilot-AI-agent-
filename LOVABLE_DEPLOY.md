# Deploying PrepPilot AI on Lovable & Cloud Platforms

PrepPilot AI is designed for seamless modern deployment on **Lovable.dev**, **Railway**, and **Docker**.

---

## 🚀 Option 1: Deploying on Lovable (lovable.dev)

Lovable connects directly to your GitHub repository (`mithulreddy2728/PrePilot-AI-agent-`) to build, host, and provide an interactive AI development workspace.

### Steps:
1. **Push the latest commits to GitHub**:
   ```bash
   git add .
   git commit -m "Add multi-language DSA arena, 16 company hiring tracks, and gamified leaderboard"
   git push origin main
   ```

2. **Log into Lovable**:
   - Go to [https://lovable.dev](https://lovable.dev) and sign in with your GitHub account.

3. **Import the Repository**:
   - Click **"Import from GitHub"** or **"New Project" > "Import Existing Repository"**.
   - Select your repo: `mithulreddy2728/PrePilot-AI-agent-`.
   - Lovable reads `lovable.config.json` and `package.json` automatically.
   - Root directory: `./` (or `frontend` for static hosting).

4. **Deploy Live**:
   - Click **Deploy** in the top-right corner.
   - Lovable provides a live URL (e.g. `https://preppilot-ai.lovable.app`).

---

## ⚡ Option 2: Full-Stack Deployment (Backend on Railway + Frontend on Lovable/Vercel)

For a complete production setup with persistent database and multi-language compiler sandbox:

### Backend on Railway (1-click Docker):
1. Go to [https://railway.app](https://railway.app) and click **"New Project" > "Deploy from GitHub repo"**.
2. Select `mithulreddy2728/PrePilot-AI-agent-`.
3. Railway automatically detects `railway.json` and `Dockerfile`.
4. Add environment variables in Railway Settings:
   - `JWT_SECRET_KEY`: `your-secure-random-secret`
   - `GEMINI_API_KEY`: *(Optional)* Your Google Gemini API key
   - `SEED_DEMO_DATA`: `true`
5. Railway assigns a public URL (e.g., `https://preppilot-production.up.railway.app`).

### Connect Frontend:
- Update `API_BASE` in `frontend/js/api.js` or set `window.PREPPILOT_API_URL` to your Railway URL.

---

## 💻 Local Quickstart

```bash
# 1. Activate Python virtual environment
source venv/bin/activate

# 2. Run backend & frontend server
uvicorn backend.app.main:app --reload --port 8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
