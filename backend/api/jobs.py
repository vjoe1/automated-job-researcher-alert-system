from typing import Annotated, Optional
from fastapi import HTTPException, Depends, Query, APIRouter
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from backend.models.models import Job
from backend.database.database import get_db
from backend.schemas.schemas import JobResponse, SortBy, PostedRange, RemoteMode, ExperienceLevel
from backend.core.constants import POSTED_RANGE_DAYS, EXPERIENCE_LEVEL_YEARS
import time
from sqlalchemy.orm import defer


router = APIRouter(prefix="/jobs", tags=["Jobs"])



@router.get("/count")
def get_jobs_count(db: Annotated[Session, Depends(get_db)]):
    total = db.execute(select(func.count(Job.rowid))).scalar_one()
    return {"total": total}


@router.get("", response_model=list[JobResponse])
def get_jobs(
    db: Annotated[Session, Depends(get_db)],

    # Search
    title: Optional[str] = None,
    company: Optional[list[str]] = Query(None, description="company or more "),
    description_q: Optional[str] = Query(None, alias="description"),
    q: Optional[str] = Query(None, description= " global search title + company + description"),

    # Filters
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    remote: Optional[RemoteMode] = None,
    min_salary: Optional[float] = None,
    max_salary: Optional[float] = None,
    currency: Optional[str] = None,
    posted: Optional[PostedRange] = None,
    experience_level: Optional[ExperienceLevel] = None,
    actively_hiring: Optional[bool] = None,

    # Sorting
    sort_by: SortBy = SortBy.newest,

    limit: Optional[int] = Query(
    None,
    ge=1,
    le=5000,
    description="Optional result limit. Leave empty to return all matching rows (capped at 5000)."),
    offset: int = Query(
    0,
    ge=0,
    le=10000,
    description="pagination"
),
):
    stmt = select(Job).options(defer(Job.embedding))

    # --- Search ---
    if title:
        stmt = stmt.where(Job.title.ilike(f"%{title}%"))

    if company:
        stmt = stmt.where(Job.company.in_(company))

    if description_q:
        stmt = stmt.where(Job.description.ilike(f"%{description_q}%"))

    if q:
        stmt = stmt.where(
            or_(
                Job.title.ilike(f"%{q}%"),
                Job.company.ilike(f"%{q}%"),
                Job.description.ilike(f"%{q}%"),
            )
        )

    # --- Filters ---
    if job_type:
        stmt = stmt.where(Job.job_type.ilike(f"%{job_type}%"))

    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))

    if remote == RemoteMode.remote_only:
        stmt = stmt.where(Job.location.ilike("%remote%"))
    elif remote == RemoteMode.onsite_only:
        stmt = stmt.where(Job.location.ilike("%onsite%"))
    elif remote == RemoteMode.remote_and_onsite:
        stmt = stmt.where(
            or_(Job.location.ilike("%remote%"), Job.location.ilike("%onsite%"))
        )

    if currency:
        stmt = stmt.where(Job.currency == currency)

    if min_salary is not None:
        stmt = stmt.where(
            or_(Job.max_salary >= min_salary, Job.max_salary.is_(None))
        )

    if max_salary is not None:
        stmt = stmt.where(
            or_(Job.min_salary <= max_salary, Job.min_salary.is_(None))
        )

    if posted is not None:
        stmt = stmt.where(Job.days_since_posted <= POSTED_RANGE_DAYS[posted])

    if experience_level is not None:
        lower, upper = EXPERIENCE_LEVEL_YEARS[experience_level]
        stmt = stmt.where(
            or_(Job.max_years.is_(None), Job.max_years >= lower),
            or_(Job.min_years.is_(None), Job.min_years <= upper),
        )

    if actively_hiring is True:
        stmt = stmt.where(Job.hiring.ilike("%actively%"))
    elif actively_hiring is False:
        stmt = stmt.where(
            or_(Job.hiring.is_(None), ~Job.hiring.ilike("%actively%"))
        )

    # --- Sorting ---
    if sort_by == SortBy.newest:
        pass
    elif sort_by == SortBy.oldest:
        stmt = stmt.order_by(Job.days_since_posted.is_(None), Job.days_since_posted.desc())
    elif sort_by == SortBy.salary_high:
        stmt = stmt.order_by(Job.max_salary.is_(None), Job.max_salary.desc())
    elif sort_by == SortBy.salary_low:
        stmt = stmt.order_by(Job.min_salary.is_(None), Job.min_salary.asc())
    elif sort_by == SortBy.company_asc:
        stmt = stmt.order_by(Job.company.asc())
    elif sort_by == SortBy.company_desc:
        stmt = stmt.order_by(Job.company.desc())


    stmt = stmt.offset(offset)

    if limit is not None:
        stmt = stmt.limit(limit)

    start = time.perf_counter()

    results = db.execute(stmt).scalars().all()

    elapsed = time.perf_counter() - start
    print(f"[TIMING] execute={elapsed:.3f}s rows={len(results)}")

    return results



@router.get("/{rowid}", response_model=JobResponse)
def get_job(rowid: int, db: Annotated[Session, Depends(get_db)]):
    job = db.get(Job, rowid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job