from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import delete, not_, or_, select, update
from sqlalchemy.orm import Session, joinedload

from src.database.models import Job
from src.logger import get_logger

if TYPE_CHECKING:
    from src.services.skill_service import SkillService


logger = get_logger(__name__)


class JobService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_job_by_id(self, job_id: int) -> Job | None:
        try:
            stmt = select(Job).where(Job.id == job_id)
            result = self.db_session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception:
            logger.exception("Failed to fetch job by id: %s", job_id)
            return None

    def delete_job(self, job_id: int) -> bool:
        try:
            stmt = delete(Job).where(Job.id == job_id)
            result = self.db_session.execute(stmt)
            return (result.rowcount or 0) > 0
        except Exception:
            logger.exception("Failed to delete job: %s", job_id)
            return False

    def archive_job(self, job_id: int) -> bool:
        try:
            stmt = (
                update(Job)
                .where(Job.id == job_id)
                .values(status="archived")
                .execution_options(synchronize_session="fetch")
            )
            result = self.db_session.execute(stmt)
            return (result.rowcount or 0) > 0
        except Exception:
            logger.exception("Failed to archive job: %s", job_id)
            return False

    def cleanup_jobs(self, location_filter: str = "Australia") -> int:
        try:
            stmt = delete(Job).where(
                or_(
                    Job.location.is_(None),
                    not_(Job.location.contains(location_filter)),
                )
            )
            result = self.db_session.execute(stmt)
            return result.rowcount or 0
        except Exception:
            logger.exception("Failed to cleanup jobs with filter: %s", location_filter)
            return 0

    def upsert_job(self, job_data: dict[str, Any]) -> Job:
        url = job_data.get("url")
        job = None
        if url:
            job = self.db_session.query(Job).filter(Job.url == url).one_or_none()

        allowed_fields = {
            "company",
            "title",
            "location",
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
            .options(joinedload(Job.skills))
            .filter(Job.status == "active")
            .order_by(Job.scraped_at.desc())
            .limit(limit)
            .all()
        )

    def process_new_jobs_with_ai(
        self, skill_service: SkillService, limit: int = 100
    ) -> int:
        jobs = (
            self.db_session.query(Job)
            .filter(~Job.job_skills.any())
            .order_by(Job.scraped_at.desc())
            .limit(limit)
            .all()
        )

        processed = 0
        for job in jobs:
            skill_service.extract_and_save_skills(job.id)
            processed += 1

        return processed
