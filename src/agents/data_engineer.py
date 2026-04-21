from typing import List, Optional
from datetime import datetime
import os

import pandas as pd
from openpyxl import load_workbook

from ..config import DATA_FILE
from ..models import JobPosting, ApplicationStatus


class DataEngineerAgent:
    def __init__(self, file_path: str = DATA_FILE):
        self.file_path = file_path

    def _job_to_dict(self, job: JobPosting) -> dict:
        return {
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "experience_required": job.experience_required,
            "description": job.description,
            "skills": ", ".join(job.skills),
            "source": job.source,
            "url": job.url,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "status": job.status.value,
            "score": job.score,
            "created_at": job.created_at.isoformat() if job.created_at else datetime.now().isoformat(),
        }

    def _dict_to_job(self, row: dict) -> JobPosting:
        return JobPosting(
            job_id=str(row["job_id"]),
            title=str(row["title"]),
            company=str(row["company"]),
            location=str(row["location"]),
            experience_required=int(row["experience_required"]),
            description=str(row["description"]),
            skills=row["skills"].split(", ") if isinstance(row["skills"], str) else [],
            source=str(row["source"]),
            url=str(row["url"]),
            posted_date=datetime.fromisoformat(row["posted_date"]) if row["posted_date"] else None,
            status=ApplicationStatus(row["status"]) if row["status"] else ApplicationStatus.NEW,
            score=float(row["score"]) if pd.notna(row["score"]) else None,
        )

    def load_existing_jobs(self) -> List[JobPosting]:
        if not os.path.exists(self.file_path):
            return []

        df = pd.read_excel(self.file_path)
        return [self._dict_to_job(row) for _, row in df.iterrows()]

    def save_jobs(self, jobs: List[JobPosting], append: bool = True):
        new_jobs = jobs

        if append and os.path.exists(self.file_path):
            existing = self.load_existing_jobs()
            existing_urls = {job.url for job in existing}
            new_jobs = [job for job in jobs if job.url not in existing_urls]

        if not new_jobs:
            print("No new jobs to save")
            return

        all_jobs = self.load_existing_jobs() + new_jobs if append else new_jobs

        df = pd.DataFrame([self._job_to_dict(job) for job in all_jobs])
        df.to_excel(self.file_path, index=False, engine="openpyxl")
        print(f"Saved {len(new_jobs)} jobs to {self.file_path}")

    def update_status(self, job_id: str, status: ApplicationStatus):
        jobs = self.load_existing_jobs()
        updated = False

        for job in jobs:
            if job.job_id == job_id:
                job.status = status
                updated = True

        if updated:
            df = pd.DataFrame([self._job_to_dict(job) for job in jobs])
            df.to_excel(self.file_path, index=False, engine="openpyxl")
            print(f"Updated {job_id} status to {status.value}")
        else:
            print(f"Job {job_id} not found")

    def get_jobs_by_status(self, status: ApplicationStatus) -> List[JobPosting]:
        jobs = self.load_existing_jobs()
        return [job for job in jobs if job.status == status]

    def remove_duplicates(self) -> int:
        jobs = self.load_existing_jobs()
        seen = set()
        unique_jobs = []

        for job in jobs:
            if job.url not in seen:
                seen.add(job.url)
                unique_jobs.append(job)

        duplicates = len(jobs) - len(unique_jobs)

        if duplicates > 0:
            df = pd.DataFrame([self._job_to_dict(job) for job in unique_jobs])
            df.to_excel(self.file_path, index=False, engine="openpyxl")
            print(f"Removed {duplicates} duplicates")

        return duplicates


def run_data_engineer(jobs: List[JobPosting]) -> List[JobPosting]:
    agent = DataEngineerAgent()
    agent.save_jobs(jobs)
    return agent.load_existing_jobs()


if __name__ == "__main__":
    from ..models import ApplicationStatus

    test_jobs = [
        JobPosting(
            job_id="test1",
            title="Data Analyst",
            company="ABC Corp",
            location="Chennai",
            experience_required=2,
            description="Python, SQL, Tableau",
            skills=["Python", "SQL"],
            source="Naukri",
            url="https://naukri.com/job/123",
            posted_date=datetime.now(),
            status=ApplicationStatus.NEW,
            score=85,
        )
    ]

    agent = DataEngineerAgent()
    agent.save_jobs(test_jobs, append=False)

    loaded = agent.load_existing_jobs()
    print(f"Loaded {len(loaded)} jobs")
    agent.update_status("test1", ApplicationStatus.APPLIED)
    agent.remove_duplicates()