import json
from unittest.mock import Mock

from src.ai.llm_client import LLMClient
from src.database.models import Job, JobSkill, Skill
from src.services.skill_service import SkillService


def _create_job(db_session, description: str) -> Job:
    job = Job(
        company="Acme Corp",
        title="Data Engineer",
        url="https://jobs.example.com/acme/data-engineer",
        description=description,
    )
    db_session.add(job)
    db_session.flush()
    return job


def test_extract_and_save_skills_creates_skills_links_and_raw(db_session):
    job = _create_job(db_session, "We need Python and SQL skills.")
    llm_client = Mock(spec=LLMClient)
    llm_client.generate_json.return_value = {"skills": ["Python", "SQL"]}

    service = SkillService(db_session, llm_client)

    result = service.extract_and_save_skills(job.id)
    db_session.flush()

    assert result == ["python", "sql"]
    assert db_session.query(Skill).count() == 2

    job_skills = db_session.query(JobSkill).filter(JobSkill.job_id == job.id).all()
    assert len(job_skills) == 2

    job_from_db = db_session.query(Job).filter(Job.id == job.id).one()
    assert job_from_db.skills_raw == json.dumps({"skills": ["Python", "SQL"]})


def test_extract_and_save_skills_uses_existing_skills(db_session):
    job = _create_job(db_session, "We need Python and SQL skills.")
    db_session.add(Skill(skill_name="python"))
    db_session.flush()

    llm_client = Mock(spec=LLMClient)
    llm_client.generate_json.return_value = {"skills": ["Python", "SQL"]}

    service = SkillService(db_session, llm_client)

    service.extract_and_save_skills(job.id)
    db_session.flush()

    assert db_session.query(Skill).count() == 2
    assert db_session.query(Skill).filter(Skill.skill_name == "python").count() == 1

    python_skill = db_session.query(Skill).filter(Skill.skill_name == "python").one()
    sql_skill = db_session.query(Skill).filter(Skill.skill_name == "sql").one()
    job_skill_ids = {
        link.skill_id
        for link in db_session.query(JobSkill).filter(JobSkill.job_id == job.id).all()
    }
    assert job_skill_ids == {python_skill.id, sql_skill.id}
