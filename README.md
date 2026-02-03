# Job Tracker

Job Tracker is a Python-based system for collecting job postings, tracking applications, and analyzing skill demand over time.

## Phase 1 Scope

- Configuration management with environment-backed settings
- SQLAlchemy models for jobs, applications, and skills
- Database session utilities

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Create a `.env` file with your database URL:

```bash
DATABASE_URL=sqlite:///./job_tracker.db
```

By default, the app uses `sqlite:///./job_tracker.db` if `DATABASE_URL` is not set.

## Notes

- Migrations are intentionally not run in Phase 1; only core infrastructure is defined.
