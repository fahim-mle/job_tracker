from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from src.database.models import Job


class JobService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def upsert_job(self, job_data: dict[str, Any]) -> Job:
        url = job_data.get("url")
        job = None
        if url:
            job = self.db_session.query(Job).filter(Job.url == url).one_or_none()

        allowed_fields = {
            "company",
            "title",
            "description",
            "skills_raw",
            "url",
            "posted_date",
            "deadline",
            "status",
            "source_platform",
            "raw_html",
        }
        payload = {
            key: value for key, value in job_data.items() if key in allowed_fields
        }

        if job is None:
            job = Job(**payload)
            self.db_session.add(job)
            return job

        for key, value in payload.items():
            if key == "url" and url is None:
                continue
            setattr(job, key, value)

        return job

    def get_active_jobs(self, limit: int = 100) -> list[Job]:
        return (
            self.db_session.query(Job)
            .filter(Job.status == "active")
            .order_by(Job.scraped_at.desc())
            .limit(limit)
            .all()
        )
