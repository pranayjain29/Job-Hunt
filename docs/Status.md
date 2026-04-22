# Job Hunt 2 - v0.3.0

## Version: 0.3.0

---

## What's Built

| Component | Status | Notes |
|-----------|--------|-------|
| Setup Script | ✓ | Installs uv, deps, playwright |
| CLI | ✓ | Interactive yes/edit/quit |
| Config | ✓ | .env file |
| Scraper | ✓ | Naukri + visible browser |
| Evaluator | ✓ | Async, 4 concurrent batches |
| Data Engineer | ✓ | Excel + deduplication |
| Dashboard | ✓ | Streamlit + threshold |

---

## Key Features

- [x] Resume-aware job scoring
- [x] Skills passed to prompt (better scoring)
- [x] Async evaluator (4 concurrent batches)
- [x] Batch AI processing (10 jobs/call)
- [x] Retry on API failure (3 attempts)
- [x] Deduplication by URL
- [x] Configurable score threshold
- [x] Visible browser mode
- [x] Interactive dashboard
- [x] `-y` auto-confirm flag
- [x] Separate evaluate command

---

## Files

```
setup.py              # First time setup
main.py             # CLI entry
.env               # Your config
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
uv run main.py run -y

# Existing user
uv run main.py run -y
uv run main.py scrape
uv run main.py evaluate
uv run main.py dashboard
```

Dashboard: http://localhost:8501

---

## Testing

| Test | Result |
|------|--------|
| Setup | ✓ Pass |
| Config load | ✓ Pass |
| Scrape | ✓ Pass |
| Evaluator | ✓ Pass (async, 4 concurrent) |
| Dashboard | ✓ Pass |

---

## v0.3.0 Ready