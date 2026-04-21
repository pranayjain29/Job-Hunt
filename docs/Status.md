# Job Hunt 2 - v1.0 Ready

## Version: 1.0 (Production Ready)

---

## What's Built

| Component | Status | Notes |
|-----------|--------|-------|
| Setup Script | ✓ | Installs uv, deps, playwright |
| CLI | ✓ | Interactive yes/edit/quit |
| Config | ✓ | .env file |
| Scraper | ✓ | Naukri + visible browser |
| Evaluator | ✓ | OpenRouter + retry logic |
| Data Engineer | ✓ | Excel + deduplication |
| Dashboard | ✓ | Streamlit + threshold |

---

## Key Features

- [x] Resume-aware job scoring
- [x] Batch AI processing (10 jobs/call)
- [x] Retry on API failure (3 attempts)
- [x] Deduplication by URL
- [x] Configurable score threshold
- [x] Visible browser mode
- [x] Interactive dashboard

---

## Files

```
setup.py              # First time setup
main.py             # CLI entry
.env               # Your config (empty)
.env.example        # Template
src/
│   ├── config.py
│   └── agents/
│       ├── scraper.py
│       ├── evaluator.py
│       ├── data_engineer.py
│       └── dashboard.py
job_leads.xlsx
docs/
```

---

## Usage

```bash
# New user
python setup.py
uv run python main.py run

# Existing user
uv run python main.py run
uv run python main.py scrape
uv run python main.py dashboard
```

Dashboard: http://localhost:8501

---

## Testing

| Test | Result |
|------|--------|
| Setup | ✓ Pass |
| Config load | ✓ Pass |
| Scrape | ✓ Pass (44 jobs) |
| Evaluator import | ✓ Pass |
| Dashboard | ✓ Pass |

---

## v1.0 Ready - Git Push!