# Implementation Phases

This document outlines the step-by-step implementation plan for the Job Tracker project. We are following a Trunk-Based Development approach, meaning small, frequent commits to the main branch.

## **Phase 1: Core Infrastructure & Database (Week 1)**

**Goal:** Establish the project structure, database schema, and basic configuration.

### **Step 1.1: Project Setup**

- [ ] Initialize Python virtual environment (`venv`)
- [ ] Create `requirements.txt` / `pyproject.toml` with core dependencies:
  - `sqlalchemy`, `alembic` (Database)
  - `pydantic` (Data validation)
  - `python-dotenv` (Configuration)
  - `pytest`, `ruff` (Testing/Linting)
- [ ] Configure `pre-commit` hooks for linting and formatting.
- [ ] Create `src/config.py` for environment variable management.

### **Step 1.2: Database Implementation**

- [ ] Define SQLAlchemy models in `src/database/models.py`:
  - `Job`
  - `Application`
  - `Skill`
  - `JobSkill`
- [ ] Initialize Alembic for migrations (`alembic init alembic`).
- [ ] Create initial migration script (`alembic revision --autogenerate`).
- [ ] Create `src/database/session.py` for database connection handling (SQLite).
- [ ] Write a script `scripts/init_db.py` to create the database and seed initial test data.

### **Step 1.3: Basic Scraper Architecture**

- [ ] Create `src/scrapers/base.py` defining the `BaseScraper` abstract class.
  - Methods: `search_jobs()`, `scrape_job_details()`, `save_job()`
- [ ] Implement robust error handling and logging configuration (`src/logger.py`).

## **Phase 2: Scraping Implementation (Week 1-2)**

**Goal:** Build a functional scraper for LinkedIn (and potentially others) that respects rate limits.

### **Step 2.1: LinkedIn Scraper (Playwright)**

- [ ] Install Playwright browsers (`playwright install chromium`).
- [ ] Implement `LinkedInScraper` in `src/scrapers/linkedin.py`.
  - [ ] Login handling (if necessary/safe) or public search access.
  - [ ] Search result pagination.
  - [ ] Job detail extraction (title, company, description, date, URL).
- [ ] Implement `RateLimiter` utility to ensure 3-5s delays.

### **Step 2.2: Data Pipeline**

- [ ] Create a service layer `src/services/job_service.py` to handle logic between scraper and DB.
- [ ] Implement "Upsert" logic: avoid duplicates, update existing jobs if status changes.
- [ ] Add raw HTML storage for future AI processing.

### **Step 2.3: Automation**

- [ ] Create `src/automation/scheduler.py` using `APScheduler`.
- [ ] Configure daily job (e.g., 08:00 AM) to run the scraper.
- [ ] Write `scripts/run_scraper.py` entry point.

## **Phase 3: Dashboard & Application Tracking (Week 2-3)**

**Goal:** User interface for viewing jobs and managing applications.

### **Step 3.1: Streamlit Dashboard**

- [ ] Set up `src/dashboard/app.py`.
- [ ] Create "Jobs" tab:
  - List view of active jobs.
  - Filters (Company, Date, Keywords).
- [ ] Create "Applications" tab:
  - Kanban board or list view of application statuses.
  - Form to update status/notes.

### **Step 3.2: Application Management**

- [ ] Implement backend logic for moving applications between states (Applied -> Interview -> Offer).
- [ ] Add analytics widgets (Applications per week, Response rate).

## **Phase 4: AI Integration (Week 3-4)**

**Goal:** Integrate Local LLM for intelligent skill extraction.

### **Step 4.1: LLM Setup**

- [ ] Install and configure `ollama` python client.
- [ ] Create `src/ai/llm_client.py` wrapper.
- [ ] Pull suitable model (e.g., `llama3` or `mistral`).

### **Step 4.2: Skill Extraction**

- [ ] Implement `SkillExtractor` class.
- [ ] Design prompt for extracting skills, experience level, and salary from job descriptions.
- [ ] Update `JobService` to process new jobs through `SkillExtractor` automatically.

### **Step 4.3: Learning System**

- [ ] Create logic to compare "User Skills" vs "Job Required Skills".
- [ ] Visualize skill gaps in the dashboard.
- [ ] Implement `LearningPathGenerator` using LLM.
- [ ] Suggest resources for missing high-frequency skills.
