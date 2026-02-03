from typing import Iterable

import streamlit as st

from src.database.session import SessionLocal
from src.services.job_service import JobService


def render_jobs_page() -> None:
    st.header("Jobs")

    with SessionLocal() as db_session:
        job_service = JobService(db_session)
        jobs = job_service.get_active_jobs()

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

    def filter_jobs(items: Iterable[object]) -> list[object]:
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

    filtered_jobs = filter_jobs(jobs)

    if not jobs:
        st.info("No active jobs found.")
        return

    st.caption(f"Showing {len(filtered_jobs)} of {len(jobs)} active jobs")

    rows = []
    for job in filtered_jobs:
        posted_date = getattr(job, "posted_date", None)
        rows.append(
            {
                "Track": False,
                "Company": getattr(job, "company", "") or "",
                "Title": getattr(job, "title", "") or "",
                "Location": getattr(job, "location", "") or "N/A",
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
        disabled=["Company", "Title", "Location", "Posted Date", "Link"],
    )

    selected_count = len([row for row in edited_rows if row.get("Track")])
    st.caption(f"Selected {selected_count} jobs to track")


def render_applications_page() -> None:
    st.header("Applications")
    st.write("Applications page placeholder.")


def render_stats_page() -> None:
    st.header("Stats")
    st.write("Stats page placeholder.")


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
