from datetime import date, datetime

from src.database.models import Job
from src.services.job_service import JobService


def test_upsert_job_creates_new_job_and_saves_fields(db_session):
    service = JobService(db_session)

    job_data = {
        "company": "Acme Corp",
        "title": "Data Engineer",
        "description": "Build pipelines",
        "skills_raw": "Python, SQL",
        "url": "https://jobs.example.com/acme/data-engineer",
        "posted_date": date(2024, 1, 15),
        "deadline": date(2024, 2, 1),
        "status": "active",
        "source_platform": "ExampleBoard",
        "raw_html": "<html>...</html>",
    }

    job = service.upsert_job(job_data)
    db_session.flush()

    assert job.id is not None
    assert job.company == "Acme Corp"
    assert job.title == "Data Engineer"
    assert job.description == "Build pipelines"
    assert job.skills_raw == "Python, SQL"
    assert job.url == "https://jobs.example.com/acme/data-engineer"
    assert job.posted_date == date(2024, 1, 15)
    assert job.deadline == date(2024, 2, 1)
    assert job.status == "active"
    assert job.source_platform == "ExampleBoard"
    assert job.raw_html == "<html>...</html>"


def test_upsert_job_updates_existing_job_by_url(db_session):
    service = JobService(db_session)

    initial_job = service.upsert_job(
        {
            "company": "Acme Corp",
            "title": "Data Engineer",
            "url": "https://jobs.example.com/acme/data-engineer",
            "status": "active",
        }
    )
    db_session.flush()
    original_id = initial_job.id

    updated_job = service.upsert_job(
        {
            "company": "Acme Corp",
            "title": "Senior Data Engineer",
            "url": "https://jobs.example.com/acme/data-engineer",
            "status": "closed",
        }
    )
    db_session.flush()

    assert updated_job.id == original_id
    assert db_session.query(Job).count() == 1
    assert updated_job.title == "Senior Data Engineer"
    assert updated_job.status == "closed"


def test_get_active_jobs_returns_ordered_and_limited(db_session):
    service = JobService(db_session)

    db_session.add_all(
        [
            Job(
                company="Acme Corp",
                title="Engineer I",
                url="https://jobs.example.com/acme/engineer-1",
                status="active",
                scraped_at=datetime(2024, 1, 1, 9, 0, 0),
            ),
            Job(
                company="Acme Corp",
                title="Engineer II",
                url="https://jobs.example.com/acme/engineer-2",
                status="active",
                scraped_at=datetime(2024, 1, 3, 9, 0, 0),
            ),
            Job(
                company="Acme Corp",
                title="Engineer III",
                url="https://jobs.example.com/acme/engineer-3",
                status="active",
                scraped_at=datetime(2024, 1, 2, 9, 0, 0),
            ),
            Job(
                company="Acme Corp",
                title="Engineer IV",
                url="https://jobs.example.com/acme/engineer-4",
                status="inactive",
                scraped_at=datetime(2024, 1, 4, 9, 0, 0),
            ),
        ]
    )
    db_session.flush()

    active_jobs = service.get_active_jobs(limit=2)

    assert [job.url for job in active_jobs] == [
        "https://jobs.example.com/acme/engineer-2",
        "https://jobs.example.com/acme/engineer-3",
    ]
