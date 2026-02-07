# Task 002: Dashboard UX & Interaction Overhaul

**Status**: Done
**Type**: Improvement
**Created**: 2026-02-07

## 📝 User Feedback
> "The feature is not working properly... table should have two new columns, one for crud operations and one for details. You added details below the table, which increases my time... delaying the process."

## 🎯 Problem Statement
1.  **Split Focus**: The "View Details" button was below the table (or in a separate section), requiring users to select a row then scroll/look elsewhere.
2.  **Inefficient Workflow**: Users want to perform actions (Delete, Track, View) directly from the list row.
3.  **Missing "Columns"**: The user explicitly requested "Action Columns" in the table structure.

## 🛠️ Proposed Solution

### 1. UI Architecture Shift: Component-Based Rows
Streamlit `st.dataframe` does not support embedding action buttons (Track/Delete) inside cells. To achieve the "Two New Columns" requirement with *functional buttons*, we must switch from `st.data_editor` to a **Custom Row Rendering** loop.

**New Layout (Per Job):**
```text
| Company/Title (Col 1) | Location/Date (Col 2) | Actions (Col 3)      | Details (Col 4) |
|-----------------------|-----------------------|----------------------|-----------------|
| Google                | Remote                | [Track] [Archive]    | [ℹ️ Details]    |
| Software Engineer     | 2 days ago            | [Delete]             |                 |
```

### 2. Modal Dialog for Details
To solve the "checking twice" and scrolling issue, clicking **[ℹ️ Details]** will open a `st.dialog` (Modal).
-   **Content**: Full job description.
-   **Overlay**: Opens *over* the current page, preserving context.
-   **Actions**: "Track", "Archive", "Close" buttons inside the modal too.

### 3. Implementation Plan
-   **Pagination**: Since we are rendering rows manually, we must add pagination (e.g., 20 jobs per page) to prevent performance lag.
-   **State Management**: Ensure actions (Delete/Track) trigger a rerun and stay on the same page.

## 📋 Implementation Tasks

- [x] **Frontend**: Remove `st.data_editor`.
- [x] **Frontend**: Implement `render_job_row(job)` function using `st.columns`.
- [x] **Frontend**: Implement `show_job_details(job)` using `st.dialog`.
- [x] **Frontend**: Add Pagination controls (Prev/Next).
- [x] **Frontend**: Verify "Track", "Delete", "Archive" buttons work inline.

## 🧪 Verification Plan
-   [ ] Verify "Details" opens a modal overlay.
-   [ ] Verify "Delete" removes the row immediately.
-   [ ] Verify "Track" changes the button state (e.g., to "Tracked").
