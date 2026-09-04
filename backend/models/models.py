from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text , Float , UniqueConstraint , BigInteger , Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base


class Job(Base):
    __tablename__ = "jobs_cleaned"

    rowid: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    autoincrement=True)

    job_link: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )
    company: Mapped[str | None] = mapped_column(String)
    company_link: Mapped[str | None] = mapped_column(String)
    hiring: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    employees: Mapped[str | None] = mapped_column(String)
    title: Mapped[str | None] = mapped_column(String)
    job_type: Mapped[str | None] = mapped_column(String)
    salary: Mapped[str | None] = mapped_column(String)
    experience: Mapped[str | None] = mapped_column(String)
    location: Mapped[str | None] = mapped_column(String)
    posted: Mapped[str | None] = mapped_column(String)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    min_years: Mapped[int | None] = mapped_column(Integer)
    max_years: Mapped[int | None] = mapped_column(Integer)
    days_since_posted: Mapped[int | None] = mapped_column(Integer)
    min_employees: Mapped[int | None] = mapped_column(Integer)
    max_employees: Mapped[int | None] = mapped_column(Integer)
    currency: Mapped[str | None] = mapped_column(String)
    min_salary: Mapped[float | None] = mapped_column(Float)
    max_salary: Mapped[float | None] = mapped_column(Float)
    salary_clean: Mapped[str | None] = mapped_column(String)
    embedding: Mapped[str | None] = mapped_column(String)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    saved_jobs: Mapped[list["SavedJob"]] = relationship(back_populates="user")


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "job_rowid", name="uq_user_job"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    job_rowid: Mapped[int] = mapped_column(
        ForeignKey("jobs_cleaned.rowid"),
        index=True
    )
    saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    user: Mapped["User"] = relationship(
        back_populates="saved_jobs"
    )

    job: Mapped["Job"] = relationship()



class BotState(Base):
    __tablename__ = "bot_state"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=1)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))