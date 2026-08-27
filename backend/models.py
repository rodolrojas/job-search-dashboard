from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
JSON_DOCUMENT = JSON().with_variant(JSONB, "postgresql")


def utc_now() -> datetime:
    return datetime.now(UTC)


class JobSearchRun(db.Model):
    __tablename__ = "job_search_runs"

    id: Mapped[str] = mapped_column(String(240), primary_key=True)
    source_file: Mapped[str] = mapped_column(String(240), unique=True, nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    run_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    timezone: Mapped[str | None] = mapped_column(String(80))
    summary: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    top_three: Mapped[list[Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=list)
    comparison: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    issues: Mapped[list[Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=list)
    blocked_sources: Mapped[list[Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=list)
    agent_metadata: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    listings: Mapped[list[JobRunListing]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="JobRunListing.rank",
    )

    __table_args__ = (Index("ix_job_search_runs_latest", "report_date", "run_number"),)


class Job(db.Model):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(180), primary_key=True)
    role: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    offer_url: Mapped[str | None] = mapped_column(Text)
    contact_email: Mapped[str | None] = mapped_column(String(320))
    recruiter_or_careers_url: Mapped[str | None] = mapped_column(Text)
    salary: Mapped[str] = mapped_column(String(240), nullable=False, default="Undisclosed")
    employment_type: Mapped[str] = mapped_column(String(80), nullable=False, default="Full-time")
    first_seen_on: Mapped[date | None] = mapped_column(Date)
    last_seen_on: Mapped[date | None] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    listings: Mapped[list[JobRunListing]] = relationship(back_populates="job")


class JobRunListing(db.Model):
    __tablename__ = "job_run_listings"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("job_search_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    rank: Mapped[int | None] = mapped_column(Integer)
    posted_on: Mapped[date | None] = mapped_column(Date, index=True)
    posted_evidence: Mapped[str | None] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    score_breakdown: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    suggested_resume: Mapped[str] = mapped_column(String(240), nullable=False, default="Rodolfo_Rojas_General_CV.pdf")
    strategic_note: Mapped[str | None] = mapped_column(Text)
    live_check: Mapped[str | None] = mapped_column(Text)
    source_name: Mapped[str | None] = mapped_column(String(240))
    requirements_summary: Mapped[str | None] = mapped_column(Text)
    is_new: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)

    run: Mapped[JobSearchRun] = relationship(back_populates="listings")
    job: Mapped[Job] = relationship(back_populates="listings")

    __table_args__ = (
        UniqueConstraint("run_id", "job_id", name="uq_job_run_listings_run_job"),
        Index("ix_job_run_listings_run_rank", "run_id", "rank"),
        Index("ix_job_run_listings_run_score", "run_id", "score"),
    )


class CandidateProfile(db.Model):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    display_name: Mapped[str] = mapped_column(String(180), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    location: Mapped[str | None] = mapped_column(String(240))
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    variants: Mapped[list[ResumeVariant]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class ResumeVariant(db.Model):
    __tablename__ = "resume_variants"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, default=1)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    headline: Mapped[str] = mapped_column(Text, nullable=False, default="")
    pdf_filename: Mapped[str] = mapped_column(String(240), nullable=False)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)

    profile: Mapped[CandidateProfile] = relationship(back_populates="variants")


class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id: Mapped[str] = mapped_column(String(220), primary_key=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True)
    company: Mapped[str] = mapped_column(String(180), nullable=False)
    role: Mapped[str] = mapped_column(String(240), nullable=False)
    location: Mapped[str | None] = mapped_column(String(240))
    job_url: Mapped[str | None] = mapped_column(Text)
    source_file: Mapped[str | None] = mapped_column(String(240), index=True)
    source_original_rank: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    applied_on: Mapped[date | None] = mapped_column(Date, index=True)
    status_updated_on: Mapped[date | None] = mapped_column(Date)
    next_action: Mapped[str | None] = mapped_column(Text)
    next_action_date: Mapped[date | None] = mapped_column(Date)
    contacts: Mapped[list[Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=list)
    notes: Mapped[list[Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=list)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class JobExclusion(db.Model):
    __tablename__ = "job_exclusions"

    id: Mapped[str] = mapped_column(String(220), primary_key=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, unique=True)
    company: Mapped[str] = mapped_column(String(180), nullable=False)
    role: Mapped[str] = mapped_column(String(240), nullable=False)
    job_url: Mapped[str | None] = mapped_column(Text)
    source_file: Mapped[str | None] = mapped_column(String(240), index=True)
    source_original_rank: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(80), nullable=False, default="user_removed", index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    keep_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    excluded_on: Mapped[date | None] = mapped_column(Date, index=True)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class CoverLetter(db.Model):
    __tablename__ = "cover_letters"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_variant: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(String(40), nullable=False)
    warning: Mapped[str | None] = mapped_column(Text)
    filename: Mapped[str] = mapped_column(String(260), nullable=False)
    saved_to: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, index=True)


class AgentRun(db.Model):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    phase: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON_DOCUMENT)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    events: Mapped[list[AgentRunEvent]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="AgentRunEvent.sequence",
    )


class AgentRunEvent(db.Model):
    __tablename__ = "agent_run_events"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    phase: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON_DOCUMENT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    run: Mapped[AgentRun] = relationship(back_populates="events")

    __table_args__ = (UniqueConstraint("run_id", "sequence", name="uq_agent_run_events_run_sequence"),)


def model_counts() -> dict[str, Any]:
    return {
        "runs": db.session.query(JobSearchRun).count(),
        "jobs": db.session.query(Job).count(),
        "listings": db.session.query(JobRunListing).count(),
        "profiles": db.session.query(CandidateProfile).count(),
        "resume_variants": db.session.query(ResumeVariant).count(),
        "applications": db.session.query(JobApplication).count(),
        "exclusions": db.session.query(JobExclusion).count(),
        "cover_letters": db.session.query(CoverLetter).count(),
        "agent_runs": db.session.query(AgentRun).count(),
    }
