# Job Hunt 2 - v0.3.1

## Version: 0.3.1

---

## What's Built

| Component | Status | Notes |
|-----------|--------|-------|
| Setup Script | ✓ | Installs uv, deps, playwright |
| CLI | ✓ | Interactive yes/edit/quit |
| Config | ✓ | .env file |
| Scraper | ✓ | 3 parallel browsers |
| Evaluator | ✓ | Async, 4 concurrent batches |
| Data Engineer | ✓ | Excel + deduplication |
| Dashboard | ✓ | Wordcloud + skills gap |

---

## Key Features

- [x] Resume-aware job scoring
- [x] Skills passed to prompt (better scoring)
- [x] Concurrent scraper (3 parallel browsers)
- [x] Async evaluator (4 concurrent batches)
- [x] Batch AI processing (10 jobs/call)
- [x] Skills wordcloud visualization
- [x] Skills gap analysis
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

Dashboard: http://localhost:8501 (Statistics tab for wordcloud & skills gap)

---

## Testing

| Test | Result |
|------|--------|
| Setup | ✓ Pass |
| Config load | ✓ Pass |
| Scrape | ✓ Pass |
| Evaluator | ✓ Pass (async, 4 concurrent) |
| Dashboard | ✓ Pass |
| Wordcloud | ✓ Pass |
| Skills Gap | ✓ Pass |

---

## v0.3.1 Ready