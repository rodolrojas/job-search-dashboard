# Role Radar architecture

```mermaid
flowchart LR
  User[Candidate] --> UI[Next.js dashboard]
  UI --> Store[Zustand state]
  Store --> Client[Axios API client]
  Client --> API[Flask REST API]

  subgraph Legacy[One-time legacy import]
    Runs[Job-search run JSON files]
    Profile[Professional profile JSON]
    History[Applications and exclusions JSON]
    Resumes[Six resume variants and PDFs]
  end

  Runs --> Import[Idempotent bootstrap importer]
  Profile --> Import
  History --> Import
  Import --> PG[(PostgreSQL)]
  API --> Repo[SQLAlchemy repository]
  Repo --> PG
  Repo --> Resumes

  API --> Runner[Agent run registry]
  Runner --> Agent[Job-search orchestrator]
  Agent --> Plan[Bounded query plan]
  Agent --> Runtime[Codex runtime adapter]
  Runtime -->|local backend| Codex[Host Codex CLI in read-only mode]
  Runtime -->|Docker backend| Bridge[Authenticated host bridge]
  Bridge --> Codex
  Codex --> Web[Live web search]
  Agent --> Validate[URL, date, history validation]
  Codex --> Score[Schema-validated profile scoring]
  Agent --> Persist[Transactional search-run persistence]
  Persist --> PG
  Runner --> Audit[Durable run and event audit]
  Audit --> PG
  API --> Cover[Cover-letter agent]
  Cover --> Runtime
  Cover --> Drafts[Local deterministic fallback]
  Cover --> PG
  Cover --> Output[Optional text-file export]

  Application[Application assistant] --> Guardrail[Prepare only; never auto-submit]
  API --> Application
```

## Responsibility boundaries

- The Next.js frontend presents the shortlist, composes filters, and sends explicit user actions to the API.
- The Flask API owns data normalization, durable status changes, cover-letter generation, and access to candidate profile data.
- PostgreSQL is the authoritative store for all dynamic application data.
  Existing workspace JSON files are a one-time bootstrap source when their
  destination tables are empty.
- Search runs and their ranked listings are modeled separately, preserving a
  job's history across multiple runs while keeping one canonical job record.
- The job-search and cover-letter agents invoke the signed-in host Codex CLI
  through `codex exec`. Prompts travel over stdin and final results are
  constrained by generated Pydantic JSON Schemas. Neither workflow reads an
  OpenAI API key.
- When Flask runs in Docker, its runtime adapter sends only the prompt, output
  schema, and search flag to an authenticated bridge on the host. The bridge
  does not accept arbitrary commands, paths, or sandbox settings.
- Codex runs with a read-only sandbox through either direct CLI mode or the
  host bridge. Ordinary Python code still owns query limits, history exclusion,
  URL/date validation, score normalization, resume allowlisting, and
  persistence.
- Every agent phase is persisted to PostgreSQL and exposed to the frontend.
  Interrupted runs are marked failed after a backend restart, keeping the
  execution trace inspectable without exposing hidden reasoning.
- Automated application submission is intentionally outside the system boundary. The application assistant may prepare materials, but never submits on the candidate's behalf.
