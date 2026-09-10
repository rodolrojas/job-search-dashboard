from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import select

from models import (
    AgentRun,
    AgentRunEvent,
    CandidateProfile,
    CoverLetter,
    Job,
    JobApplication,
    JobExclusion,
    JobRunListing,
    JobSearchRun,
    ResumeVariant,
    db,
)


JSONDict = dict[str, Any]
_DATE_RE = re.compile(r"job_search_(\d{4}-\d{2}-\d{2})(?:-rerun(?:-(\d+))?)?\.json$")


def _read_json(path: Path, default: JSONDict | None = None) -> JSONDict:
    if not path.exists():
        return default or {}
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _parse_datetime(value: Any, default: datetime | None = None) -> datetime:
    if isinstance(value, datetime):
        return value
    if value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            pass
    return default or datetime.now(UTC)


def _run_key(path: Path) -> tuple[date, int]:
    match = _DATE_RE.match(path.name)
    if not match:
        return date.min, -1
    rerun_rank = 0
    if "-rerun" in path.stem:
        rerun_rank = int(match.group(2) or 1)
    return date.fromisoformat(match.group(1)), rerun_rank


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _resume_filename(key: str) -> str:
    names = {
        "general": "Rodolfo_Rojas_General_CV.pdf",
        "react-node": "Rodolfo_Rojas_React_Node_CV.pdf",
        "frontend": "Rodolfo_Rojas_Frontend_CV.pdf",
        "backend": "Rodolfo_Rojas_Backend_CV.pdf",
        "php": "Rodolfo_Rojas_PHP_CV.pdf",
        "go": "Rodolfo_Rojas_Go_CV.pdf",
    }
    return names.get(key, f"Rodolfo_Rojas_{key.title()}_CV.pdf")


def _default_applications() -> JSONDict:
    today = date.today().isoformat()
    return {
        "schema_version": "1.0",
        "created_on": today,
        "last_updated": today,
        "status_values": ["application_sent"],
        "applications": [],
    }


def _default_exclusions() -> JSONDict:
    today = date.today().isoformat()
    return {
        "schema_version": "1.0",
        "created_on": today,
        "last_updated": today,
        "status_values": ["user_removed"],
        "exclusions": [],
    }


def _default_profile() -> JSONDict:
    return {
        "basics": {"name": "Rodolfo Rojas"},
        "summary": [
            "I bring more than ten years of full-stack software engineering experience.",
        ],
        "variants": {
            "general": {
                "label": "General",
                "headline": "Senior full-stack software engineer",
            },
            "react-node": {
                "label": "React + Node",
                "headline": "Senior React, Node.js, and TypeScript engineer",
            },
            "frontend": {
                "label": "Frontend",
                "headline": "Senior frontend engineer",
            },
            "backend": {
                "label": "Backend",
                "headline": "Senior backend engineer",
            },
            "php": {
                "label": "PHP",
                "headline": "Senior PHP engineer",
            },
            "go": {
                "label": "Go",
                "headline": "Senior Go engineer",
            },
        },
    }


