from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session, selectinload

from src.database.models import Application


class ApplicationService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def create_application(self, job_id: int, status: str = "applied") -> Application:
        existing = (
            self.db_session.query(Application)
            .filter(Application.job_id == job_id)
            .one_or_none()
        )
        if existing is not None:
            return existing

        application = Application(
            job_id=job_id,
            status=status,
            applied_date=date.today(),
            last_updated=datetime.utcnow(),
        )
        self.db_session.add(application)
        return application

    def get_applications(self) -> list[Application]:
        return (
            self.db_session.query(Application)
            .options(selectinload(Application.job))
            .order_by(Application.last_updated.desc())
            .all()
        )

    def update_application_status(
        self, app_id: int, new_status: str
    ) -> Application | None:
        application = (
            self.db_session.query(Application)
            .filter(Application.id == app_id)
            .one_or_none()
        )
        if application is None:
            return None

        application.status = new_status
        application.last_updated = datetime.utcnow()
        return application

    def update_application_notes(
        self, app_id: int, notes: str | None
    ) -> Application | None:
        application = (
            self.db_session.query(Application)
            .filter(Application.id == app_id)
            .one_or_none()
        )
        if application is None:
            return None

        application.notes = notes
        application.last_updated = datetime.utcnow()
        return application
