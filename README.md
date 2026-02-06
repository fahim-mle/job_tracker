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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

Use the `run_scraper.py` script to fetch jobs from LinkedIn.

```bash
python scripts/run_scraper.py --now --keywords "Software Engineer" --location "Brisbane"
```

**Available Flags:**

| Flag | Description | Default | Example |
| :--- | :--- | :--- | :--- |
| `--now` | Run the scraper immediately instead of waiting for the scheduled time. | `False` | `--now` |
| `--keywords` | Job search terms. | `"Python"` | `--keywords "Data Scientist"` |
| `--location` | Job search location. | `"Remote"` | `--location "Sydney"` |
| `--job-type` | Filter by job type (`remote`, `hybrid`, `onsite`). | `None` | `--job-type remote` |
| `--hour` | Hour to run the daily scheduled task (0-23). | `8` | `--hour 9` |
| `--minute` | Minute to run the daily scheduled task (0-59). | `0` | `--minute 30` |

### Run Dashboard

Start the Streamlit UI to view jobs and track applications.

```bash
streamlit run src/dashboard/app.py
```

## Project Structure

```txt
job_tracker/
├── scripts/
│   └── run_scraper.py          # Main scraper entry point
├── src/
│   ├── ai/
│   │   ├── llm_client.py       # Ollama integration
│   │   └── ...
│   ├── automation/
│   │   └── scheduler.py        # APScheduler configuration
│   ├── dashboard/
│   │   └── app.py              # Streamlit dashboard application
│   ├── database/
│   │   ├── models.py           # SQLAlchemy database models
│   │   └── session.py          # Database connection/session
│   ├── scrapers/
│   │   ├── base.py             # Base scraper class
│   │   └── linkedin.py         # LinkedIn implementation
│   ├── services/
│   │   ├── job_service.py      # Job CRUD and processing logic
│   │   ├── skill_service.py    # AI skill extraction logic
│   │   └── application_service.py # Application tracking logic
│   ├── config.py               # App configuration
│   └── logger.py               # Logging configuration
├── tests/                      # Test suite
├── docs/
│   ├── progress/               # Progress tracking logs
│   ├── archive/                # Archived docs
│   └── ...
├── alembic/                    # Database migrations
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Notes

- **Phase 1 Status**: LinkedIn scraping (deep) is implemented. Seek and Indeed are planned.
- **Database**: Migrations are managed via Alembic.
