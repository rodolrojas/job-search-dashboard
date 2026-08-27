from __future__ import annotations

import json
from pathlib import Path

from flask import Flask

from models import db, model_counts
from repository import JobRepository


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _database_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    return app


def test_schema_contains_every_persistent_domain_model():
    assert {
        "candidate_profiles",
        "resume_variants",
        "job_search_runs",
        "jobs",
        "job_run_listings",
        "job_applications",
        "job_exclusions",
        "cover_letters",
        "agent_runs",
        "agent_run_events",
    }.issubset(db.metadata.tables)


def test_repository_bootstraps_json_then_persists_workflow_data(tmp_path: Path):
    _write_json(
        tmp_path / "resume" / "resume-data.json",
        {
            "basics": {"name": "Candidate", "email": "candidate@example.com"},
            "variants": {"general": {"label": "General", "headline": "Senior Engineer"}},
        },
    )
    _write_json(tmp_path / "job_applications.json", {"applications": []})
    _write_json(tmp_path / "job_exclusions.json", {"exclusions": []})
    _write_json(
        tmp_path / "job_search_2026-08-26.json",
        {
            "report_date": "2026-08-26",
            "search_summary": {
                "distinct_candidates_reviewed": 1,
                "passed_all_filters": 1,
                "rejected_or_unverifiable": 0,
            },
            "results": [
                {
                    "rank": 1,
                    "job_id": "example-senior-engineer",
                    "role": "Senior Engineer",
                    "company": "Example Co",
                    "location": "LATAM - Remote",
                    "score": 90,
                    "suggested_resume": "Rodolfo_Rojas_General_CV.pdf",
                }
            ],
        },
    )

    app = _database_app()
    repository = JobRepository(tmp_path)
    with app.app_context():
        db.create_all()
        repository.bootstrap_from_files()
        job = repository.find_job("example-senior-engineer")
        assert job is not None

        repository.mark_applied(job)
        repository.save_cover_letter(
            job,
            "general",
            {
                "content": "Dear Example Co Hiring Team,\n",
                "mode": "codex",
                "warning": None,
                "filename": "example-cover-letter.txt",
                "saved_to": None,
            },
        )
        repository.save_agent_run(
            {
                "id": "a" * 32,
                "status": "completed",
                "phase": "complete",
                "message": "Finished.",
                "created_at": "2026-08-27T10:00:00+00:00",
                "updated_at": "2026-08-27T10:01:00+00:00",
                "events": [
                    {
                        "phase": "persist",
                        "message": "Saved to PostgreSQL.",
                        "details": {"count": 1},
                        "created_at": "2026-08-27T10:00:30+00:00",
                    }
                ],
                "result": {"result_count": 1},
                "error": None,
            }
        )

        counts = model_counts()
        assert counts["runs"] == 1
        assert counts["applications"] == 1
        assert counts["cover_letters"] == 1
        assert counts["agent_runs"] == 1
        assert repository.dashboard()["jobs"][0]["status"] == "applied"
        assert repository.load_agent_runs()[-1]["events"][0]["details"] == {"count": 1}
