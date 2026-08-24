from __future__ import annotations

import json
import re
import threading
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from models import CandidateProfile, JobApplication, JobExclusion, JobListing, db


JSONDict = dict[str, Any]
_WRITE_LOCK = threading.Lock()
_DATE_RE = re.compile(r"job_search_(\d{4}-\d{2}-\d{2})(?:-rerun(?:-(\d+))?)?\.json$")


def _read_json(path: Path, default: JSONDict | None = None) -> JSONDict:
    if not path.exists():
        return default or {}
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _atomic_write_json(path: Path, payload: JSONDict) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    temp_path.replace(path)


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


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


class JobRepository:
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

    def latest_run_path(self) -> Path:
        files = self.run_files()
        if not files:
            raise FileNotFoundError("No job_search_YYYY-MM-DD.json files were found.")
        return files[0]

    def load_profile(self) -> JSONDict:
        return _read_json(self.profile_path)

    def load_applications(self) -> JSONDict:
        return _read_json(
            self.applications_path,
            {
                "schema_version": "1.0",
                "created_on": date.today().isoformat(),
                "last_updated": date.today().isoformat(),
                "status_values": ["application_sent"],
                "applications": [],
            },
        )

    def load_exclusions(self) -> JSONDict:
        return _read_json(
            self.exclusions_path,
            {
                "schema_version": "1.0",
                "created_on": date.today().isoformat(),
                "last_updated": date.today().isoformat(),
                "status_values": ["user_removed"],
                "exclusions": [],
            },
        )

    def _status_maps(self) -> tuple[dict[str, JSONDict], dict[str, JSONDict]]:
        applications = {
            str(item.get("job_id")): item
            for item in self.load_applications().get("applications", [])
            if item.get("job_id")
        }
        exclusions = {
            str(item.get("job_id")): item
            for item in self.load_exclusions().get("exclusions", [])
            if item.get("job_id")
        }
        return applications, exclusions

    def normalize_job(
        self,
        raw: JSONDict,
        applications: dict[str, JSONDict],
        exclusions: dict[str, JSONDict],
    ) -> JSONDict:
        job_id = str(raw.get("job_id") or raw.get("id") or _slug(f"{raw.get('company', '')}-{raw.get('role', '')}"))
        status = "available"
        if job_id in applications:
            status = "applied"
        elif job_id in exclusions:
            status = "rejected"

        return {
            "id": job_id,
            "rank": raw.get("rank"),
            "role": raw.get("role") or raw.get("title") or "Untitled role",
            "company": raw.get("company") or "Unknown company",
            "location": raw.get("location") or "Remote",
            "posted": raw.get("posted") or raw.get("posted_date"),
            "posted_evidence": raw.get("posted_evidence"),
            "score": int(raw.get("score") or 0),
            "score_breakdown": raw.get("score_breakdown") or {},
            "salary": raw.get("salary") or "Undisclosed",
            "employment_type": raw.get("employment_type") or "Full-time",
            "offer_url": raw.get("offer_url") or raw.get("url") or raw.get("link"),
            "contact_email": raw.get("contact_email") or raw.get("email"),
            "recruiter_or_careers_url": raw.get("recruiter_or_careers_url") or raw.get("careers_url"),
            "suggested_resume": raw.get("suggested_resume") or raw.get("suggested_resume_variant") or "Rodolfo_Rojas_General_CV.pdf",
            "strategic_note": raw.get("strategic_note") if int(raw.get("score") or 0) >= 70 else None,
            "live_check": raw.get("live_check"),
            "is_new": bool(raw.get("new") or raw.get("is_new")),
            "status": status,
        }

    def dashboard(self) -> JSONDict:
        run_path = self.latest_run_path()
        run = _read_json(run_path)
        applications, exclusions = self._status_maps()
        jobs = [self.normalize_job(item, applications, exclusions) for item in run.get("results", run.get("roles", []))]

        board_checks = run.get("corrected_board_rerun", []) or run.get("board_checks", [])
        blocked_sources = [
            {"site": item.get("site", "Unknown site"), "details": item.get("outcome") or item.get("reason") or "Access was blocked."}
            for item in board_checks
            if str(item.get("status", "")).lower() in {"blocked", "login_required", "login wall"}
        ]
        audit_notes = run.get("audit_notes", [])
        if isinstance(audit_notes, str):
            audit_notes = [audit_notes]

        comparison = run.get("comparison_with_previous_rerun") or run.get("comparison_with_previous") or {}
        summary = run.get("search_summary") or {}
        if not summary:
            summary = {
                "distinct_candidates_reviewed": len(jobs),
                "passed_all_filters": len(jobs),
                "rejected_or_unverifiable": 0,
            }

        profile = self.load_profile()
        variants = [
            {
                "key": key,
                "label": value.get("label", key),
                "headline": value.get("headline", ""),
                "pdf": f"Rodolfo_Rojas_{'React_Node' if key == 'react-node' else key.title()}_CV.pdf",
            }
            for key, value in (profile.get("variants") or {}).items()
        ]

        return {
            "run": {
                "date": run.get("report_date") or run.get("run_date") or _run_key(run_path)[0].isoformat(),
                "timezone": run.get("timezone"),
                "source_file": run_path.name,
            },
            "summary": summary,
            "jobs": jobs,
            "top_three": run.get("top_three") or [],
            "comparison": {
                "added": comparison.get("added", []),
                "retained": comparison.get("retained", []),
                "dropped": comparison.get("dropped", []),
            },
            "issues": audit_notes,
            "blocked_sources": blocked_sources,
            "resume_variants": variants,
        }

    def find_job(self, job_id: str) -> JSONDict | None:
        for job in self.dashboard()["jobs"]:
            if job["id"] == job_id:
                return job
        return None

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
        with _WRITE_LOCK:
            payload = self.load_applications()
            for item in payload.get("applications", []):
                if item.get("job_id") == job["id"]:
                    return item
            today = date.today().isoformat()
            record = {
                "application_id": f"app-{job['id']}-{today.replace('-', '')}",
                "job_id": job["id"],
                "company": job["company"],
                "role": job["role"],
                "location": job["location"],
                "job_url": job.get("offer_url"),
                "source_file": self.latest_run_path().name,
                "source_original_rank": job.get("rank"),
                "applied_on": today,
                "status": "application_sent",
                "status_updated_on": today,
                "next_action": "Await response",
                "next_action_date": None,
                "contacts": [],
                "notes": ["Marked as applied from Role Radar."],
            }
            payload.setdefault("applications", []).append(record)
            payload["last_updated"] = today
            _atomic_write_json(self.applications_path, payload)
            return record

    def mark_rejected(self, job: JSONDict) -> JSONDict:
        with _WRITE_LOCK:
            payload = self.load_exclusions()
            for item in payload.get("exclusions", []):
                if item.get("job_id") == job["id"]:
                    return item
            today = date.today().isoformat()
            record = {
                "exclusion_id": f"exclude-{job['id']}-{today.replace('-', '')}",
                "job_id": job["id"],
                "company": job["company"],
                "role": job["role"],
                "source_file": self.latest_run_path().name,
                "source_original_rank": job.get("rank"),
                "excluded_on": today,
                "status": "user_removed",
                "reason": "Marked as rejected from Role Radar.",
                "keep_out_of_future_results": True,
            }
            payload.setdefault("exclusions", []).append(record)
            payload["last_updated"] = today
            _atomic_write_json(self.exclusions_path, payload)
            return record

    def sync_database(self) -> None:
        dashboard = self.dashboard()
        profile = self.load_profile()
        display_name = (profile.get("basics") or {}).get("name") or "Candidate"
        profile_row = db.session.get(CandidateProfile, 1) or CandidateProfile(id=1, display_name=display_name, raw_json="{}")
        profile_row.display_name = display_name
        profile_row.raw_json = json.dumps(profile, ensure_ascii=False)
        db.session.add(profile_row)

        for job in dashboard["jobs"]:
            row = db.session.get(JobListing, job["id"]) or JobListing(
                id=job["id"], role=job["role"], company=job["company"], location=job["location"], score=job["score"], run_file=dashboard["run"]["source_file"], raw_json="{}"
            )
            row.role = job["role"]
            row.company = job["company"]
            row.location = job["location"]
            row.score = job["score"]
            row.posted_on = _parse_date(job.get("posted"))
            row.is_new = job["is_new"]
            row.run_file = dashboard["run"]["source_file"]
            row.raw_json = json.dumps(job, ensure_ascii=False)
            db.session.add(row)

        for item in self.load_applications().get("applications", []):
            row_id = str(item.get("application_id") or f"app-{item.get('job_id')}")
            row = db.session.get(JobApplication, row_id) or JobApplication(
                id=row_id, job_id=str(item.get("job_id", "")), company=str(item.get("company", "")), role=str(item.get("role", "")), status=str(item.get("status", "application_sent")), raw_json="{}"
            )
            row.applied_on = _parse_date(item.get("applied_on"))
            row.raw_json = json.dumps(item, ensure_ascii=False)
            db.session.add(row)

        for item in self.load_exclusions().get("exclusions", []):
            row_id = str(item.get("exclusion_id") or f"exclude-{item.get('job_id')}")
            row = db.session.get(JobExclusion, row_id) or JobExclusion(
                id=row_id, job_id=str(item.get("job_id", "")), company=str(item.get("company", "")), role=str(item.get("role", "")), reason=str(item.get("reason", "User removed")), raw_json="{}"
            )
            row.keep_out = bool(item.get("keep_out_of_future_results", True))
            row.excluded_on = _parse_date(item.get("excluded_on"))
            row.raw_json = json.dumps(item, ensure_ascii=False)
            db.session.add(row)

        db.session.commit()

