# Job Tracker Technical Implementation Plan

## **Technical Stack & Architecture**

### **Core Technologies**
- **Backend**: Python 3.11+ (async/await support)
- **Web Scraping**: Playwright (modern JS-heavy sites) + requests + BeautifulSoup (fallback)
- **Database**: SQLite with SQLAlchemy ORM
- **Task Scheduling**: APScheduler + cron for daily automation
- **AI Integration**: Ollama (local LLM) + OpenAI API (fallback)
- **Frontend**: Streamlit (rapid prototyping) → FastAPI + React (production)

### **Development Workflow**
```
project/
├── src/
│   ├── scrapers/           # Platform-specific scrapers
│   ├── database/          # Models & migrations
│   ├── ai/               # Local LLM integration
│   ├── api/              # REST endpoints
│   └── automation/       # Scheduled tasks
├── config/               # Configuration management
├── tests/               # Unit/integration tests
├── scripts/             # Deployment & maintenance
└── docs/               # Project documentation
```

## **Phase 1: Core Infrastructure (Week 1)**

### **Database Schema Design**
```sql
-- jobs table
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    skills_raw TEXT,  -- JSON array
    url TEXT UNIQUE,
    posted_date DATE,
    deadline DATE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    source_platform TEXT,
    raw_html TEXT  -- For AI processing
);

-- applications table
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER REFERENCES jobs(id),
    applied_date DATE,
    status TEXT DEFAULT 'applied',
    notes TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- skills table
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT UNIQUE,
    category TEXT,
    frequency INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 1
);

-- job_skills junction table
CREATE TABLE job_skills (
    job_id INTEGER REFERENCES jobs(id),
    skill_id INTEGER REFERENCES skills(id),
    confidence_score REAL
);
```

### **Scraper Architecture**
```python
# Base scraper class
class BaseScraper:
    def __init__(self, config):
        self.session = requests.Session()
        self.playwright = None
        self.rate_limiter = AsyncRateLimiter()
    
    async def scrape(self, search_params):
        # Platform-specific implementation
        pass

# LinkedIn-specific scraper
class LinkedInScraper(BaseScraper):
    async def search_jobs(self, keywords, location):
        # Playwright for JS-heavy content
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Respect robots.txt + rate limiting
```

### **Environment Setup**
```bash
# Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Core dependencies
pip install playwright requests beautifulsoup4 sqlalchemy
pip install apscheduler streamlit fastapi uvicorn
pip install pandas matplotlib seaborn
pip install ollama openai python-dotenv

# Development tools
pip install pytest black ruff pre-commit
```

## **Phase 2: Scraping Implementation (Week 1-2)**

### **LinkedIn Scraper Strategy**
1. **Respectful Approach**:
   - 3-5 second delays between requests
   - User-agent rotation
   - Session persistence
   - robots.txt compliance check

2. **Data Extraction**:
   - Job titles, companies, descriptions
   - Required skills (AI-powered extraction)
   - Posting dates, application deadlines
   - Location, salary (if available)

3. **Error Handling**:
   - Exponential backoff for rate limits
   - CAPTCHA detection & manual fallback
   - Proxy rotation (future enhancement)

### **Daily Automation Setup**
```python
# cron job: 0 8 * * * /path/to/venv/bin/python /path/to/scripts/daily_scrape.py

class DailyScraper:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    async def run_daily_scrape(self):
        # Target companies from config
        scrapers = [LinkedInScraper(), CompanyScraper()]
        
        for scraper in scrapers:
            await scraper.scrape_target_companies()
            await self.rate_limiter.wait()
```

## **Phase 3: AI Integration (Week 2-3)**

### **Local LLM Setup**
```python
# Ollama integration
class SkillExtractor:
    def __init__(self):
        self.client = Client(host='http://localhost:11434')
    
    async def extract_skills(self, job_description):
        prompt = f"""
        Extract technical skills from this job description:
        {job_description}
        
        Return JSON format: {{"skills": ["skill1", "skill2"], "confidence": 0.8}}
        """
        
        response = await self.client.chat(
            model='llama3.2',
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response['message']['content'])
```

### **Skill Analysis Pipeline**
1. **Extraction**: Local LLM processes job descriptions
2. **Normalization**: Standardize skill names (e.g., "JS" → "JavaScript")
3. **Frequency Analysis**: Track demand trends
4. **Gap Identification**: Compare with user's current skills

## **Phase 4: Application Tracking (Week 3)**

