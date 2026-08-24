from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class JobListing(db.Model):
    __tablename__ = "job_listings"

    id: Mapped[str] = mapped_column(String(180), primary_key=True)
    role: Mapped[str] = mapped_column(String(240), index=True)
    company: Mapped[str] = mapped_column(String(180), index=True)
    location: Mapped[str] = mapped_column(String(240), index=True)
    score: Mapped[int] = mapped_column(Integer, index=True)
    posted_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_new: Mapped[bool] = mapped_column(Boolean, default=False)
    run_file: Mapped[str] = mapped_column(String(240), index=True)
    raw_json: Mapped[str] = mapped_column(Text)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class CandidateProfile(db.Model):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    display_name: Mapped[str] = mapped_column(String(180))
    raw_json: Mapped[str] = mapped_column(Text)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id: Mapped[str] = mapped_column(String(220), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(180), index=True)
    company: Mapped[str] = mapped_column(String(180))
    role: Mapped[str] = mapped_column(String(240))
    status: Mapped[str] = mapped_column(String(80), index=True)
    applied_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    raw_json: Mapped[str] = mapped_column(Text)


class JobExclusion(db.Model):
    __tablename__ = "job_exclusions"

    id: Mapped[str] = mapped_column(String(220), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(180), index=True)
    company: Mapped[str] = mapped_column(String(180))
    role: Mapped[str] = mapped_column(String(240))
    reason: Mapped[str] = mapped_column(Text)
    keep_out: Mapped[bool] = mapped_column(Boolean, default=True)
    excluded_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    raw_json: Mapped[str] = mapped_column(Text)


def model_counts() -> dict[str, Any]:
    return {
        "jobs": db.session.query(JobListing).count(),
        "profiles": db.session.query(CandidateProfile).count(),
        "applications": db.session.query(JobApplication).count(),
        "exclusions": db.session.query(JobExclusion).count(),
    }
