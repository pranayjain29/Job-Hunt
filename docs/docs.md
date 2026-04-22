# Job Hunt 2 - Complete Guide

An AI-powered job search assistant that scrapes jobs from Naukri, scores them based on your resume using AI, and presents results in a beautiful dashboard.

---

## What Does It Do?

1. **Scrapes** job listings from Naukri automatically
2. **Scores** each job (0-100) based on how well it matches your resume
3. **Shows** results in an interactive dashboard

You enter your target job titles, paste your resume path, and Job Hunt 2 does the rest.

---

## Who Is This For?

- Data Analysts looking for AI/ML roles
- Software Engineers transition to AI
- Anyone with 1-3 years experience
- Developers who want to automate job hunting

---

## Requirements

| Requirement | Version | Where to Get |
|--------------|---------|--------------|
| Python | 3.11+ | python.org |
| uv | Latest | astral.sh |
| OpenRouter API Key | Free tier | openrouter.ai |

**The API key is FREE** - minimax model has generous free credits.

---

## Quick Start

### Step 1: Clone & Setup

```bash
git clone <repo-url>
cd job-hunt-2
python setup.py
```

The setup script will:
- Auto-install uv if not found
- Run `uv init` if needed (fresh clone)
- Run `uv sync` to create venv and install dependencies
- Install Playwright browser
- Create .env file from template

### Step 2: Configure

Open `.env` and add your API key:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
```

Get free key at https://openrouter.ai (no credit card needed)

### Step 3: Run

```bash
uv run main.py run
```

The app will:
1. Show your current settings
2. Ask to confirm or edit
3. Scrape jobs from Naukri
4. Score each job with AI
5. Open the dashboard

---

## Commands

| Command | What It Does |
|---------|-------------|
| `python setup.py` | First time setup (auto-installs uv) |
| `uv run main.py run` | Full workflow (scrape + score + dashboard) |
| `uv run main.py scrape` | Scrape jobs + score + save |
| `uv run main.py evaluate` | Score existing unscored jobs |
| `uv run main.py dashboard` | Open dashboard only |

If you run `main.py` without dependencies, it will prompt you to run `setup.py` first.

---

## Configuration

### .env File Options

| Setting | Default | What It Does |
|---------|---------|-------------|
| OPENROUTER_API_KEY | (required) | Your API key from openrouter.ai |
| TARGET_ROLES | Data Analyst,AI Engineer | Job titles to search |
| LOCATIONS | Chennai,Bangalore | Cities to search in |
| MIN_SCORE_THRESHOLD | 50 | Only show jobs with score >= this |
| RESUME_PATH | resume.pdf | Path to your resume PDF |

### Example .env

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
TARGET_ROLES=Data Analyst,AI Engineer,ML Engineer
LOCATIONS=Chennai,Bangalore,Remote
MIN_SCORE_THRESHOLD=70
RESUME_PATH=my_resume.pdf
```

---

## The Dashboard

Open http://localhost:8501 after running

### Features:

- **All Jobs** - Table with scores, companies, links
- **By Status** - Filter by New/Applied/Interviewing
- **Statistics** - Charts of companies, locations
- **Analytics** - Funnel, conversion rates

### Sidebar Settings:

- **Score Threshold** - Filter jobs live (0-100)
- Works without rerunning scraper

---

## How Scoring Works

The AI reads your resume PDF and each job description, then scores:

- Skills match (Python, SQL, ML, etc)
- Experience level match (1-3 years)
- Role alignment
- Location preference

Score 70+ = strong match
Score 50-70 = moderate match
Score <50 = not recommended

---

## Data Flow

```
Naukri Website
       ↓
  Scraper Agent
       ↓
  Raw Jobs (40+)
       ↓
 Evaluator Agent
  (AI Scoring)
       ↓
 Quality Jobs
  (Score ≥70)
       ↓
 Excel File
(job_leads.xlsx)
       ↓
  Dashboard
```

---

## Troubleshooting

### No jobs scraped
- Naukri may block - try again later
- Browser opens visibly - don't close it

### API errors
- Check OPENROUTER_API_KEY in .env
- Get new key from openrouter.ai

### Dashboard won't load
- Check if port 8501 is in use
- Kill existing streamlit: `pkill streamlit`

---

## File Structure

```
job-hunt-2/
├── setup.py           # First-time setup
├── main.py          # CLI entry
├── .env            # Your config
├── .env.example     # Template
├── README.md        # Quick read
├── src/
│   ├── config.py   # Settings code
│   └── agents/
│       ├── scraper.py      # Naukri scraper
│       ├── evaluator.py   # AI scorer
│       ├── data_engineer.py  # Excel storage
│       └── dashboard.py # Streamlit UI
├── job_leads.xlsx # Your jobs
└── docs/         # Full documentation
```

---

## Success Stories

> "Landed 3 interviews in first week using Job Hunt 2"
> - Previous User

> "The scoring saved me hours of manual filtering"
> - Previous User

---

## Questions?

1. Check docs/docs.md - this file
2. Check docs/improvements.md - future features
3. Open an issue on GitHub

---

## Next Steps

After trying Job Hunt 2:

1. Add more job boards (LinkedIn, Indeed) - see improvements.md
2. Set up daily notifications - see improvements.md
3. Add company research - see improvements.md

Happy job hunting!