# Job Tracker - MASTER ROADMAP

## Project Vision

A **Personalized AI Recruiter** focused on the Australian market (specifically Brisbane) that automates job finding, relevance scoring, and skill gap analysis.

**Goal**: Transform job searching from a manual, time-consuming process into an intelligent, automated system that finds the right opportunities for you.

**Key Platforms**:

- LinkedIn (existing)
- Seek (new)
- Indeed (new)

## Current System Status

### Core Infrastructure

- **Python**: 3.12+
- **Database**: SQLite with SQLAlchemy ORM
- **Migrations**: Alembic for database schema management
- **Scheduling**: `apscheduler` for automated tasks

### Existing Components

- **Scrapers**: LinkedIn Basic card scraping working with Job Type/Location/Keyword filters
- **UI**: Streamlit Dashboard with Jobs list, Application tracking, Basic stats
- **AI**: Local Ollama integration structure exists (CodeLlama/Llama3) but limited by lack of full job description data

### Current Limitations

- Only summary data from LinkedIn (no full job descriptions)
- No user profile/context storage
- No relevance scoring engine
- No skill gap analysis

## Detailed Future Roadmap

### Phase 1: Deep Scraping (The Data Foundation)

**Objective**: Fetch full job description text, not just summaries

**Why this matters**: Without complete job descriptions, the AI cannot perform meaningful analysis or relevance scoring.

**Tasks**:

- Upgrade LinkedIn scraper to visit detail pages and extract full descriptions
- Implement Seek scraper for Australian job market
- Implement Indeed scraper for additional coverage
- Standardize job data structure across all platforms
- Add error handling and rate limiting for all scrapers

**Technical Notes**:

- Use `apscheduler` for automated scraping runs
- Store raw HTML for debugging and future improvements
- Implement retry logic for failed requests

### Phase 2: Digital Twin (User Profile)

**Objective**: Store user context and preferences

**Why this matters**: The system needs to understand who you are to find relevant jobs for you.

**Tasks**:

- Create `Profile` model with fields: name, location, experience, education, skills, preferences
- Implement CV/Resume uploader (PDF/DOCX support)
- Use LLM to parse CV into structured skills/experience
- Create user preferences system (job types, salary ranges, locations)
- Implement profile editing interface in Streamlit

**Database Schema**:

```sql
CREATE TABLE profile (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    experience_years INTEGER,
    education_level TEXT,
    skills TEXT, -- JSON array of skills
    preferences TEXT, -- JSON object of preferences
    cv_text TEXT, -- Parsed CV content
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Phase 3: Relevance Engine (The Brain)

**Objective**: Sort jobs by fit, not date

**Why this matters**: Current systems show jobs by recency, but the best jobs for you might be older posts that perfectly match your profile.

**Tasks**:

- Implement `MatchService` class
- Compare `Job.description` vs `Profile` using semantic similarity
- Calculate `relevance_score` (0-100)
- Create Categories: Most Relevant (80-100), Relevant (50-79), Mismatch (0-49)
- Store match scores in database
- Implement relevance-based job sorting in UI

**Match Algorithm**:

- Use semantic similarity (cosine similarity on embeddings)
- Weight factors: skills match, experience level, location, job type
- Consider industry keywords and technologies
- Handle synonyms and related terms

**Database Schema**:

```sql
CREATE TABLE match_score (
    id INTEGER PRIMARY KEY,
    job_id INTEGER NOT NULL,
    profile_id INTEGER NOT NULL,
    relevance_score INTEGER CHECK(relevance_score >= 0 AND relevance_score <= 100),
    category TEXT CHECK(category IN ('Most Relevant', 'Relevant', 'Mismatch')),
    explanation TEXT, -- AI-generated reasoning
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(job_id) REFERENCES job(id),
    FOREIGN KEY(profile_id) REFERENCES profile(id)
);
```

### Phase 4: Market Analyst (Skill Gaps)

**Objective**: Identify missing skills and market demands

**Why this matters**: Know what skills you need to develop to qualify for your target jobs.

**Tasks**:

- Aggregate top skills from "Most Relevant" jobs
- Compare with User Profile skills
- Highlight gaps with priority levels
- Suggest learning resources for missing skills
- Track skill demand trends over time
- Generate skill development roadmap

**Analysis Features**:

- Top 10 missing skills across relevant jobs
- Skill frequency analysis
- Emerging skill trends
- Competitive skill analysis

## Technical Implementation Details

### Database Extensions Required

1. **Profile Table**: Store user information and parsed CV data
2. **MatchScore Table**: Store relevance scores and categories
3. **Skill Table**: (Optional) Store standardized skill definitions
4. **LearningResource Table**: (Optional) Store skill development resources

### AI Integration

- **Local Ollama**: Use for all LLM operations (privacy-focused)
- **Embedding Models**: Use sentence transformers for semantic similarity
- **CV Parsing**: Use specialized models for document understanding
- **Skill Extraction**: Use named entity recognition for skill identification

### Scheduling Strategy

- **Daily**: Scrape new jobs from all platforms
- **Weekly**: Recalculate relevance scores for existing jobs
- **Monthly**: Update skill trend analysis
- **On-demand**: Recalculate when user profile changes

### Error Handling and Monitoring

- Implement comprehensive logging for all scrapers
- Add health checks for database and AI services
- Create monitoring dashboard for system status
- Implement alerting for scraper failures

## Success Metrics

### User Experience

- Time saved in job searching
- Quality of job matches (user feedback)
- Skill gap identification accuracy

### Technical Performance

- Scraper success rate
- Relevance score accuracy
- System uptime and reliability
- Processing speed for large job datasets

### Business Impact

- Number of relevant jobs found vs manual searching
- Skill development progress tracking
- Career advancement opportunities identified

## Next Steps

1. **Immediate**: Complete Phase 1 (Deep Scraping)
2. **Short-term**: Implement Phase 2 (Digital Twin)
3. **Medium-term**: Build Phase 3 (Relevance Engine)
4. **Long-term**: Develop Phase 4 (Market Analyst)

**Priority**: Focus on data quality first, then AI intelligence, then user experience.

---

*This document serves as the single source of truth for the Job Tracker project. All development decisions should align with this roadmap.*
