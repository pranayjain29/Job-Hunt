from typing import List, Optional
import asyncio
import json
import requests

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
        self.semaphore = asyncio.Semaphore(4)
        self.failed_batches = []

    def _build_batch_prompt(self, jobs: List[JobPosting]) -> str:
        job_list = []
        for i, job in enumerate(jobs):
            skills_text = ", ".join(job.skills[:5]) if job.skills else "N/A"
            job_list.append(f"{i+1}. {job.title} at {job.company} | Skills: {skills_text} | Exp: {job.experience_required} yrs")

        jobs_text = "\n".join(job_list)

        return f"""You are a job matching expert. Analyze these job postings and give scores from 0-100 based on how well they match the candidate's profile.

CANDIDATE PROFILE:
{RESUME_CONTEXT}

Target roles: {', '.join(TARGET_ROLES)}

JOBS TO EVALUATE:
{jobs_text}

Evaluate each job based on how well it matches the candidate's skills and experience. Consider:
- Skills match (given in job listing)
- Experience level match
- Role alignment with candidate's background

Respond ONLY with valid JSON array in this exact format (one object per job):
[{{"index": 1, "score": 85, "skills": ["Python", "SQL"], "reason": "brief reason"}}, ...]"""

    def _call_sync(self, prompt: str) -> Optional[List[dict]]:
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
                    raise requests.HTTPError("401 unauthorized")
                elif response.status_code == 429:
                    raise requests.HTTPError("429 rate limited")
                elif response.status_code >= 500:
                    raise requests.HTTPError(f"{response.status_code} server error")

                response.raise_for_status()
                result = response.json()

                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not content:
                    raise ValueError("Empty response")
                
                content = content.strip()
                
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                elif content.startswith("```"):
                    content = content.replace("```", "").strip()
                
                return json.loads(content)

            except Exception as e:
                if attempt < self.max_retries - 1:
                    continue
                return None
        
        return None

    async def _call_openrouter(self, prompt: str, batch_idx: int) -> Optional[List[dict]]:
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: self._call_sync(prompt))
            if result is None:
                self.failed_batches.append(batch_idx)
            return result

    async def evaluate_jobs(self, jobs: List[JobPosting]) -> List[JobPosting]:
        total_batches = (len(jobs) + self.batch_size - 1) // self.batch_size
        self.failed_batches = []
        print(f"Evaluating {len(jobs)} jobs in {total_batches} batches (4 concurrent)...")

        batches = [jobs[i:i+self.batch_size] for i in range(0, len(jobs), self.batch_size)]
        
        tasks = [
            self._call_openrouter(self._build_batch_prompt(batch), idx + 1)
            for idx, batch in enumerate(batches)
        ]
        results = await asyncio.gather(*tasks)

        for batch, result in zip(batches, results):
            if result:
                for r in result:
                    idx = r.get("index", 0) - 1
                    if 0 <= idx < len(batch):
                        batch[idx].score = r.get("score", 50)
                        batch[idx].skills = r.get("skills", [])
                print(f"  Batch evaluated: {len(result)} jobs")
            else:
                print(f"  Batch failed")

        if self.failed_batches:
            print(f"\nWARNING: Failed batches: {self.failed_batches}")
            print("Re-run the evaluate command to retry failed batches.")

        return jobs

    async def filter_quality_jobs(self, jobs: List[JobPosting], min_score: float = None) -> List[JobPosting]:
        min_score = min_score or MIN_SCORE_THRESHOLD
        evaluated = await self.evaluate_jobs(jobs)
        return [job for job in evaluated if job.score and job.score >= min_score]


async def run_evaluator(jobs: List[JobPosting], min_score: float = None) -> List[JobPosting]:
    evaluator = EvaluatorAgent()
    return await evaluator.filter_quality_jobs(jobs, min_score)