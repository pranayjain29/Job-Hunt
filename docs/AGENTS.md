# Job Hunt 2 - Development Guide

For developers who want to modify or understand the code.

---

## Project Structure

```
src/
├── config.py         # All settings (from .env)
├── models.py         # JobPosting, ApplicationStatus
└── agents/
    ├── scraper.py       # Naukri scraper
    ├── evaluator.py    # AI scoring
    ├── data_engineer.py # Excel storage
    └── dashboard.py  # Streamlit UI
```

---

## Core Components

### 1. Scraper Agent (scraper.py)
- Uses Playwright (async) for browser automation
- Scrapes Naukri job listings
- Filters by experience (1-3 years)
- Returns: List[JobPosting]

### 2. Evaluator Agent (evaluator.py)
- Uses OpenRouter API
- Calls minimax/minimax-m2.5:free model
- Batch processing: 10 jobs per call
- Returns: Jobs with scores

### 3. Data Engineer (data_engineer.py)
- Saves to Excel (job_leads.xlsx)
- Deduplication by URL
- Status tracking

### 4. Dashboard (dashboard.py)
- Streamlit web UI
- Sidebar score filter
- Status management

---

## Key Classes

### JobPosting
```python
@dataclass
class JobPosting:
    job_id: str
    title: str
    company: str
    location: str
    experience_required: int
    description: str
    skills: List[str]
    source: str
    url: str
    score: Optional[float]  # Added by evaluator
    status: ApplicationStatus  # New/Applied/Interviewing/etc
```

### ApplicationStatus
```python
class ApplicationStatus(Enum):
    NEW = "New"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    REJECTED = "Rejected"
    NOT_APPLYING = "Not Applying"
    OFFER = "Offer"
```

---

## Configuration

### Environment Variables

```env
# Required
OPENROUTER_API_KEY=sk-or-...

# Job Search
TARGET_ROLES=Data Analyst,AI Engineer
LOCATIONS=Chennai,Bangalore
EXPERIENCE_MIN=1
EXPERIENCE_MAX=3

# Scoring
MIN_SCORE_THRESHOLD=50
BATCH_SIZE=10
OPENROUTER_MODEL=minimax/minimax-m2.5:free
```

---

## Development Rules

### Adding New Agents

1. Create in `src/agents/`
2. Use relative imports:
   ```python
   from ..config import ...
   from ..models import ...
   ```

### Adding New Job Boards

1. Create scraper in `src/agents/`
2. Follow existing pattern in scraper.py
3. Update main.py to call it

### Modifying Scoring

1. Edit `src/agents/evaluator.py`
2. Update `_build_batch_prompt()`
3. Changes apply to all future scoring

---

## Testing

```bash
# Test scraper
uv run python -c "from src.agents.scraper import NaukriScraperRunner; print(NaukriScraperRunner.run())"

# Test evaluator
uv run python -c "from src.agents.evaluator import EvaluatorAgent; from src.models import JobPosting; from datetime import datetime; jobs = [JobPosting(job_id='1', title='Data Analyst', company='Test', location='Chennai', experience_required=2, description='Python SQL', skills=[], source='Naukri', url='https://test.com', posted_date=datetime.now())]; print(EvaluatorAgent().evaluate_jobs(jobs))"

# Test data engineer
uv run python -c "from src.agents.data_engineer import DataEngineerAgent; print(len(DataEngineerAgent().load_existing_jobs()))"
```

---

## API Details

### OpenRouter Call

```python
import requests

def call_ai(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jobhunt2.local",
        "X-Title": "Job Hunt 2"
    }
    payload = {
        "model": "minimax/minimax-m2.5:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    return response.json()
```

---

## Performance

| Action | Time |
|--------|------|
| Scraping 40 jobs | ~2 min |
| AI Scoring (40 jobs) | ~1 min |
| Dashboard load | instant |

---

## Dependencies

```toml
[dependencies]
openai = ">=2.32.0"
openpyxl = ">=3.1.5"
pandas = ">=3.0.2"
playwright = ">=1.58.0"
python-dotenv = ">=1.2.2"
streamlit = ">=1.56.0"
requests = ">=2.31.0"
PyPDF2 = ">=3.0.0"
```

---

## Common Issues

| Issue | Fix |
|-------|-----|
| Page length < 1000 | Naukri blocking - use visible browser |
| JSON parse error | AI response format changed |
| Duplicate jobs | Check data_engineer.remove_duplicates() |
| Dashboard import error | Check sys.path in dashboard.py |

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make changes
4. Test locally
5. Open a PR

---

## License

MIT License - Free to use and modify.