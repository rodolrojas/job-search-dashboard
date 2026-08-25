# Role Radar architecture

```mermaid
flowchart LR
  User[Candidate] --> UI[Next.js dashboard]
  UI --> Store[Zustand state]
  Store --> Client[Axios API client]
  Client --> API[Flask REST API]

  subgraph Data[Existing workspace data]
    Runs[Job-search run JSON files]
    Profile[Professional profile JSON]
    History[Applications and exclusions JSON]
    Resumes[Six resume variants and PDFs]
  end

  API --> Repo[JSON repository]
  Repo --> Runs
  Repo --> Profile
  Repo --> History
  Repo --> Resumes
  Repo --> ORM[(SQLite / SQLAlchemy index)]

  API --> Runner[Agent run registry]
  Runner --> Agent[Job-search orchestrator]
  Agent --> Plan[Bounded query plan]
  Agent --> Web[OpenAI web_search tool]
  Agent --> Validate[URL, date, history validation]
  Agent --> Score[Structured profile scoring]
  Agent --> Persist[Atomic job-search JSON run]
  Persist --> Runs
  API --> Cover[Cover-letter agent]
  Cover --> Responses[OpenAI Responses API]
  Cover --> Drafts[Local deterministic fallback]
  Cover --> Output[Generated cover-letter files]

  Application[Application assistant] --> Guardrail[Prepare only; never auto-submit]
  API --> Application
```

## Responsibility boundaries

- The Next.js frontend presents the shortlist, composes filters, and sends explicit user actions to the API.
- The Flask API owns data normalization, durable status changes, cover-letter generation, and access to candidate profile data.
- Existing JSON files remain the portable source of truth. SQLAlchemy builds a queryable local index without replacing them.
- The job-search orchestrator makes research calls through the OpenAI Responses
  API, but ordinary Python code owns query limits, history exclusion, URL/date
  validation, score normalization, resume allowlisting, and persistence.
- Every agent phase is recorded in an in-process run registry and exposed to the
  frontend. This makes the execution trace inspectable without exposing hidden
  reasoning.
- Automated application submission is intentionally outside the system boundary. The application assistant may prepare materials, but never submits on the candidate's behalf.
