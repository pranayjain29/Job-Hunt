# Job Hunt 2

AI-Powered Automated Job Search

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url>
cd job-hunt-2

# 2. Run setup (first time only)
python setup.py

# 3. Edit .env - add your OPENROUTER_API_KEY
# Get free key at https://openrouter.ai (no credit card)

# 4. Run the app
uv run python main.py run
```

## Commands

| Command | Description |
|---------|-------------|
| `python setup.py` | First time setup |
| `uv run python main.py run` | Full workflow |
| `uv run python main.py scrape` | Scrape jobs only |
| `uv run python main.py dashboard` | Open dashboard |

Dashboard: http://localhost:8501

## Configuration (.env)

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxx
TARGET_ROLES=Data Analyst,AI Engineer,ML Engineer
LOCATIONS=Chennai,Bangalore
MIN_SCORE_THRESHOLD=50
RESUME_PATH=resume.pdf
```

## Flow

1. Run `python setup.py` (first time)
2. Edit `.env` with your API key
3. Run `uv run python main.py run`
4. Confirm settings or edit
5. Scrapes Naukri jobs
6. Scores with AI
7. Opens dashboard