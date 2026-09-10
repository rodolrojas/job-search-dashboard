# How the real job-search agent works

The implementation is intentionally split at trust boundaries so it can be
read, tested, and changed without treating one model response as truth.

## Source map

- `backend/job_search_agent.py` contains the orchestration loop, Codex gateway,
  Pydantic response schemas, hard filters, URL validator, scoring
  normalization, and JSON persistence.
- `backend/codex_runtime.py` resolves the host CLI, probes its availability,
  launches `codex exec`, optionally calls an authenticated host bridge, and
  validates the final structured response.
- `backend/codex_bridge.py` is the narrow Docker-to-host boundary. It accepts
  a prompt, generated JSON Schema, and search boolean—not arbitrary commands.
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
       2. host Codex CLI
          + live web search
          + read-only sandbox
          + Pydantic JSON Schema
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

1. Install Codex CLI on the host and sign in with `codex login`.
2. Confirm `codex --version` works in the terminal that will start Flask.
3. Copy `backend/.env.example` to `backend/.env`. Set `CODEX_CLI_PATH` only when
   the executable is not on `PATH`; leave `CODEX_MODEL` blank to use the host
   default.
4. Start the Flask API and frontend as described in the README.
5. Select **Run AI search** in the Inspectable AI agent panel.
6. Watch the phases update. On completion the new JSON file becomes the latest
   dashboard run.

Useful limits:

```dotenv
AGENT_MAX_SEARCH_QUERIES=4
AGENT_MAX_RESULTS=15
CODEX_TIMEOUT_SECONDS=600
```

Smaller values make learning runs faster. The CLI uses the authentication and
model access already configured for the signed-in host Codex installation.

For Docker, the backend container reaches Codex through the host bridge:

1. Copy `backend/.env.example` to `backend/.env`.
2. Set a long random `CODEX_BRIDGE_TOKEN`.
3. Set `CODEX_BRIDGE_URL=http://host.docker.internal:8765`.
4. Keep `CODEX_BRIDGE_HOST=0.0.0.0` and `CODEX_BRIDGE_PORT=8765`.
5. From `backend/`, create the host venv and install dependencies:

   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```

6. Start the bridge on the host and leave it running:

   ```bash
   .venv/bin/python codex_bridge.py
   ```

7. From the repository root, start the containers:

   ```bash
   docker compose --env-file backend/.env up --build
   ```

8. Verify the backend sees the bridge:

   ```bash
   docker exec job-dashboard-backend-1 python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/api/agent', timeout=15).read().decode())"
   ```

The response should report `"configured": true` and `"provider": "Host Codex
bridge"`. The same `CODEX_BRIDGE_TOKEN` must reach both processes, but the
container never receives the host's Codex credential files.

## Why it is an agent

This is more than one text-generation call: the system has a goal, constructs
a bounded plan, invokes the host Codex agent with an external research tool,
observes structured results, applies application-owned validations, makes a
second structured judgment, changes durable state, and exposes the execution
trace. The orchestration is explicit Python, so each capability and failure
mode is inspectable.

## Limitations

- Direct HTTP checks cannot prove that every JavaScript-heavy page is still
  accepting applications. Ambiguous or blocked pages are rejected or reported.
- The server does not inherit browser login sessions. Login walls are never
  bypassed.
- Docker requires the included host bridge because a Linux container cannot
  directly start a Windows host process. The bridge must remain running for an
  agent run to complete. If the container reports `Codex host bridge is
  unavailable (URLError)`, the bridge is usually stopped, bound only to
  `127.0.0.1`, or the container does not have
  `CODEX_BRIDGE_URL=http://host.docker.internal:8765`.
- The in-process registry assumes one Flask process. A production system with
  multiple replicas should replace it with a durable queue such as Celery/RQ
  plus Redis or a database-backed job table.
- The agent prepares recommendations only. It never applies to jobs.
