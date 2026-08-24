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

  API --> Recommendation[Recommendation agent]
  API --> Screening[Resume screening and variant selection]
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
- The recommendation and resume-screening layers use verified scores and resume variants already present in the run data.
- Automated application submission is intentionally outside the system boundary. The application assistant may prepare materials, but never submits on the candidate's behalf.

