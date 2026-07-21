# JobPilot

Semi-automated job hunting assistant. Scrapes job listings from multiple boards, scores them against your profile, tailors your resume and cover letter per job using GPT-4o, and queues everything into a web dashboard where you review and click to apply.

## Quick Start

### 1. Configure your profile

```bash
cp profile.example.yaml profile.yaml
# Edit profile.yaml with your target roles, skills, and resume text
```

### 2. Set up API keys

```bash
cp .env.example .env
# Add your OPENAI_API_KEY (required for scoring + tailoring)
# Add your SERPAPI_API_KEY (optional, for LinkedIn/Google Jobs search)
```

### 3. Install and run

```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..

# Run both (two terminals):
# Terminal 1 - Backend:
source venv/bin/activate
uvicorn backend.main:app --reload

# Terminal 2 - Frontend:
cd frontend && npm run dev
```

Open http://localhost:5173 in your browser.

## How It Works

1. **Scrape** — Fetches job listings from RemoteOK, LinkedIn (via Google Jobs/SerpAPI), Indeed, and HN Who's Hiring
2. **Dedup** — Filters out jobs you've already seen
3. **Score** — Rates each job 0-100 for fit using GPT-4o-mini against your profile
4. **Tailor** — For high-scoring jobs, generates a tailored resume and cover letter using GPT-4o
5. **Review** — Browse the dashboard, edit tailored documents, click Apply to open the job page

The pipeline runs automatically on a configurable cron (default: every 6 hours), or you can trigger it manually from the dashboard.

## Job Sources

| Source | Method | API Key Needed |
|--------|--------|----------------|
| RemoteOK | Public JSON API | No |
| LinkedIn | SerpAPI (Google Jobs) | Yes (`SERPAPI_API_KEY`) |
| Indeed | HTML scraping | No |
| HN Who's Hiring | Algolia + Firebase API | No |
