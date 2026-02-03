# Job Tracker

Job Tracker is a Python-based system for collecting job postings, tracking applications, and analyzing skill demand over time.

## Prerequisites

- Python 3.11+
- Ollama (for AI integration)
  ```bash
  # Pull the recommended model
  ollama pull codellama:7b
  ```

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browser:

```bash
playwright install chromium
```

4. (Optional) Create a `.env` file with your database URL:

```bash
DATABASE_URL=sqlite:///./job_tracker.db
```

By default, the app uses `sqlite:///./job_tracker.db` if `DATABASE_URL` is not set.

## Usage

### Run Scraper

```bash
python scripts/run_scraper.py --now --keywords "Python" --location "Remote"
```

### Run Dashboard

```bash
streamlit run src/dashboard/app.py
```

## Project Structure

```
job_tracker/
├── scripts/
│   └── run_scraper.py          # Main scraper entry point
├── src/
│   ├── dashboard/
│   │   └── app.py             # Streamlit dashboard application
│   ├── jobs/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── services.py        # Job scraping and processing services
│   │   └── schemas.py         # Pydantic schemas
│   ├── applications/
│   │   ├── models.py          # Application tracking models
│   │   └── services.py        # Application management services
│   └── ai/
│       ├── models.py           # AI/LLM integration models
│       └── services.py         # Skill extraction services
├── tests/
├── docs/
│   └── progress/
│       └── storyboard.md      # Project progress tracking
├── alembic/                   # Database migrations
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Notes

- Migrations are intentionally not run in Phase 1; only core infrastructure is defined.