### **Streamlit Dashboard**
```python
# main dashboard features
def main():
    st.title("Job Tracker Dashboard")
    
    # Tabs: Jobs, Applications, Skills, Learning
    tab1, tab2, tab3, tab4 = st.tabs(["Jobs", "Applications", "Skills", "Learning"])
    
    with tab1:
        # Filterable job listings
        # AI-powered skill matching
        # Application status tracking
    
    with tab3:
        # Skill frequency charts
        # Learning gap analysis
        # Progress tracking
```

### **API Layer (Future)**
```python
# FastAPI endpoints
@app.get("/jobs")
async def get_jobs(filters: JobFilters):
    return await job_service.get_filtered_jobs(filters)

@app.post("/applications")
async def create_application(application: ApplicationCreate):
    return await application_service.create(application)
```

## **Phase 5: Learning System (Week 4)**

### **Learning Path Generation**
```python
class LearningPathGenerator:
    async def generate_path(self, skill_gaps):
        prompt = f"""
        Create learning path for these skills: {skill_gaps}
        
        For each skill, suggest:
        1. Online courses (free/paid)
        2. Project ideas
        3. Time estimation
        4. Prerequisites
        
        Return structured JSON with priorities
        """
        
        response = await self.local_llm.generate(prompt)
        return self.parse_learning_path(response)
```

## **Database Migration Strategy**

### **SQLite → PostgreSQL Path**
```python
# Migration script
alembic revision --autogenerate -m "Add job_skills table"
alembic upgrade head

# Data export for portability
def export_to_csv():
    jobs_df = pd.read_sql("SELECT * FROM jobs", engine)
    applications_df = pd.read_sql("SELECT * FROM applications", engine)
    
    jobs_df.to_csv("jobs_backup.csv", index=False)
    applications_df.to_csv("applications_backup.csv", index=False)
```

## **Testing & Quality Assurance**

### **Test Strategy**
```python
# Unit tests
class TestLinkedInScraper:
    async def test_job_extraction(self):
        scraper = LinkedInScraper(test_config)
        jobs = await scraper.scrape_mock_page()
        assert len(jobs) > 0
        assert all(job.get('title') for job in jobs)

# Integration tests
class TestSkillExtraction:
    async def test_skill_extraction_pipeline(self):
        extractor = SkillExtractor()
        skills = await extractor.extract_skills(sample_description)
        assert isinstance(skills, dict)
        assert 'skills' in skills
```

## **Deployment & Monitoring**

### **Local Development Setup**
```bash
# Pre-commit hooks
pre-commit install

# Development server
uvicorn src/api/main:app --reload --port 8000
streamlit run src/dashboard/app.py

# Scheduled jobs
python -m src.automation.daily_scrape
```

### **Monitoring & Logging**
```python
# Structured logging
import structlog
logger = structlog.get_logger()

async def scrape_with_monitoring():
    logger.info("Starting daily scrape", timestamp=datetime.now())
    try:
        # Scrape logic
        logger.info("Scrape completed", jobs_found=len(jobs))
    except Exception as e:
        logger.error("Scrape failed", error=str(e))
```

## **Risk Mitigation Enhancements**

### **Scalability Considerations**
1. **Rate Limiting**: Token bucket algorithm
2. **Caching**: Redis for frequent queries
3. **Database**: Connection pooling, query optimization
4. **Monitoring**: Prometheus + Grafana (future)

### **Data Quality**
```python
# Validation layer
class JobValidator:
    def validate(self, job_data):
        required_fields = ['title', 'company', 'description']
        return all(field in job_data for field in required_fields)
    
    def sanitize(self, job_data):
        # HTML sanitization, text normalization
        job_data['description'] = bleach.clean(job_data['description'])
        return job_data
```

## **Immediate Action Items**

1. **Setup Development Environment**
   - Create virtual environment
   - Install core dependencies
   - Initialize git repository with pre-commit hooks

2. **Database Initialization**
   - Create SQLite database with schema
   - Set up Alembic for migrations
   - Create initial test data

3. **Build First Scraper**
   - LinkedIn scraper proof-of-concept
   - Implement rate limiting and error handling
   - Test with limited data set

4. **Basic Dashboard**
   - Streamlit prototype for data visualization
   - Simple job listing display
   - Basic filtering capabilities

This comprehensive plan provides a clear path from concept to production-ready job tracking system with modern Python practices, AI integration, and sustainable scraping strategies.