from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database.models import Application, Job, JobSkill, Skill
from src.database.session import SessionLocal


def _database_has_data(session) -> bool:
    return any(
        session.query(model).first() for model in (Job, Skill, Application, JobSkill)
    )


def seed_database() -> None:
    session = SessionLocal()
    try:
        if _database_has_data(session):
            return

        job = Job(
            company="Sample Company",
            title="Python Developer",
            description="Seeded job for local development.",
        )
        python_skill = Skill(skill_name="Python")
        sql_skill = Skill(skill_name="SQL")
        job.job_skills = [
            JobSkill(skill=python_skill),
            JobSkill(skill=sql_skill),
        ]

        session.add_all([job, python_skill, sql_skill])
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
