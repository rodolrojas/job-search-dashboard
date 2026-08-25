from __future__ import annotations

from app import create_app
from codex_runtime import CodexRuntimeStatus


def test_health_reports_imported_models():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["models"]["jobs"] > 0


def test_dashboard_exposes_jobs_and_summary():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    response = app.test_client().get("/api/dashboard")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["jobs"]) >= 7
    assert payload["summary"]["passed_all_filters"] >= len(payload["jobs"])


def test_job_filters_are_composable():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    response = app.test_client().get("/api/jobs?search=node&min_score=80&sort=score_desc")
    assert response.status_code == 200
    payload = response.get_json()
    assert all(item["score"] >= 80 for item in payload["jobs"])
    assert payload["jobs"] == sorted(payload["jobs"], key=lambda item: item["score"], reverse=True)


def test_agent_endpoint_requires_a_runnable_codex_cli():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "CODEX_STATUS_FACTORY": lambda: CodexRuntimeStatus(False, None, "Codex CLI is unavailable."),
        }
    )
    client = app.test_client()
    info = client.get("/api/agent")
    assert info.status_code == 200
    assert info.get_json()["configured"] is False
    assert info.get_json()["provider"] == "Host Codex CLI"
    start = client.post("/api/agent/runs")
    assert start.status_code == 503
