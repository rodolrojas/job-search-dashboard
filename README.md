# Role Radar

Role Radar is a responsive job-search command center built around the existing job-run, professional-profile, application-history, exclusion-history, and resume-variant files in the parent workspace.

It includes:

- a ranked grid of every role in the latest run;
- composable filters for text, score, company, location, and status;
- sorting by score, date, company, or role;
- run totals, top-three recommendations, prior-run comparison, search issues, and login-wall notes;
- persistent **Mark as Applied** and **Mark as Rejected** actions;
- tailored cover-letter generation using the suggested resume variant;
- optional OpenAI Responses API generation with a truthful local fallback;
- Flask + SQLAlchemy models for jobs, profile, application history, and exclusions.
- an inspectable AI job-search agent that plans searches, uses OpenAI web search,
  validates direct listing URLs, scores profile fit, and persists fresh runs.

## Project layout

```text
job-search-dashboard/
├── app/                 Next.js routes and global styling
├── components/          Dashboard and shadcn-style UI components
├── data/                Safe preview data for frontend-only hosting
├── lib/                 API client, types, and formatting helpers
├── store/               Zustand application state
├── backend/             Flask API, SQLAlchemy models, JSON repository, tests
├── docs/                Architecture and project brief
└── public/              Social preview asset
```

## Prerequisites

- Node.js 22.13 or newer
- pnpm
- Python 3.11 or newer

## 1. Start the Flask backend

From `job-search-dashboard/backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

The API starts at `http://localhost:5000`. On first launch it finds the newest `job_search_YYYY-MM-DD*.json` file, imports the profile and history JSON files, and builds `backend/role_radar.db` as a local SQLAlchemy index.

To run the job-search agent, set `OPENAI_API_KEY` in `backend/.env`. The agent
uses `OPENAI_MODEL` (`gpt-5.4` by default), and its cost/latency can be bounded
with `AGENT_MAX_SEARCH_QUERIES` and `AGENT_MAX_RESULTS`. Then select **Run AI
search** in the dashboard. See [docs/agent-walkthrough.md](docs/agent-walkthrough.md)
for a code-level tour of the loop and its trust boundaries.

## 2. Start the Next.js frontend

From `job-search-dashboard` in a second terminal:

```powershell
pnpm install
Copy-Item .env.example .env
pnpm dev
```

Open `http://localhost:3000`.

If the Flask service is unavailable, the dashboard enters preview mode using a bundled copy of the latest shortlist. Cover-letter previews still work, but status buttons are disabled because they must write through the backend.

## OpenAI cover-letter generation

The backend works without an API key and creates a deterministic draft from verified profile data. To use the OpenAI Responses API, set these values in `backend/.env`:

```dotenv
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.4
```

The official SDK reads `OPENAI_API_KEY` from the environment. Generated letters are saved under the parent workspace at `output/cover_letters/`. Review every letter before using it. See the [official Responses API reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create).

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

See [docs/architecture.md](docs/architecture.md) for the full diagram and responsibility boundaries.

## Data safety and application boundary

- Existing job-run and resume files are read, not rewritten.
- Applied and rejected actions append normalized records to the existing history JSON files.
- JSON writes are atomic and synchronized inside the local Flask process.
- The system does **not** submit job applications. It prepares recommendations, resume choices, and cover letters for the user to review and submit.
- Research pages are untrusted input. The agent never uses credentials, bypasses
  access controls, or accepts a listing without application-owned URL/date checks.
