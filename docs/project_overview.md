Refined System Design
Project Scope
Primary Goal: Daily job monitoring for 15-20 targeted companies
Secondary Goal: Reusable scraping architecture for other content (coding articles, learning resources)
Technical Decisions
Data Layer
Database: SQLite initially (easy migration to PostgreSQL later)
Schema Design:
jobs table:

- id, company, title, description, skills_raw, url, posted_date, deadline, scraped_at, status

applications table:

- id, job_id (FK), applied_date, status, notes, last_updated

skills table:

- id, skill_name, category, frequency, priority

learning_goals table:

- id, skill_id (FK), target_date, progress, resources
Scraping Strategy
Approach: Pragmatic compliance

Respectful delays between requests (2-5s)
User-agent rotation
Session management
Error handling for blocks
robots.txt: assess per-site (LinkedIn strict, corporate career pages lenient)

Daily automation: Cron job/scheduled script
AI Integration
Local models (ollama/llama.cpp):

Job description summarization
Skill extraction from text
Learning path suggestions

API-based (future phases):

Complex project ideation
Cover letter assistance
Interview prep

Implementation Phases
Phase 1: Core Scraper (Week 1)

Build modular scraper (per-site adapters)
Database setup + initial schema
CSV export capability (backup/portability)

Phase 2: Application Tracker (Week 2)

Simple CLI or web interface
CRUD operations on applications
Status workflow management

Phase 3: Skill Pipeline (Week 3)

NLP skill extraction (regex + local LLM)
Skill frequency analysis
Gap identification dashboard

Phase 4: Learning System (Week 4)

Goal setting interface
Progress tracking
Local LLM for resource suggestions

Phase 5: Extensibility (Ongoing)

Generic scraper templates
Content categorization
Multi-domain knowledge base

Immediate Next Steps

Site analysis: Inspect LinkedIn/Seek HTML structure
Choose scraper library: Playwright (modern) vs BeautifulSoup+requests (lightweight)
Database setup: Create initial schema
Build first scraper: Single site proof-of-concept

Risk Mitigation

Rate limiting: Implement exponential backoff
Blocking: Fallback to manual CSV import
Data quality: Validation layer before DB insert
Maintenance: Version control scraper configs (selectors break)