class JobRepository:
    """PostgreSQL-backed source of truth with a one-time legacy JSON importer."""

    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.applications_path = data_root / "job_applications.json"
        self.exclusions_path = data_root / "job_exclusions.json"
        self.profile_path = data_root / "resume" / "resume-data.json"

    def run_files(self) -> list[Path]:
        candidates = [
            path
            for path in self.data_root.glob("job_search_*.json")
            if path.name != "job_search_prior_run.json" and _DATE_RE.match(path.name)
        ]
        return sorted(candidates, key=_run_key, reverse=True)

    def bootstrap_from_files(self) -> None:
        """Import legacy workspace files only when their destination tables are empty."""

        if db.session.query(CandidateProfile).count() == 0:
            self._save_profile(_read_json(self.profile_path, _default_profile()))

        if db.session.query(JobSearchRun).count() == 0:
            for path in reversed(self.run_files()):
                self.save_search_run(_read_json(path), path.name, commit=False)

        if db.session.query(JobApplication).count() == 0:
            for item in _read_json(self.applications_path, _default_applications()).get("applications", []):
                self._import_application(item)

        if db.session.query(JobExclusion).count() == 0:
            for item in _read_json(self.exclusions_path, _default_exclusions()).get("exclusions", []):
                self._import_exclusion(item)

        db.session.commit()

    def sync_database(self) -> None:
        """Backward-compatible alias for the idempotent legacy bootstrap."""

        self.bootstrap_from_files()

    def latest_run(self) -> JobSearchRun:
        run = db.session.execute(
            select(JobSearchRun).order_by(
                JobSearchRun.report_date.desc(),
                JobSearchRun.run_number.desc(),
                JobSearchRun.created_at.desc(),
            ).limit(1)
        ).scalar_one_or_none()
        if not run:
            raise FileNotFoundError("No job-search runs are stored in PostgreSQL.")
        return run

    def latest_run_path(self) -> Path:
        return self.data_root / self.latest_run().source_file

    def latest_run_name(self) -> str:
        return self.latest_run().source_file

    def next_run_name(self, today: date) -> str:
        base = f"job_search_{today.isoformat()}.json"
        if db.session.get(JobSearchRun, base) is None:
            return base
        rerun = f"job_search_{today.isoformat()}-rerun.json"
        if db.session.get(JobSearchRun, rerun) is None:
            return rerun
        index = 2
        while db.session.get(JobSearchRun, f"job_search_{today.isoformat()}-rerun-{index}.json") is not None:
            index += 1
        return f"job_search_{today.isoformat()}-rerun-{index}.json"

    def load_profile(self) -> JSONDict:
        profile = db.session.get(CandidateProfile, 1)
        if not profile:
            raise FileNotFoundError("No candidate profile is stored in PostgreSQL.")
        return dict(profile.raw_json or {})

    def load_applications(self) -> JSONDict:
        rows = db.session.execute(
            select(JobApplication).order_by(JobApplication.applied_on.asc(), JobApplication.created_at.asc())
        ).scalars()
        payload = _default_applications()
        payload["applications"] = [dict(row.raw_json or {}) for row in rows]
        if payload["applications"]:
            payload["last_updated"] = max(
                str(item.get("status_updated_on") or item.get("applied_on") or payload["last_updated"])
                for item in payload["applications"]
            )
        return payload

    def load_exclusions(self) -> JSONDict:
        rows = db.session.execute(
            select(JobExclusion).order_by(JobExclusion.excluded_on.asc(), JobExclusion.created_at.asc())
        ).scalars()
        payload = _default_exclusions()
        payload["exclusions"] = [dict(row.raw_json or {}) for row in rows]
        if payload["exclusions"]:
            payload["last_updated"] = max(
                str(item.get("excluded_on") or payload["last_updated"])
                for item in payload["exclusions"]
            )
        return payload

    def _status_maps(self) -> tuple[dict[str, JSONDict], dict[str, JSONDict]]:
        applications = {
            row.job_id: dict(row.raw_json or {})
            for row in db.session.execute(select(JobApplication)).scalars()
        }
        exclusions = {
            row.job_id: dict(row.raw_json or {})
            for row in db.session.execute(select(JobExclusion)).scalars()
        }
        return applications, exclusions

    def normalize_job(
        self,
        raw: JSONDict,
        applications: dict[str, JSONDict],
        exclusions: dict[str, JSONDict],
    ) -> JSONDict:
        job_id = str(raw.get("job_id") or raw.get("id") or _slug(f"{raw.get('company', '')}-{raw.get('role', '')}"))
        status = "applied" if job_id in applications else "rejected" if job_id in exclusions else "available"
        score = int(raw.get("score") or 0)

        return {
            "id": job_id,
            "rank": raw.get("rank"),
            "role": raw.get("role") or raw.get("title") or "Untitled role",
            "company": raw.get("company") or "Unknown company",
            "location": raw.get("location") or "Remote",
            "posted": raw.get("posted") or raw.get("posted_date"),
            "posted_evidence": raw.get("posted_evidence"),
            "score": score,
            "score_breakdown": raw.get("score_breakdown") or {},
            "salary": raw.get("salary") or "Undisclosed",
            "employment_type": raw.get("employment_type") or "Full-time",
            "offer_url": raw.get("offer_url") or raw.get("url") or raw.get("link"),
            "contact_email": raw.get("contact_email") or raw.get("email"),
            "recruiter_or_careers_url": raw.get("recruiter_or_careers_url") or raw.get("careers_url"),
            "suggested_resume": raw.get("suggested_resume") or raw.get("suggested_resume_variant") or "Rodolfo_Rojas_General_CV.pdf",
            "strategic_note": raw.get("strategic_note") if score >= 70 else None,
            "live_check": raw.get("live_check"),
            "is_new": bool(raw.get("new") or raw.get("is_new")),
            "status": status,
        }

    def dashboard(self) -> JSONDict:
        run = self.latest_run()
        applications, exclusions = self._status_maps()
        jobs = [
            self.normalize_job(dict(listing.raw_json or {}), applications, exclusions)
            for listing in run.listings
        ]
        profile = self.load_profile()
        variants = [
            {
                "key": row.key,
                "label": row.label,
                "headline": row.headline,
                "pdf": row.pdf_filename,
            }
            for row in db.session.execute(select(ResumeVariant).order_by(ResumeVariant.key)).scalars()
        ]
        if not variants:
            variants = [
                {
                    "key": key,
                    "label": value.get("label", key),
                    "headline": value.get("headline", ""),
                    "pdf": _resume_filename(key),
                }
                for key, value in (profile.get("variants") or {}).items()
            ]

        return {
            "run": {
                "date": run.report_date.isoformat(),
                "timezone": run.timezone,
                "source_file": run.source_file,
            },
            "summary": dict(run.summary or {}),
            "jobs": jobs,
            "top_three": list(run.top_three or []),
            "comparison": dict(run.comparison or {"added": [], "retained": [], "dropped": []}),
            "issues": list(run.issues or []),
            "blocked_sources": list(run.blocked_sources or []),
            "resume_variants": variants,
        }

    def find_job(self, job_id: str) -> JSONDict | None:
        return next((job for job in self.dashboard()["jobs"] if job["id"] == job_id), None)

    def filtered_jobs(self, query: dict[str, str]) -> JSONDict:
        payload = self.dashboard()
        jobs: Iterable[JSONDict] = payload["jobs"]
        search = query.get("search", "").strip().lower()
        company = query.get("company", "").strip().lower()
        location = query.get("location", "").strip().lower()
        status = query.get("status", "").strip().lower()
        min_score = int(query.get("min_score", "0") or 0)

        if search:
            jobs = [item for item in jobs if search in " ".join([item["role"], item["company"], item["location"], item.get("strategic_note") or ""]).lower()]
        if company:
            jobs = [item for item in jobs if item["company"].lower() == company]
        if location:
            jobs = [item for item in jobs if location in item["location"].lower()]
        if status:
            jobs = [item for item in jobs if item["status"] == status]
        jobs = [item for item in jobs if item["score"] >= min_score]

        sort = query.get("sort", "score_desc")
        reverse = sort.endswith("_desc")
        key_name = "posted" if sort.startswith("date") else "company" if sort.startswith("company") else "role" if sort.startswith("role") else "score"
        jobs = sorted(jobs, key=lambda item: item.get(key_name) or "", reverse=reverse)
        return {"jobs": jobs, "count": len(jobs)}

    def mark_applied(self, job: JSONDict) -> JSONDict:
        existing = db.session.execute(
            select(JobApplication).where(JobApplication.job_id == job["id"])
        ).scalar_one_or_none()
        if existing:
            return dict(existing.raw_json or {})

        today = date.today().isoformat()
        record = {
            "application_id": f"app-{job['id']}-{today.replace('-', '')}",
            "job_id": job["id"],
            "company": job["company"],
            "role": job["role"],
            "location": job["location"],
            "job_url": job.get("offer_url"),
            "source_file": self.latest_run_name(),
            "source_original_rank": job.get("rank"),
            "applied_on": today,
            "status": "application_sent",
            "status_updated_on": today,
            "next_action": "Await response",
            "next_action_date": None,
            "contacts": [],
            "notes": ["Marked as applied from Role Radar."],
        }
        self._upsert_job(job, self.latest_run().report_date)
        self._import_application(record)
        db.session.commit()
        return record

    def mark_rejected(self, job: JSONDict) -> JSONDict:
        existing = db.session.execute(
            select(JobExclusion).where(JobExclusion.job_id == job["id"])
        ).scalar_one_or_none()
        if existing:
            return dict(existing.raw_json or {})

        today = date.today().isoformat()
        record = {
            "exclusion_id": f"exclude-{job['id']}-{today.replace('-', '')}",
            "job_id": job["id"],
            "company": job["company"],
            "role": job["role"],
            "job_url": job.get("offer_url"),
            "source_file": self.latest_run_name(),
            "source_original_rank": job.get("rank"),
            "excluded_on": today,
            "status": "user_removed",
            "reason": "Marked as rejected from Role Radar.",
            "keep_out_of_future_results": True,
        }
        self._upsert_job(job, self.latest_run().report_date)
        self._import_exclusion(record)
        db.session.commit()
        return record

    def save_search_run(self, payload: JSONDict, source_file: str, *, commit: bool = True) -> JobSearchRun:
        fallback_date, run_number = _run_key(Path(source_file))
        report_date = _parse_date(payload.get("report_date") or payload.get("run_date")) or fallback_date
        if report_date == date.min:
            raise ValueError(f"Could not determine the report date for {source_file}.")

        comparison = payload.get("comparison_with_previous_rerun") or payload.get("comparison_with_previous") or {}
        summary = payload.get("search_summary") or {}
        results = payload.get("results", payload.get("roles", []))
        if not summary:
            summary = {
                "distinct_candidates_reviewed": len(results),
                "passed_all_filters": len(results),
                "rejected_or_unverifiable": 0,
            }
        audit_notes = payload.get("audit_notes", [])
        issues = [audit_notes] if isinstance(audit_notes, str) else list(audit_notes or [])
        board_checks = payload.get("corrected_board_rerun", []) or payload.get("board_checks", []) or payload.get("source_audit", [])
        blocked_sources = [
            {
                "site": item.get("site", "Unknown site"),
                "details": item.get("outcome") or item.get("reason") or "Access was blocked.",
            }
            for item in board_checks
            if str(item.get("status", "")).lower() in {"blocked", "login_required", "login wall", "access_issue"}
        ]

        run = db.session.get(JobSearchRun, source_file)
        if not run:
            run = JobSearchRun(id=source_file, source_file=source_file, report_date=report_date)
            db.session.add(run)
        run.report_date = report_date
        run.run_number = run_number
        run.timezone = payload.get("timezone")
        run.summary = summary
        run.top_three = payload.get("top_three") or []
        run.comparison = {
            "added": comparison.get("added", []),
            "retained": comparison.get("retained", []),
            "dropped": comparison.get("dropped", []),
        }
        run.issues = issues
        run.blocked_sources = blocked_sources
        run.agent_metadata = payload.get("agent") or {}
        run.raw_json = payload

        existing = {listing.job_id: listing for listing in run.listings}
        seen: set[str] = set()
        for raw in results:
            job_id = str(raw.get("job_id") or raw.get("id") or _slug(f"{raw.get('company', '')}-{raw.get('role', '')}"))
            seen.add(job_id)
            self._upsert_job(raw | {"id": job_id}, report_date)
            listing = existing.get(job_id)
            if not listing:
                listing = JobRunListing(run=run, job_id=job_id)
                db.session.add(listing)
                existing[job_id] = listing
            listing.rank = raw.get("rank")
            listing.posted_on = _parse_date(raw.get("posted") or raw.get("posted_date"))
            listing.posted_evidence = raw.get("posted_evidence")
            listing.score = int(raw.get("score") or 0)
            listing.score_breakdown = raw.get("score_breakdown") or {}
            listing.suggested_resume = raw.get("suggested_resume") or raw.get("suggested_resume_variant") or "Rodolfo_Rojas_General_CV.pdf"
            listing.strategic_note = raw.get("strategic_note")
            listing.live_check = raw.get("live_check")
            listing.source_name = raw.get("source_name")
            listing.requirements_summary = raw.get("requirements_summary")
            listing.is_new = bool(raw.get("new") or raw.get("is_new"))
            listing.raw_json = raw | {"job_id": job_id}

        for job_id, listing in existing.items():
            if job_id not in seen:
                db.session.delete(listing)
        if commit:
            db.session.commit()
        return run

    def save_cover_letter(self, job: JSONDict, variant_key: str, result: JSONDict) -> str:
        self._upsert_job(job, self.latest_run().report_date)
        record_id = uuid.uuid4().hex
        db.session.add(
            CoverLetter(
                id=record_id,
                job_id=job["id"],
                resume_variant=variant_key,
                content=str(result["content"]),
                mode=str(result["mode"]),
                warning=result.get("warning"),
                filename=str(result["filename"]),
                saved_to=result.get("saved_to"),
            )
        )
        db.session.commit()
        return record_id

    def save_agent_run(self, snapshot: JSONDict) -> None:
        run = db.session.get(AgentRun, snapshot["id"])
        if not run:
            run = AgentRun(
                id=snapshot["id"],
                status=snapshot["status"],
                phase=snapshot["phase"],
                message=snapshot["message"],
                created_at=_parse_datetime(snapshot.get("created_at")),
                updated_at=_parse_datetime(snapshot.get("updated_at")),
            )
            db.session.add(run)
        run.status = snapshot["status"]
        run.phase = snapshot["phase"]
        run.message = snapshot["message"]
        run.result = snapshot.get("result")
        run.error = snapshot.get("error")
        run.updated_at = _parse_datetime(snapshot.get("updated_at"))

        existing = {event.sequence: event for event in run.events}
        for sequence, payload in enumerate(snapshot.get("events") or [], start=1):
            event = existing.get(sequence)
            if not event:
                event = AgentRunEvent(run=run, sequence=sequence)
                db.session.add(event)
            event.phase = str(payload.get("phase") or "unknown")
            event.message = str(payload.get("message") or "")
            event.details = payload.get("details")
            event.created_at = _parse_datetime(payload.get("created_at"))
        db.session.commit()

    def load_agent_runs(self, limit: int = 50) -> list[JSONDict]:
        rows = list(
            db.session.execute(
                select(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit)
            ).scalars()
        )
        recovered = False
        for row in rows:
            if row.status in {"queued", "running"}:
                row.status = "failed"
                row.phase = "failed"
                row.message = "Agent run was interrupted by a backend restart."
                row.error = "Backend restarted before the run completed."
                row.updated_at = datetime.now(UTC)
                recovered = True
        if recovered:
            db.session.commit()
        return [self._agent_run_payload(row) for row in reversed(rows)]

    def _agent_run_payload(self, row: AgentRun) -> JSONDict:
        return {
            "id": row.id,
            "status": row.status,
            "phase": row.phase,
            "message": row.message,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
            "events": [
                {
                    "phase": event.phase,
                    "message": event.message,
                    "details": event.details,
                    "created_at": event.created_at.isoformat(),
                }
                for event in row.events
            ],
            "result": row.result,
            "error": row.error,
        }

    def _save_profile(self, profile: JSONDict) -> None:
        basics = profile.get("basics") or {}
        row = CandidateProfile(
            id=1,
            display_name=basics.get("name") or "Candidate",
            email=basics.get("email"),
            location=basics.get("location"),
            raw_json=profile,
        )
        db.session.add(row)
        for key, value in (profile.get("variants") or {}).items():
            db.session.add(
                ResumeVariant(
                    key=key,
                    profile=row,
                    label=value.get("label", key),
                    headline=value.get("headline", ""),
                    pdf_filename=_resume_filename(key),
                    raw_json=value,
                )
            )

    def _upsert_job(self, raw: JSONDict, seen_on: date | None) -> Job:
        job_id = str(raw.get("job_id") or raw.get("id") or _slug(f"{raw.get('company', '')}-{raw.get('role', '')}"))
        row = db.session.get(Job, job_id)
        if not row:
            row = Job(
                id=job_id,
                role=str(raw.get("role") or raw.get("title") or "Untitled role"),
                company=str(raw.get("company") or "Unknown company"),
                location=str(raw.get("location") or "Remote"),
            )
            db.session.add(row)
        row.role = str(raw.get("role") or raw.get("title") or row.role)
        row.company = str(raw.get("company") or row.company)
        row.location = str(raw.get("location") or row.location)
        row.offer_url = raw.get("offer_url") or raw.get("url") or raw.get("link") or row.offer_url
        row.contact_email = raw.get("contact_email") or raw.get("email") or row.contact_email
        row.recruiter_or_careers_url = raw.get("recruiter_or_careers_url") or raw.get("careers_url") or row.recruiter_or_careers_url
        row.salary = str(raw.get("salary") or row.salary or "Undisclosed")
        row.employment_type = str(raw.get("employment_type") or row.employment_type or "Full-time")
        if seen_on:
            row.first_seen_on = min(filter(None, [row.first_seen_on, seen_on]))
            row.last_seen_on = max(filter(None, [row.last_seen_on, seen_on]))
        return row

    def _import_application(self, item: JSONDict) -> None:
        job_id = str(item.get("job_id") or "")
        if not job_id:
            return
        self._upsert_job(item | {"id": job_id, "offer_url": item.get("job_url")}, _parse_date(item.get("applied_on")))
        row_id = str(item.get("application_id") or f"app-{job_id}")
        row = db.session.get(JobApplication, row_id) or db.session.execute(
            select(JobApplication).where(JobApplication.job_id == job_id)
        ).scalar_one_or_none()
        if not row:
            row = JobApplication(id=row_id, job_id=job_id, company=str(item.get("company") or "Unknown company"), role=str(item.get("role") or "Untitled role"), status=str(item.get("status") or "application_sent"))
            db.session.add(row)
        row.location = item.get("location")
        row.job_url = item.get("job_url")
        row.source_file = item.get("source_file")
        row.source_original_rank = item.get("source_original_rank")
        row.status = str(item.get("status") or "application_sent")
        row.applied_on = _parse_date(item.get("applied_on"))
        row.status_updated_on = _parse_date(item.get("status_updated_on"))
        row.next_action = item.get("next_action")
        row.next_action_date = _parse_date(item.get("next_action_date"))
        row.contacts = item.get("contacts") or []
        row.notes = item.get("notes") or []
        row.raw_json = item

    def _import_exclusion(self, item: JSONDict) -> None:
        job_id = str(item.get("job_id") or "")
        if not job_id:
            return
        self._upsert_job(item | {"id": job_id, "offer_url": item.get("job_url")}, _parse_date(item.get("excluded_on")))
        row_id = str(item.get("exclusion_id") or f"exclude-{job_id}")
        row = db.session.get(JobExclusion, row_id) or db.session.execute(
            select(JobExclusion).where(JobExclusion.job_id == job_id)
        ).scalar_one_or_none()
        if not row:
            row = JobExclusion(id=row_id, job_id=job_id, company=str(item.get("company") or "Unknown company"), role=str(item.get("role") or "Untitled role"), reason=str(item.get("reason") or "User removed"))
            db.session.add(row)
        row.job_url = item.get("job_url")
        row.source_file = item.get("source_file")
        row.source_original_rank = item.get("source_original_rank")
        row.status = str(item.get("status") or "user_removed")
        row.reason = str(item.get("reason") or "User removed")
        row.keep_out = bool(item.get("keep_out_of_future_results", True))
        row.excluded_on = _parse_date(item.get("excluded_on"))
        row.raw_json = item
