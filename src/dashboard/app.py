from typing import Iterable

import streamlit as st
from sqlalchemy import func

from src.database.models import Application, Job, JobSkill, Skill
from src.database.session import SessionLocal
from src.services.application_service import ApplicationService
from src.services.job_service import JobService


def render_jobs_page() -> None:
    st.header("Jobs")

    with SessionLocal() as db_session:
        job_service = JobService(db_session)
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

    rows = []
    for job in filtered_jobs:
        posted_date = getattr(job, "posted_date", None)
        skills = getattr(job, "skills", None) or []
        skill_names = sorted(
            {skill.skill_name for skill in skills if getattr(skill, "skill_name", None)}
        )
        rows.append(
            {
                "Track": False,
                "Company": getattr(job, "company", "") or "",
                "Title": getattr(job, "title", "") or "",
                "Location": getattr(job, "location", "") or "N/A",
                "Skills": ", ".join(skill_names) if skill_names else "N/A",
                "Posted Date": posted_date.isoformat() if posted_date else "N/A",
                "Link": getattr(job, "url", "") or "",
            }
        )

    edited_rows = st.data_editor(
        rows,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Track": st.column_config.CheckboxColumn("Track"),
            "Link": st.column_config.LinkColumn("Link"),
        },
        disabled=["Company", "Title", "Location", "Skills", "Posted Date", "Link"],
    )

    selected_count = len([row for row in edited_rows if row.get("Track")])
    st.caption(f"Selected {selected_count} jobs to track")

    selected_jobs = [
        job for job, row in zip(filtered_jobs, edited_rows) if row.get("Track")
    ]
    track_clicked = st.button(
        "Track Selected",
        type="primary",
        disabled=selected_count == 0,
    )

    if track_clicked and selected_jobs:
        with SessionLocal() as db_session:
            app_service = ApplicationService(db_session)
            try:
                created_count = 0
                for job in selected_jobs:
                    application = app_service.create_application(job.id)
                    if application in db_session.new:
                        created_count += 1
                db_session.commit()
            except Exception as exc:
                db_session.rollback()
                st.error(f"Failed to track applications: {exc}")
            else:
                if created_count:
                    st.success(
                        f"Tracked {created_count} application"
                        f"{'s' if created_count != 1 else ''}."
                    )
                else:
                    st.info("Selected jobs are already tracked.")


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
    st.set_page_config(title="Job Tracker", layout="wide")

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
