# Role Radar

Role Radar is a responsive job-search command center backed by PostgreSQL. On
the first database startup, it imports the existing job-run,
professional-profile, application-history, exclusion-history, and
resume-variant files from the parent workspace.

It includes:

- a ranked grid of every role in the latest run;
- composable filters for text, score, company, location, and status;
- sorting by score, date, company, or role;
- run totals, top-three recommendations, prior-run comparison, search issues, and login-wall notes;
- persistent **Mark as Applied** and **Mark as Rejected** actions;
- Codex-powered cover-letter generation using the suggested resume variant,
  with a truthful local fallback;
- PostgreSQL + SQLAlchemy models for search runs, jobs, profile and resume
  variants, applications, exclusions, cover letters, and agent audit events;
- an inspectable AI job-search agent that plans searches, invokes the signed-in
  Codex CLI on the host machine for web research and structured scoring,
  validates direct listing URLs, scores profile fit, and persists fresh runs.

## Project layout

```text
job-search-dashboard/
├── app/                 Next.js routes and global styling
├── components/          Dashboard and shadcn-style UI components
├── data/                Safe preview data for frontend-only hosting
├── lib/                 API client, types, and formatting helpers
├── store/               Zustand application state
├── backend/             Flask API, PostgreSQL models/schema, repository, tests
├── docs/                Architecture and project brief
└── public/              Social preview asset
```

## Prerequisites

- Node.js 22.13 or newer
- pnpm
- Python 3.11 or newer
- Docker Desktop, or a PostgreSQL 17 server
- [Codex CLI](https://developers.openai.com/codex/cli/reference) installed and signed in on the host machine

## 1. Start PostgreSQL and the application with Docker

Copy the backend environment file and replace the development database password
and Codex bridge token before using the stack outside a local machine:

```powershell
Copy-Item backend/.env.example backend/.env
docker compose --env-file backend/.env up --build
```

The stack starts PostgreSQL on `localhost:5432`, Flask on
`http://localhost:5000`, and the frontend on `http://localhost:3000`.
PostgreSQL data survives container recreation in the `postgres-data` named
volume. The database container applies `backend/schema.sql` to a new volume,
and SQLAlchemy verifies any missing tables at API startup.

The first API startup imports the existing workspace JSON files only when their
destination tables are empty. From that point onward PostgreSQL is the source
of truth for job runs, profile data, status changes, generated cover letters,
and agent execution history.

## 2. Run the Flask backend outside Docker

Start only PostgreSQL from the repository root:

```powershell
docker compose --env-file backend/.env up -d postgres
```

Then, from `job-search-dashboard/backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

The API starts at `http://localhost:5000` and connects to the PostgreSQL
settings in `backend/.env`. `DATABASE_URL` may be set explicitly; otherwise the
backend builds the connection from `POSTGRES_*`, `DB_HOST`, and `DB_PORT`.

The job-search and cover-letter agents do not require an API key. They launch
the host's signed-in `codex exec` runtime in read-only, non-interactive mode. Confirm that
`codex --version` works in the same terminal that starts Flask, then select
**Run AI search** in the dashboard. If the executable is not on `PATH`, set
`CODEX_CLI_PATH` in `backend/.env`. Leave `CODEX_MODEL` blank to inherit the
host's configured default model, or set it to an allowed model override.

The run limit can be adjusted with `CODEX_TIMEOUT_SECONDS`; workload size is
bounded by `AGENT_MAX_SEARCH_QUERIES` and `AGENT_MAX_RESULTS`. See
[docs/agent-walkthrough.md](docs/agent-walkthrough.md) for a code-level tour of
the loop and its trust boundaries.

This direct mode expects Flask and Codex CLI on the same operating-system host.
For a Dockerized backend, use the authenticated host bridge below.

## 3. Start the Next.js frontend separately

From `job-search-dashboard` in a second terminal:

```powershell
pnpm install
Copy-Item .env.example .env
pnpm dev
```

Open `http://localhost:3000`.

If the Flask service is unavailable, the dashboard enters preview mode using a bundled copy of the latest shortlist. Cover-letter previews still work, but status buttons are disabled because they must write through the backend.

## Docker backend with host Codex

The Linux backend container cannot execute a Windows host binary directly.
`backend/codex_bridge.py` solves that boundary without copying Codex credentials
into Docker: it accepts one authenticated, schema-constrained operation and
always launches `codex exec` with a read-only sandbox and no approvals.

1. Copy `backend/.env.example` to `backend/.env` and replace
   `CODEX_BRIDGE_TOKEN` with a random value of at least 32 characters. For
   example, generate one with
   `[Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))`.
   Keep `CODEX_BRIDGE_URL` blank in this host-side file.
2. Start the bridge on the host:

   ```powershell
   Set-Location backend
   python codex_bridge.py
   ```

3. In another terminal, start Docker with the same environment file. This also
   starts the persistent PostgreSQL container:

   ```powershell
   docker compose --env-file backend/.env up --build
   ```

Compose points the backend at `http://host.docker.internal:8765`. The bearer
token is required on both sides; do not commit it. If Windows Firewall asks,
allow the bridge only on trusted/private networks.

## Codex cover-letter generation

Cover letters use the same direct Codex CLI or authenticated Docker bridge as
the job-search agent. The generator sends only the selected job and relevant
candidate profile fields, disables web search, and validates the response
against a Pydantic schema. If Codex cannot run, the backend saves a
deterministic draft so the user remains unblocked. Generated letters are saved
under the parent workspace at `output/cover_letters/`; review every letter
before using it.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Service and imported-model counts |
| `GET` | `/api/dashboard` | Latest run, jobs, summary, recommendations, and comparison |
| `GET` | `/api/jobs` | Backend filtering and sorting |
| `GET` | `/api/agent` | Agent configuration, workflow, guardrails, and latest run |
| `POST` | `/api/agent/runs` | Start a background job-search agent run |
| `GET` | `/api/agent/runs/:id` | Inspect progress, events, result, or failure |
| `POST` | `/api/jobs/:id/status` | Mark a role as applied or rejected |
| `POST` | `/api/jobs/:id/cover-letter` | Generate and save a tailored cover letter |

Filtering parameters for `/api/jobs` can be combined: `search`, `min_score`, `company`, `location`, `status`, and `sort`.

## Verification

Frontend:

```powershell
pnpm build
```

Backend:

```powershell
python -m pytest
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full system diagram
and [docs/data-model.md](docs/data-model.md) for the PostgreSQL entity model.

## Data safety and application boundary

- Existing job-run, profile, and history JSON files are read only during the
  initial database bootstrap and are never rewritten.
- Applications, exclusions, generated letters, agent events, and new search
  runs are committed transactionally to PostgreSQL.
- Resume PDF files remain read-only workspace assets; their variant metadata is
  stored in PostgreSQL.
- The system does **not** submit job applications. It prepares recommendations, resume choices, and cover letters for the user to review and submit.
- Research pages are untrusted input. The agent never uses credentials, bypasses
  access controls, or accepts a listing without application-owned URL/date checks.
