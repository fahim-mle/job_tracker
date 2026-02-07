# Task 001: Dashboard Detail View & CRUD Management

**Status**: Active
**Type**: Feature
**Created**: 2026-02-07

## 📝 User Request
>
> "Streamlit doesn't show description... most of the jobs are from all over the world... need a crud implementation... each job must have a details page... can change specific job posts tracking (applied, rejected, accepted)... need a directory for issues/bugs/updates."

## 🎯 Problem Statement

1. **Read-Only UI**: Users cannot interact with job data (view details, delete junk).
2. **Data Quality**: Database contains irrelevant global jobs (need cleanup tools).
3. **Workflow Gap**: No way to transition a job from "New" to "Applied" or "Rejected" easily.

## 🛠️ Proposed Solution

### 1. Backend Updates (`src/services/job_service.py`)

- Implement `get_job_by_id(job_id)`: Fetch full job details including description.
- Implement `delete_job(job_id)`: Hard delete for junk data.
- Implement `archive_job(job_id)`: Soft delete (status='archived') for non-relevant jobs.
- Implement `cleanup_jobs(criteria)`: Bulk delete utility (e.g., `location != 'Australia'`).

### 2. Frontend Overhaul (`src/dashboard/app.py`)

- **Master-Detail Layout**:
  - **List View**: Standard table with "View" button.
  - **Detail View**: Full page view of a single job.
- **Detail View Components**:
  - **Header**: Title, Company, Location, Posted Date.
  - **Description**: Rendered Markdown of the full description.
  - **Action Bar**:
    - `Track` (Move to Applications)
    - `Reject` (Hide/Archive)
    - `Delete` (Hard Remove)
- **Admin Sidebar**:
  - "Cleanup Database": Button to remove jobs not matching "Australia/Brisbane" (configurable).

## 📋 Implementation Tasks

- [x] **Backend**: Add `get_job`, `delete_job`, `archive_job` to `JobService`.
- [x] **Backend**: Add `delete_non_target_jobs` to `JobService` (for cleanup).
- [ ] **Frontend**: Refactor `app.py` to use `st.session_state` for navigation (List <-> Detail).
- [ ] **Frontend**: Implement Detail View with Description and Actions.
- [ ] **Frontend**: Add Admin/Cleanup section in Sidebar.

## 🧪 Verification Plan

- [ ] Verify clicking a job shows the full description.
- [ ] Verify "Delete" removes the job from the DB.
- [ ] Verify "Track" moves the job to the Applications tab.
