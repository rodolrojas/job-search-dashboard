# How the real job-search agent works

The implementation is intentionally split at trust boundaries so it can be
read, tested, and changed without treating one model response as truth.

## Source map

- `backend/job_search_agent.py` contains the orchestration loop, OpenAI tool
  boundary, Pydantic response schemas, hard filters, URL validator, scoring
  normalization, and JSON persistence.
- `backend/agent_service.py` runs the agent in a background thread and records
  an event stream for the UI.
- `backend/prompts/job_search_agent.md` is the research policy supplied to the
  model. It is versioned alongside the code.
- `backend/app.py` exposes endpoints to inspect configuration, start a run, and
  poll progress.
- `components/agent-panel.tsx` renders the run controls and event timeline.

## The loop

```text
candidate profile + history + prompt
                 │
                 ▼
       1. deterministic plan
       (bounded search queries)
                 │
                 ▼
       2. OpenAI Responses API
          + built-in web_search
          + Pydantic output schema
                 │
                 ▼
       3. application-owned checks
          dedupe → history exclusion
          → 30-day date window
          → direct HTTP URL check
                 │
                 ▼
       4. structured AI scoring
          six explicit score categories
          + one known resume variant
                 │
                 ▼
       5. deterministic persistence
          ranked job_search_*.json
          → repository → dashboard
```

The model is allowed to research and judge semantic fit. It is not allowed to
write files, change history, submit forms, send email, use credentials, or
decide whether a URL actually responded. Those capabilities remain in ordinary
application code.

## Running it

1. Copy `backend/.env.example` to `backend/.env`.
2. Set `OPENAI_API_KEY` and optionally change `OPENAI_MODEL`.
3. Start the Flask API and frontend as described in the README.
4. Select **Run AI search** in the Inspectable AI agent panel.
5. Watch the phases update. On completion the new JSON file becomes the latest
   dashboard run.

Useful limits:

```dotenv
AGENT_MAX_SEARCH_QUERIES=4
AGENT_MAX_RESULTS=15
```

Smaller values make learning runs faster and cheaper. Search-tool and model
usage is billed by the API project associated with the key.

## Why it is an agent

This is more than one text-generation call: the system has a goal, constructs
a bounded plan, invokes an external research tool, observes results, applies
application-owned validations, makes a second structured judgment, changes
durable state, and exposes the execution trace. The orchestration is explicit
Python, so each capability and failure mode is inspectable.

## Limitations

- Direct HTTP checks cannot prove that every JavaScript-heavy page is still
  accepting applications. Ambiguous or blocked pages are rejected or reported.
- The server does not inherit browser login sessions. Login walls are never
  bypassed.
- The in-process registry assumes one Flask process. A production system with
  multiple replicas should replace it with a durable queue such as Celery/RQ
  plus Redis or a database-backed job table.
- The agent prepares recommendations only. It never applies to jobs.
