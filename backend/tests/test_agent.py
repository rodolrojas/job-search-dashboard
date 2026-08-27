from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from flask import Flask

from job_search_agent import (
    BlockedSource,
    JobSearchAgent,
    ResearchBatch,
    ResearchCandidate,
    ScoreBreakdown,
    ScoredRecommendation,
    ScoringBatch,
    UrlValidation,
)
from models import db
from repository import JobRepository


class FakeGateway:
    provider = "Fake structured runtime"
    model = "fake-agent-model"

    def research(self, **_kwargs) -> ResearchBatch:
        return ResearchBatch(
            candidates=[
                ResearchCandidate(
                    source_name="Example Careers",
                    role="Senior Full Stack Engineer",
                    company="Example Co",
                    location="LATAM — Remote",
                    posted_date=date(2026, 8, 24),
                    posted_evidence="Published August 24, 2026",
                    employment_type="Full-time",
                    salary="USD 5,000/month",
                    offer_url="https://example.com/jobs/123",
                    contact_email=None,
                    recruiter_or_careers_url="https://example.com/careers",
                    requirements_summary="TypeScript, React, Node.js, PostgreSQL, and AWS.",
                )
            ],
            blocked_sources=[BlockedSource(site="Login Board", details="Login required")],
            notes=["Fake gateway used for deterministic testing."],
        )

    def score(self, *, candidates, **_kwargs) -> ScoringBatch:
        return ScoringBatch(
            recommendations=[
                ScoredRecommendation(
                    offer_url=candidates[0].offer_url,
                    accepted=True,
                    rejection_reason=None,
                    score_breakdown=ScoreBreakdown(
                        skills_match=19,
                        seniority_scope=18,
                        technical_fit=19,
                        leadership_alignment=17,
                        compensation=9,
                        strategic_positioning=9,
                    ),
                    suggested_resume_key="react-node",
                    strategic_note="Strong end-to-end product engineering match.",
                )
            ]
        )


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_agent_researches_validates_scores_and_persists(tmp_path: Path):
    _write_json(
        tmp_path / "resume" / "resume-data.json",
        {
            "basics": {"name": "Candidate"},
            "skills": ["TypeScript", "React", "Node.js"],
            "variants": {"general": {"label": "General"}, "react-node": {"label": "React + Node"}},
        },
    )
    _write_json(tmp_path / "job_applications.json", {"applications": []})
    _write_json(tmp_path / "job_exclusions.json", {"exclusions": []})
    _write_json(
        tmp_path / "job_search_2026-08-20.json",
        {
            "report_date": "2026-08-20",
            "results": [],
            "search_summary": {
                "distinct_candidates_reviewed": 0,
                "passed_all_filters": 0,
                "rejected_or_unverifiable": 0,
            },
        },
    )
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text("Research verified senior remote LATAM roles.", encoding="utf-8")
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    repository = JobRepository(tmp_path)
    events: list[tuple[str, str]] = []

    agent = JobSearchAgent(
        repository=repository,
        gateway=FakeGateway(),
        prompt_path=prompt_path,
        url_validator=lambda url: UrlValidation(url, url, True, 200, "HTTP 200"),
        today_factory=lambda: date(2026, 8, 25),
        max_queries=1,
        max_results=7,
    )
    with app.app_context():
        db.create_all()
        repository.bootstrap_from_files()
        result = agent.run(lambda phase, message, _details=None: events.append((phase, message)))
        saved = repository.latest_run().raw_json

    assert result["result_count"] == 1
    assert [phase for phase, _message in events] == ["plan", "research", "validate", "score", "persist", "complete"]
    assert not (tmp_path / result["output_file"]).exists()
    assert saved["agent"]["model"] == "fake-agent-model"
    assert saved["agent"]["provider"] == "Fake structured runtime"
    assert saved["results"][0]["score"] == 91
    assert saved["results"][0]["suggested_resume"] == "Rodolfo_Rojas_React_Node_CV.pdf"
    assert saved["agent"]["applications_submitted"] == 0
