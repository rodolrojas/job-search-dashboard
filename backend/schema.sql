BEGIN;

CREATE TABLE IF NOT EXISTS candidate_profiles (
    id INTEGER PRIMARY KEY,
    display_name VARCHAR(180) NOT NULL,
    email VARCHAR(320),
    location VARCHAR(240),
    raw_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resume_variants (
    key VARCHAR(80) PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    label VARCHAR(160) NOT NULL,
    headline TEXT NOT NULL DEFAULT '',
    pdf_filename VARCHAR(240) NOT NULL,
    raw_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS job_search_runs (
    id VARCHAR(240) PRIMARY KEY,
    source_file VARCHAR(240) NOT NULL UNIQUE,
    report_date DATE NOT NULL,
    run_number INTEGER NOT NULL DEFAULT 0,
    timezone VARCHAR(80),
    summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    top_three JSONB NOT NULL DEFAULT '[]'::jsonb,
    comparison JSONB NOT NULL DEFAULT '{}'::jsonb,
    issues JSONB NOT NULL DEFAULT '[]'::jsonb,
    blocked_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    agent_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    raw_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(180) PRIMARY KEY,
    role VARCHAR(240) NOT NULL,
    company VARCHAR(180) NOT NULL,
    location VARCHAR(240) NOT NULL,
    offer_url TEXT,
    contact_email VARCHAR(320),
    recruiter_or_careers_url TEXT,
    salary VARCHAR(240) NOT NULL DEFAULT 'Undisclosed',
    employment_type VARCHAR(80) NOT NULL DEFAULT 'Full-time',
    first_seen_on DATE,
    last_seen_on DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_run_listings (
    id BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(240) NOT NULL REFERENCES job_search_runs(id) ON DELETE CASCADE,
    job_id VARCHAR(180) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    rank INTEGER,
    posted_on DATE,
    posted_evidence TEXT,
    score INTEGER NOT NULL DEFAULT 0,
    score_breakdown JSONB NOT NULL DEFAULT '{}'::jsonb,
    suggested_resume VARCHAR(240) NOT NULL DEFAULT 'Rodolfo_Rojas_General_CV.pdf',
    strategic_note TEXT,
    live_check TEXT,
    source_name VARCHAR(240),
    requirements_summary TEXT,
    is_new BOOLEAN NOT NULL DEFAULT FALSE,
    raw_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT uq_job_run_listings_run_job UNIQUE (run_id, job_id)
);

CREATE TABLE IF NOT EXISTS job_applications (
    id VARCHAR(220) PRIMARY KEY,
    job_id VARCHAR(180) NOT NULL UNIQUE REFERENCES jobs(id) ON DELETE CASCADE,
    company VARCHAR(180) NOT NULL,
    role VARCHAR(240) NOT NULL,
    location VARCHAR(240),
    job_url TEXT,
    source_file VARCHAR(240),
    source_original_rank INTEGER,
    status VARCHAR(80) NOT NULL,
    applied_on DATE,
    status_updated_on DATE,
    next_action TEXT,
    next_action_date DATE,
    contacts JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes JSONB NOT NULL DEFAULT '[]'::jsonb,
    raw_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_exclusions (
    id VARCHAR(220) PRIMARY KEY,
    job_id VARCHAR(180) NOT NULL UNIQUE REFERENCES jobs(id) ON DELETE CASCADE,
    company VARCHAR(180) NOT NULL,
    role VARCHAR(240) NOT NULL,
    job_url TEXT,
    source_file VARCHAR(240),
    source_original_rank INTEGER,
    status VARCHAR(80) NOT NULL DEFAULT 'user_removed',
    reason TEXT NOT NULL,
    keep_out BOOLEAN NOT NULL DEFAULT TRUE,
    excluded_on DATE,
    raw_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cover_letters (
    id VARCHAR(32) PRIMARY KEY,
    job_id VARCHAR(180) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    resume_variant VARCHAR(80) NOT NULL,
    content TEXT NOT NULL,
    mode VARCHAR(40) NOT NULL,
    warning TEXT,
    filename VARCHAR(260) NOT NULL,
    saved_to TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id VARCHAR(32) PRIMARY KEY,
    status VARCHAR(40) NOT NULL,
    phase VARCHAR(80) NOT NULL,
    message TEXT NOT NULL,
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_run_events (
    id BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(32) NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    phase VARCHAR(80) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_agent_run_events_run_sequence UNIQUE (run_id, sequence)
);

CREATE INDEX IF NOT EXISTS ix_job_search_runs_report_date ON job_search_runs(report_date);
CREATE INDEX IF NOT EXISTS ix_job_search_runs_latest ON job_search_runs(report_date, run_number);
CREATE INDEX IF NOT EXISTS ix_jobs_role ON jobs(role);
CREATE INDEX IF NOT EXISTS ix_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS ix_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS ix_jobs_last_seen_on ON jobs(last_seen_on);
CREATE INDEX IF NOT EXISTS ix_job_run_listings_run_id ON job_run_listings(run_id);
CREATE INDEX IF NOT EXISTS ix_job_run_listings_job_id ON job_run_listings(job_id);
CREATE INDEX IF NOT EXISTS ix_job_run_listings_posted_on ON job_run_listings(posted_on);
CREATE INDEX IF NOT EXISTS ix_job_run_listings_score ON job_run_listings(score);
CREATE INDEX IF NOT EXISTS ix_job_run_listings_run_rank ON job_run_listings(run_id, rank);
CREATE INDEX IF NOT EXISTS ix_job_run_listings_run_score ON job_run_listings(run_id, score);
CREATE INDEX IF NOT EXISTS ix_job_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS ix_job_applications_applied_on ON job_applications(applied_on);
CREATE INDEX IF NOT EXISTS ix_job_applications_source_file ON job_applications(source_file);
CREATE INDEX IF NOT EXISTS ix_job_exclusions_status ON job_exclusions(status);
CREATE INDEX IF NOT EXISTS ix_job_exclusions_excluded_on ON job_exclusions(excluded_on);
CREATE INDEX IF NOT EXISTS ix_job_exclusions_source_file ON job_exclusions(source_file);
CREATE INDEX IF NOT EXISTS ix_cover_letters_job_id ON cover_letters(job_id);
CREATE INDEX IF NOT EXISTS ix_cover_letters_created_at ON cover_letters(created_at);
CREATE INDEX IF NOT EXISTS ix_agent_runs_status ON agent_runs(status);
CREATE INDEX IF NOT EXISTS ix_agent_runs_created_at ON agent_runs(created_at);
CREATE INDEX IF NOT EXISTS ix_agent_run_events_run_id ON agent_run_events(run_id);

COMMIT;
