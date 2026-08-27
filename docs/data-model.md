# PostgreSQL data model

PostgreSQL is Role Radar's source of truth for dynamic data. SQLAlchemy models
live in `backend/models.py`; the equivalent PostgreSQL bootstrap DDL is in
`backend/schema.sql`.

```mermaid
erDiagram
  CANDIDATE_PROFILES ||--o{ RESUME_VARIANTS : owns
  JOB_SEARCH_RUNS ||--o{ JOB_RUN_LISTINGS : contains
  JOBS ||--o{ JOB_RUN_LISTINGS : appears_in
  JOBS ||--o| JOB_APPLICATIONS : applied_as
  JOBS ||--o| JOB_EXCLUSIONS : excluded_as
  JOBS ||--o{ COVER_LETTERS : receives
  AGENT_RUNS ||--o{ AGENT_RUN_EVENTS : records

  JOB_SEARCH_RUNS {
    varchar id PK
    date report_date
    integer run_number
    jsonb summary
    jsonb comparison
    jsonb raw_json
  }
  JOBS {
    varchar id PK
    varchar role
    varchar company
    varchar location
    text offer_url
    date first_seen_on
    date last_seen_on
  }
  JOB_RUN_LISTINGS {
    bigint id PK
    varchar run_id FK
    varchar job_id FK
    integer rank
    integer score
    jsonb score_breakdown
    jsonb raw_json
  }
  CANDIDATE_PROFILES {
    integer id PK
    varchar display_name
    jsonb raw_json
  }
  RESUME_VARIANTS {
    varchar key PK
    integer profile_id FK
    varchar pdf_filename
    jsonb raw_json
  }
  JOB_APPLICATIONS {
    varchar id PK
    varchar job_id FK
    varchar status
    date applied_on
    jsonb raw_json
  }
  JOB_EXCLUSIONS {
    varchar id PK
    varchar job_id FK
    varchar status
    date excluded_on
    boolean keep_out
    jsonb raw_json
  }
  COVER_LETTERS {
    varchar id PK
    varchar job_id FK
    varchar resume_variant
    text content
    varchar mode
    timestamptz created_at
  }
  AGENT_RUNS {
    varchar id PK
    varchar status
    varchar phase
    jsonb result
    timestamptz created_at
  }
  AGENT_RUN_EVENTS {
    bigint id PK
    varchar run_id FK
    integer sequence
    varchar phase
    jsonb details
  }
```

## Modeling choices

- `jobs` stores the canonical role identity and current stable fields.
- `job_search_runs` stores report-level summaries, comparisons, issues, and
  agent metadata.
- `job_run_listings` is the historical many-to-many edge between jobs and
  search runs. Its unique `(run_id, job_id)` constraint prevents duplicates in
  one run while preserving rank and score changes over time.
- Applications and exclusions allow at most one active record per job through
  a unique `job_id` constraint.
- JSONB retains source-specific evidence without sacrificing normalized keys,
  relationships, dates, or indexes used by the application.
- Cover-letter content and agent events are durable; generated text files are
  exports, not the source of truth.

## Bootstrap behavior

On an empty database, the backend imports the candidate profile, resume
variants, every historical search run, applications, and exclusions from the
workspace JSON files. Each domain is imported only when its destination table
is empty, so restarting containers cannot overwrite newer PostgreSQL data.
