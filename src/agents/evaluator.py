from typing import List, Optional
import json
import requests
import time

from ..config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL, TARGET_ROLES, RESUME_CONTEXT, MIN_SCORE_THRESHOLD
from ..models import JobPosting


class EvaluatorAgent:
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or OPENROUTER_MODEL
        self.base_url = base_url or OPENROUTER_BASE_URL
        self.batch_size = 10
        self.max_retries = 3
        self.retry_delay = 5

    def _build_batch_prompt(self, jobs: List[JobPosting]) -> str:
        job_list = []
        for i, job in enumerate(jobs):
            job_list.append(f"{i+1}. {job.title} at {job.company} - {job.description[:150]}")

        jobs_text = "\n".join(job_list)

        return f"""You are a job matching expert. Analyze these job postings and give scores from 0-100 based on how well they match the candidate's profile.

CANDIDATE PROFILE:
{RESUME_CONTEXT}

Target roles: {', '.join(TARGET_ROLES)}

JOBS TO EVALUATE:
{jobs_text}

Evaluate each job based on how well it matches the candidate's skills and experience. Consider:
- Required skills vs candidate's skills
- Experience level match
- Role alignment with candidate's background

Respond ONLY with valid JSON array in this exact format (one object per job):
[{{"index": 1, "score": 85, "skills": ["Python", "SQL"], "reason": "brief reason"}}, ...]"""

    def _call_openrouter(self, prompt: str) -> Optional[List[dict]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://jobhunt2.local",
            "X-Title": "Job Hunt 2"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120
                )

                if response.status_code == 401:
                    raise requests.HTTPError("401 unauthorized - check API key")
                elif response.status_code == 429:
                    raise requests.HTTPError("429 rate limited - too many requests")
                elif response.status_code >= 500:
                    raise requests.HTTPError(f"{response.status_code} server error")

                response.raise_for_status()
                result = response.json()

                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    raise ValueError("Empty response content")
                return json.loads(content)

            except requests.HTTPError as e:
                print(f"  API error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    print(f"  Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"  Failed after {self.max_retries} attempts")
                    return None
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"  API error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    print(f"  Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"  Failed after {self.max_retries} attempts")
                    return None

        return None

    def evaluate_jobs(self, jobs: List[JobPosting]) -> List[JobPosting]:
        total_batches = (len(jobs) + self.batch_size - 1) // self.batch_size
        print(f"Evaluating {len(jobs)} jobs in {total_batches} batches...")

        for batch_idx in range(total_batches):
            start = batch_idx * self.batch_size
            end = min(start + self.batch_size, len(jobs))
            batch = jobs[start:end]

            print(f"Batch {batch_idx + 1}/{total_batches}: processing jobs {start+1}-{end}")

            prompt = self._build_batch_prompt(batch)
            results = self._call_openrouter(prompt)

            if results:
                for r in results:
                    idx = r.get("index", 0) - 1
                    if 0 <= idx < len(batch):
                        batch[idx].score = r.get("score", 50)
                        batch[idx].skills = r.get("skills", [])
            else:
                for job in batch:
                    job.score = 50

        return jobs

    def filter_quality_jobs(self, jobs: List[JobPosting], min_score: float = None) -> List[JobPosting]:
        min_score = min_score or MIN_SCORE_THRESHOLD
        evaluated = self.evaluate_jobs(jobs)
        return [job for job in evaluated if job.score and job.score >= min_score]


def run_evaluator(jobs: List[JobPosting], min_score: float = None) -> List[JobPosting]:
    evaluator = EvaluatorAgent()
    return evaluator.filter_quality_jobs(jobs, min_score)