from __future__ import annotations

import json

from sqlalchemy.orm import Session

from src.ai.llm_client import LLMClient
from src.database.models import Job, JobSkill, Skill
from src.logger import get_logger

logger = get_logger(__name__)


class SkillService:
    def __init__(self, db_session: Session, llm_client: LLMClient) -> None:
        self.db_session = db_session
        self.llm_client = llm_client

    def extract_and_save_skills(self, job_id: int) -> list[str] | None:
        job = self.db_session.query(Job).filter(Job.id == job_id).one_or_none()
        if job is None:
            logger.warning("Job not found for skill extraction: %s", job_id)
            return None

        description = (job.description or "").strip()
        if not description:
            return None

        prompt = (
            "Extract technical skills from this job description. "
            "Return JSON {skills: [list of strings]}.\n\n"
            f"Job description:\n{description}"
        )
        response = self.llm_client.generate_json(prompt)
        if not response:
            logger.warning("LLM did not return skills for job: %s", job_id)
            return None

        skills = response.get("skills")
        if not isinstance(skills, list):
            logger.warning("LLM response missing skills list for job: %s", job_id)
            return None

        job.skills_raw = json.dumps(response)

        normalized_skills: list[str] = []
        seen: set[str] = set()
        for skill_name in skills:
            if not isinstance(skill_name, str):
                continue
            normalized = skill_name.strip().lower()
            if not normalized or normalized in seen:
                continue

            seen.add(normalized)
            normalized_skills.append(normalized)

            skill = (
                self.db_session.query(Skill)
                .filter(Skill.skill_name == normalized)
                .one_or_none()
            )
            if skill is None:
                skill = Skill(skill_name=normalized)
                self.db_session.add(skill)
                self.db_session.flush()

            link = (
                self.db_session.query(JobSkill)
                .filter(
                    JobSkill.job_id == job.id,
                    JobSkill.skill_id == skill.id,
                )
                .one_or_none()
            )
            if link is None:
                self.db_session.add(JobSkill(job_id=job.id, skill_id=skill.id))

        return normalized_skills
