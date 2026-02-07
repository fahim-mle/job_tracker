from typing import TYPE_CHECKING, Callable, Iterable, cast

import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from sqlalchemy import func

from src.database.models import Application, Job, JobSkill, Skill
from src.database.session import SessionLocal
from src.services.application_service import ApplicationService
from src.services.job_service import JobService


def render_jobs_page() -> None:
    st.header("Jobs")

    if "page_number" not in st.session_state:
        st.session_state.page_number = 0

    with SessionLocal() as db_session:
        job_service = JobService(db_session)
        application_service = ApplicationService(db_session)

        st.sidebar.markdown("### Database Cleanup")
        keep_location = st.sidebar.text_input("Keep Location", value="Australia")
        cleanup_clicked = st.sidebar.button("Delete Others", key="cleanup_jobs")
        if cleanup_clicked:
            try:
                deleted_count = job_service.cleanup_jobs(keep_location)
                db_session.commit()
            except Exception as exc:
                db_session.rollback()
                st.sidebar.error(f"Cleanup failed: {exc}")
            else:
                st.sidebar.success(
                    f"Deleted {deleted_count} job{'s' if deleted_count != 1 else ''}."
                )

        jobs: list[Job] = job_service.get_active_jobs()

    search_query = st.sidebar.text_input(
        "Search",
        placeholder="Title or company",
    )
    location_query = st.sidebar.text_input(
        "Location",
        placeholder="City, region, or remote",
    )

    def source_label(job: object) -> str:
        value = getattr(job, "source_platform", None)
        return value if value else "Unknown"

    sources = sorted({source_label(job) for job in jobs})
    selected_sources = st.sidebar.multiselect(
        "Source",
        options=sources,
        default=sources,
    )

    search_value = search_query.strip().lower()
    location_value = location_query.strip().lower()

    def filter_jobs(items: Iterable[Job]) -> list[Job]:
        filtered = []
        for job in items:
            if search_value:
                company = getattr(job, "company", "") or ""
                title = getattr(job, "title", "") or ""
                if (
                    search_value not in company.lower()
                    and search_value not in title.lower()
                ):
                    continue

            if location_value:
                location = getattr(job, "location", "") or ""
                if location_value not in location.lower():
                    continue

            if selected_sources and source_label(job) not in selected_sources:
                continue

            filtered.append(job)

        return filtered

    filtered_jobs: list[Job] = filter_jobs(jobs)

    if not jobs:
        st.info("No active jobs found.")
        return

    st.caption(f"Showing {len(filtered_jobs)} of {len(jobs)} active jobs")

    page_size = 20
    total_pages = max(1, (len(filtered_jobs) + page_size - 1) // page_size)
    if st.session_state.page_number >= total_pages:
        st.session_state.page_number = total_pages - 1

    def get_dialog_decorator() -> Callable[..., Callable[..., None]]:
        dialog_attr = getattr(st, "dialog", None)
        if dialog_attr is not None:
            return dialog_attr
        dialog_attr = getattr(st, "experimental_dialog", None)
        if dialog_attr is None:
            raise RuntimeError("Streamlit dialog is not available.")
        return cast(Callable[..., Callable[..., None]], dialog_attr)

    dialog_decorator = get_dialog_decorator()

    if TYPE_CHECKING:

        def show_job_details(job_id: int) -> None:
            return
    else:

        @dialog_decorator("Job Details")
        def show_job_details(job_id: int) -> None:
            with SessionLocal() as dialog_session:
                detail_service = JobService(dialog_session)
                app_service = ApplicationService(dialog_session)
                job = detail_service.get_job_by_id(job_id)
                if job is None:
                    st.error("Job not found.")
                    return

                job_title = getattr(job, "title", "") or "Untitled role"
                job_company = getattr(job, "company", "") or "Unknown company"
                job_location = getattr(job, "location", "") or "N/A"
                posted_date = getattr(job, "posted_date", None)

                st.markdown(f"### {job_title}")
                st.write(job_company)
                st.write(job_location)
                st.write(
                    f"Posted Date: {posted_date.isoformat() if posted_date else 'N/A'}"
                )

                description = getattr(job, "description", None) or ""
                if description:
                    st.markdown(description)
                else:
                    st.markdown("_No description available._")

                action_cols = st.columns(2)
                with action_cols[0]:
                    track_clicked = st.button(
                        "Track",
                        type="primary",
                        key=f"dialog_track_{job.id}",
                    )
                    if track_clicked:
                        try:
                            application = app_service.create_application(job.id)
                            dialog_session.commit()
                        except Exception as exc:
                            dialog_session.rollback()
                            st.error(f"Failed to track application: {exc}")
                        else:
                            if application in dialog_session.new:
                                st.success("Application tracked.")
                            else:
                                st.info("Application already tracked.")

                with action_cols[1]:
                    archive_clicked = st.button(
                        "Archive",
                        key=f"dialog_archive_{job.id}",
                    )
                    if archive_clicked:
                        try:
                            archived = detail_service.archive_job(job.id)
                            if not archived:
                                raise ValueError("Job could not be archived.")
                            dialog_session.commit()
                        except Exception as exc:
                            dialog_session.rollback()
                            st.error(f"Failed to archive job: {exc}")
                        else:
                            st.success("Job archived.")
                            st.rerun()

    page_cols = st.columns([1, 2, 1])
    with page_cols[0]:
        if st.button("Previous", disabled=st.session_state.page_number == 0):
            st.session_state.page_number -= 1
            st.rerun()
    with page_cols[1]:
        st.caption(f"Page {st.session_state.page_number + 1} of {total_pages}")
    with page_cols[2]:
        if st.button(
            "Next",
            disabled=st.session_state.page_number >= total_pages - 1,
        ):
            st.session_state.page_number += 1
            st.rerun()

    start_index = st.session_state.page_number * page_size
    end_index = start_index + page_size
    page_jobs = filtered_jobs[start_index:end_index]

    for job in page_jobs:
        job_title = getattr(job, "title", "") or "Untitled role"
        job_company = getattr(job, "company", "") or "Unknown company"
        job_location = getattr(job, "location", "") or "N/A"
        posted_date = getattr(job, "posted_date", None)

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                st.markdown(f"### {job_title}")
                st.write(job_company)
            with col2:
                st.write(job_location)
                st.write(
                    f"Posted Date: {posted_date.isoformat() if posted_date else 'N/A'}"
                )
            with col3:
                if st.button("ℹ️ Info", key=f"info_{job.id}"):
                    show_job_details(job.id)
            with col4:
                track_clicked = st.button("➕ Track", key=f"track_{job.id}")
                if track_clicked:
                    try:
                        application = application_service.create_application(job.id)
                        db_session.commit()
                    except Exception as exc:
                        db_session.rollback()
                        st.error(f"Failed to track application: {exc}")
                    else:
                        if application in db_session.new:
                            st.success("Application tracked.")
                        else:
                            st.info("Application already tracked.")

                delete_clicked = st.button("🗑️ Delete", key=f"delete_{job.id}")
                if delete_clicked:
                    try:
                        deleted = job_service.delete_job(job.id)
                        if not deleted:
                            raise ValueError("Job could not be deleted.")
                        db_session.commit()
                    except Exception as exc:
                        db_session.rollback()
                        st.error(f"Failed to delete job: {exc}")
                    else:
                        st.success("Job deleted.")
                        st.rerun()


def render_applications_page() -> None:
    st.header("Applications")

    status_labels = {
        "applied": "Applied",
        "interview": "Interview",
        "offer": "Offer",
        "rejected": "Rejected",
    }
    status_options = list(status_labels.keys())

    def status_label(value: str) -> str:
        return status_labels.get(value, value.title())

    with SessionLocal() as db_session:
        app_service = ApplicationService(db_session)
        applications = app_service.get_applications()

        if not applications:
            st.info("No applications tracked yet.")
            return

        grouped: dict[str, list[Application]] = {
            status: [] for status in status_options
        }
        other_apps: list[Application] = []
        for application in applications:
            raw_status = (getattr(application, "status", "") or "applied").lower()
            if raw_status in grouped:
                grouped[raw_status].append(application)
            else:
                other_apps.append(application)

        def render_application_card(application: Application) -> None:
            job = getattr(application, "job", None)
            job_title = getattr(job, "title", "") if job else ""
            job_company = getattr(job, "company", "") if job else ""
            job_location = getattr(job, "location", "") if job else ""
            job_url = getattr(job, "url", "") if job else ""
            current_status = (
                getattr(application, "status", "applied") or "applied"
            ).lower()
            if current_status not in status_options:
                current_status = "applied"
            current_notes = getattr(application, "notes", None) or ""

            with st.form(key=f"application_form_{application.id}"):
                cols = st.columns([3, 2])
                with cols[0]:
                    title_line = job_title or "Untitled role"
                    company_line = job_company or "Unknown company"
                    st.markdown(f"**{title_line}**")
                    st.write(company_line)
                    if job_location:
                        st.caption(job_location)
                    if job_url:
                        st.write(f"[View job posting]({job_url})")

                with cols[1]:
                    status_value = st.selectbox(
                        "Status",
                        options=status_options,
                        index=status_options.index(current_status),
                        format_func=status_label,
                        key=f"status_{application.id}",
                    )
                    notes_value = st.text_area(
                        "Notes",
                        value=current_notes,
                        height=120,
                        key=f"notes_{application.id}",
                    )
                    submitted = st.form_submit_button("Save")
                    if submitted:
                        status_changed = status_value != current_status
                        notes_changed = notes_value != current_notes
                        if status_changed:
                            app_service.update_application_status(
                                application.id,
                                status_value,
                            )
                        if notes_changed:
                            app_service.update_application_notes(
                                application.id,
                                notes_value if notes_value else None,
                            )
                        if status_changed or notes_changed:
                            db_session.commit()
                            st.success("Application updated.")
                        else:
                            st.info("No changes to save.")

        for status_key in status_options:
            items = grouped.get(status_key, [])
            if not items:
                continue
            st.subheader(status_labels[status_key])
            for application in items:
                render_application_card(application)
                st.divider()

        if other_apps:
            st.subheader("Other")
            for application in other_apps:
                render_application_card(application)
                st.divider()


def render_stats_page() -> None:
    st.header("Stats")

    with SessionLocal() as db_session:
        top_skills = (
            db_session.query(
                Skill.skill_name,
                func.count(JobSkill.skill_id).label("job_count"),
            )
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .group_by(Skill.id)
            .order_by(func.count(JobSkill.skill_id).desc(), Skill.skill_name.asc())
            .limit(10)
            .all()
        )

    if not top_skills:
        st.info("No skills data available yet.")
        return

    st.subheader("Top Requested Skills")
    skill_counts = {skill_name: count for skill_name, count in top_skills}
    st.bar_chart(skill_counts)


def main() -> None:
    st.set_page_config(page_title="Job Tracker", layout="wide")

    page = st.sidebar.radio(
        "Navigation",
        ("Jobs", "Applications", "Stats"),
    )

    if page == "Jobs":
        render_jobs_page()
    elif page == "Applications":
        render_applications_page()
    else:
        render_stats_page()


if __name__ == "__main__":
    main()
