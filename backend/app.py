from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from cover_letters import generate_cover_letter
from models import db, model_counts
from repository import JobRepository


HERE = Path(__file__).resolve().parent
WORKSPACE_ROOT = HERE
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

    data_root = Path(app.config.get("DATA_ROOT", WORKSPACE_ROOT))
    repository = JobRepository(data_root)
    app.extensions["job_repository"] = repository
    db.init_app(app)

    with app.app_context():
        db.create_all()
        repository.sync_database()

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
            output_root=WORKSPACE_ROOT / "output" / "cover_letters",
        )
        return jsonify(result)

    @app.errorhandler(FileNotFoundError)
    def missing_data(error: FileNotFoundError):
        return jsonify({"error": str(error)}), 503

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("FLASK_PORT", "5000")), debug=True)

