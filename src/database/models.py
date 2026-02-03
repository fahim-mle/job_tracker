from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    skills_raw: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String(2048), unique=True)
    posted_date: Mapped[Optional[date]] = mapped_column(Date)
    deadline: Mapped[Optional[date]] = mapped_column(Date)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="active",
    )
    source_platform: Mapped[Optional[str]] = mapped_column(String(100))
    raw_html: Mapped[Optional[str]] = mapped_column(Text)

    applications: Mapped[List[Application]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
    job_skills: Mapped[List[JobSkill]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
    skills: Mapped[List[Skill]] = relationship(
        secondary="job_skills",
        back_populates="jobs",
        viewonly=True,
    )


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    applied_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="applied",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    job: Mapped[Job] = relationship(back_populates="applications")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    frequency: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )

    job_skills: Mapped[List[JobSkill]] = relationship(
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    jobs: Mapped[List[Job]] = relationship(
        secondary="job_skills",
        back_populates="skills",
        viewonly=True,
    )


class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        primary_key=True,
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id"),
        primary_key=True,
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)

    job: Mapped[Job] = relationship(back_populates="job_skills")
    skill: Mapped[Skill] = relationship(back_populates="job_skills")
