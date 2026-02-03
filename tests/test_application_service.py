from datetime import date, datetime

from src.database.models import Application, Job
from src.services.application_service import ApplicationService


def _create_job(db_session, url: str) -> Job:
    job = Job(company="Acme Corp", title="Data Engineer", url=url)
    db_session.add(job)
    db_session.flush()
    return job


def test_create_application_creates_once_and_returns_existing(db_session):
    service = ApplicationService(db_session)
    job = _create_job(db_session, "https://jobs.example.com/acme/data-engineer")

    application = service.create_application(job.id)
    db_session.flush()

    assert application.id is not None
    assert application.job_id == job.id
    assert application.status == "applied"
    assert application.applied_date == date.today()
    assert isinstance(application.last_updated, datetime)

    duplicate = service.create_application(job.id, status="interview")
    db_session.flush()

    assert duplicate.id == application.id
    assert duplicate.status == "applied"
    assert db_session.query(Application).count() == 1


def test_get_applications_orders_by_last_updated_desc(db_session):
    service = ApplicationService(db_session)

    job_one = _create_job(db_session, "https://jobs.example.com/acme/one")
    job_two = _create_job(db_session, "https://jobs.example.com/acme/two")
    job_three = _create_job(db_session, "https://jobs.example.com/acme/three")

    db_session.add_all(
        [
            Application(
                job_id=job_one.id,
                status="applied",
                applied_date=date(2024, 1, 1),
                last_updated=datetime(2024, 1, 1, 8, 0, 0),
            ),
            Application(
                job_id=job_two.id,
                status="interview",
                applied_date=date(2024, 1, 2),
                last_updated=datetime(2024, 1, 3, 9, 30, 0),
            ),
            Application(
                job_id=job_three.id,
                status="offer",
                applied_date=date(2024, 1, 2),
                last_updated=datetime(2024, 1, 2, 10, 15, 0),
            ),
        ]
    )
    db_session.flush()

    applications = service.get_applications()

    assert [app.job_id for app in applications] == [
        job_two.id,
        job_three.id,
        job_one.id,
    ]
    assert applications[0].job is not None


def test_update_application_status_updates_status_and_timestamp(db_session):
    service = ApplicationService(db_session)
    job = _create_job(db_session, "https://jobs.example.com/acme/update")

    application = Application(
        job_id=job.id,
        status="applied",
        applied_date=date(2024, 1, 1),
        last_updated=datetime(2024, 1, 1, 8, 0, 0),
    )
    db_session.add(application)
    db_session.flush()

    updated = service.update_application_status(application.id, "interview")

    assert updated is not None
    assert updated.status == "interview"
    assert updated.last_updated > datetime(2024, 1, 1, 8, 0, 0)
    assert service.update_application_status(9999, "offer") is None
