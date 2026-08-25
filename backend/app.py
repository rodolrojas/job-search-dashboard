from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from agent_service import AgentRunRegistry
from codex_runtime import CodexRuntimeStatus, codex_provider_name, codex_runtime_status
from cover_letters import generate_cover_letter
from job_search_agent import CodexCliJobGateway, JobSearchAgent
from models import db, model_counts
from repository import JobRepository


HERE = Path(__file__).resolve().parent
WORKSPACE_ROOT = HERE.parents[1]
load_dotenv(HERE / ".env")


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{(HERE / 'role_radar.db').as_posix()}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    data_root = Path(app.config.get("DATA_ROOT") or os.getenv("DATA_ROOT") or WORKSPACE_ROOT)
    repository = JobRepository(data_root)
    app.extensions["job_repository"] = repository
    db.init_app(app)

    with app.app_context():
        db.create_all()
        repository.sync_database()

    prompt_path = Path(
        app.config.get(
            "AGENT_PROMPT_PATH",
            data_root / "job listing agent.md" if (data_root / "job listing agent.md").exists() else HERE / "prompts" / "job_search_agent.md",
        )
    )

    def create_agent() -> JobSearchAgent:
        gateway_factory = app.config.get("AGENT_GATEWAY_FACTORY")
        gateway = (
            gateway_factory()
            if gateway_factory
            else CodexCliJobGateway(
                workspace=Path(app.config.get("CODEX_WORKSPACE", HERE.parent)),
            )
        )
        return JobSearchAgent(
            repository=repository,
            gateway=gateway,
            prompt_path=prompt_path,
        )

    def runtime_status() -> CodexRuntimeStatus:
        status_factory = app.config.get("CODEX_STATUS_FACTORY")
        return status_factory() if status_factory else codex_runtime_status()

    def sync_after_agent(_result: dict) -> None:
        with app.app_context():
            repository.sync_database()

    agent_runs = AgentRunRegistry(create_agent, on_complete=sync_after_agent)
    app.extensions["agent_runs"] = agent_runs

    allowed_origins = {
        item.strip()
        for item in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",")
        if item.strip()
    }

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return response

    @app.route("/api/<path:_path>", methods=["OPTIONS"])
    def options(_path: str):
        return ("", 204)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "models": model_counts(), "latest_run": repository.latest_run_path().name})

    @app.get("/api/dashboard")
    def dashboard():
        return jsonify(repository.dashboard())

    @app.get("/api/jobs")
    def jobs():
        return jsonify(repository.filtered_jobs(request.args.to_dict()))

    @app.get("/api/agent")
    def agent_info():
        status = runtime_status()
        return jsonify(
            {
                "configured": status.available,
                "provider": codex_provider_name(),
                "model": os.getenv("CODEX_MODEL") or ("host bridge default" if os.getenv("CODEX_BRIDGE_URL") else "host default"),
                "runtime": status.message,
                "runtime_version": status.version,
                "prompt_file": prompt_path.name,
                "workflow": ["plan", "research", "validate", "score", "persist"],
                "latest_run": agent_runs.latest(),
                "guardrails": [
                    "Never submits applications",
                    "Never bypasses login walls or bot protection",
                    "Requires direct URL and recent-date validation",
                    "Excludes applied and rejected roles",
                ],
            }
        )

    @app.post("/api/agent/runs")
    def start_agent_run():
        status = runtime_status()
        if not status.available:
            return jsonify({"error": status.message}), 503
        try:
            run = agent_runs.start()
        except RuntimeError as error:
            return jsonify({"error": str(error), "run": agent_runs.latest()}), 409
        return jsonify(run), 202

    @app.get("/api/agent/runs/latest")
    def latest_agent_run():
        run = agent_runs.latest()
        return (jsonify(run), 200) if run else (jsonify({"error": "No agent run has started."}), 404)

    @app.get("/api/agent/runs/<run_id>")
    def agent_run(run_id: str):
        run = agent_runs.get(run_id)
        return (jsonify(run), 200) if run else (jsonify({"error": "Agent run not found."}), 404)

    @app.post("/api/jobs/<job_id>/status")
    def update_status(job_id: str):
        job = repository.find_job(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        status = (request.get_json(silent=True) or {}).get("status")
        if status == "applied":
            record = repository.mark_applied(job)
        elif status == "rejected":
            record = repository.mark_rejected(job)
        else:
            return jsonify({"error": "Status must be 'applied' or 'rejected'."}), 400
        repository.sync_database()
        return jsonify({"status": status, "record": record})

    @app.post("/api/jobs/<job_id>/cover-letter")
    def cover_letter(job_id: str):
        job = repository.find_job(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        payload = request.get_json(silent=True) or {}
        requested_variant = str(payload.get("resume_variant") or job.get("suggested_resume") or "general")
        variant_key = requested_variant.lower().replace("rodolfo_rojas_", "").replace("_cv.pdf", "").replace("_", "-")
        variant_aliases = {"react-node": "react-node", "react-node-cv": "react-node", "general": "general", "frontend": "frontend", "backend": "backend", "php": "php", "go": "go"}
        variant_key = variant_aliases.get(variant_key, "general")
        result = generate_cover_letter(
            job=job,
            profile=repository.load_profile(),
            variant_key=variant_key,
            output_root=data_root / "output" / "cover_letters",
            workspace=Path(app.config.get("CODEX_WORKSPACE", HERE.parent)),
        )
        return jsonify(result)

    @app.errorhandler(FileNotFoundError)
    def missing_data(error: FileNotFoundError):
        return jsonify({"error": str(error)}), 503

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", "5000")), debug=True)
