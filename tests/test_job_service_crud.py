from datetime import datetime

from src.database.models import Job
from src.services.job_service import JobService


def test_get_job_by_id_returns_job_or_none(db_session):
    service = JobService(db_session)

    job = Job(
        company="Acme Corp",
        title="Backend Engineer",
        url="https://jobs.example.com/acme/backend",
        status="active",
        scraped_at=datetime(2024, 1, 1, 9, 0, 0),
    )
    db_session.add(job)
    db_session.flush()

    found = service.get_job_by_id(job.id)
    missing = service.get_job_by_id(9999)

    assert found is not None
    assert found.id == job.id
    assert missing is None


def test_delete_job_removes_job(db_session):
    service = JobService(db_session)

    job = Job(
        company="Acme Corp",
        title="Data Engineer",
        url="https://jobs.example.com/acme/data",
        status="active",
        scraped_at=datetime(2024, 1, 2, 9, 0, 0),
    )
    db_session.add(job)
    db_session.flush()

    deleted = service.delete_job(job.id)

    assert deleted is True
    assert db_session.query(Job).count() == 0


def test_archive_job_sets_status(db_session):
    service = JobService(db_session)

    job = Job(
        company="Acme Corp",
        title="ML Engineer",
        url="https://jobs.example.com/acme/ml",
        status="active",
        scraped_at=datetime(2024, 1, 3, 9, 0, 0),
    )
    db_session.add(job)
    db_session.flush()

    archived = service.archive_job(job.id)

    assert archived is True
    refreshed = db_session.query(Job).filter(Job.id == job.id).one()
    assert refreshed.status == "archived"


def test_cleanup_jobs_deletes_non_matching_locations(db_session):
    service = JobService(db_session)

    db_session.add_all(
        [
            Job(
                company="Acme Corp",
                title="AU Role",
                url="https://jobs.example.com/acme/au",
                status="active",
                location="Sydney, Australia",
                scraped_at=datetime(2024, 1, 4, 9, 0, 0),
            ),
            Job(
                company="Acme Corp",
                title="US Role",
                url="https://jobs.example.com/acme/us",
                status="active",
                location="Remote - US",
                scraped_at=datetime(2024, 1, 5, 9, 0, 0),
            ),
            Job(
                company="Acme Corp",
                title="Unknown Location",
                url="https://jobs.example.com/acme/unknown",
                status="active",
                location=None,
                scraped_at=datetime(2024, 1, 6, 9, 0, 0),
            ),
        ]
    )
    db_session.flush()

    deleted_count = service.cleanup_jobs(location_filter="Australia")

    assert deleted_count == 2
    remaining = db_session.query(Job).all()
    assert len(remaining) == 1
    assert remaining[0].location == "Sydney, Australia"
