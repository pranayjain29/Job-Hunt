import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TARGET_ROLES = [r.strip() for r in os.getenv("TARGET_ROLES", "Data Analyst,AI Engineer").split(",") if r.strip()]
LOCATIONS = [l.strip() for l in os.getenv("LOCATIONS", "Chennai,Bangalore").split(",") if l.strip()]
EXPERIENCE_RANGE = (int(os.getenv("EXPERIENCE_MIN", 1)), int(os.getenv("EXPERIENCE_MAX", 3)))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "minimax/minimax-m2.5:free")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

MIN_SCORE_THRESHOLD = int(os.getenv("MIN_SCORE_THRESHOLD", 50))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))

DATA_FILE = os.getenv("DATA_FILE", "job_leads.xlsx")

def _load_resume():
    path = os.getenv("RESUME_PATH", "")
    text = os.getenv("RESUME_TEXT", "")
    
    if path and Path(path).exists():
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
            return " ".join(page.extract_text() for page in reader.pages)
        except Exception:
            pass
    
    if text:
        return text
    
    return ""

RESUME_CONTEXT = _load_resume()