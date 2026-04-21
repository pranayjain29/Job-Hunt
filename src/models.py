from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ApplicationStatus(Enum):
    NEW = "New"
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    REJECTED = "Rejected"
    NOT_APPLYING = "Not Applying"
    OFFER = "Offer"


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
    posted_date: Optional[datetime]
    status: ApplicationStatus = ApplicationStatus.NEW
    score: Optional[float] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()