from typing import Annotated
from fastapi import APIRouter, status, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.models.models import Job, BotState
from backend.database.database import get_db
from backend.schemas.schemas import JobResponse
from datetime import datetime, UTC
import json
import numpy as np
import re
from backend.core.security import verify_bot_key
from huggingface_hub import InferenceClient
import os


router = APIRouter(prefix="/bot", tags=["Bot"])

client = InferenceClient(
    model="sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
    token=os.getenv("HF_TOKEN"),
)

def cosine_similarity(vec1, vec2):
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def extract_query_signals(query: str):
    """Simple extraction of signals like requested salary from user's free text."""
    signals = {"min_salary": None, "remote": None}

    # Looks for numbers like 100k, 100000, 100,000
    salary_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*[kK]?\+?\$?', query)
    if salary_match:
        raw = salary_match.group(1).replace(",", "")
        num = int(raw)
        if 'k' in query.lower() and num < 1000:
            num *= 1000
        if num >= 10000:  # avoid matching small random numbers
            signals["min_salary"] = num

    if re.search(r'\bremote\b', query, re.IGNORECASE):
        signals["remote"] = True

    return signals


def salary_score(query_min_salary, job_min, job_max):
    """1.0 if the requested salary falls inside the job's range, lower otherwise."""
    if query_min_salary is None or job_min is None or job_max is None:
        return 0.5  # not enough info, neutral score
    if job_min <= query_min_salary <= job_max:
        return 1.0
    # the further the requested salary is from the range, the lower the score
    distance = min(abs(query_min_salary - job_min), abs(query_min_salary - job_max))
    return max(0.0, 1.0 - distance / max(query_min_salary, 1))


@router.get("/jobs/similar")
def find_similar_jobs(
    query: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(verify_bot_key)],
    top_n: int = Query(5, le=20),
):
    """
    Takes a free-text description from the user (their requirements or experience),
    and returns the closest matching jobs by meaning, ranked by combined score.
    """

    query_embedding = client.feature_extraction(query).tolist()
    signals = extract_query_signals(query)

    stmt = select(Job.rowid, Job.title, Job.company, Job.location,
                  Job.min_salary, Job.max_salary, Job.currency, Job.job_link, Job.embedding)
    rows = db.execute(stmt).all()

    scored = []
    for row in rows:
        if not row.embedding:
            continue  # jobs without an embedding (rare, e.g. empty description)
        job_embedding = json.loads(row.embedding)
        sim_score = cosine_similarity(query_embedding, job_embedding)

        sal_score = salary_score(signals["min_salary"], row.min_salary, row.max_salary)

        location_text = (row.location or "").lower()
        loc_score = 1.0 if (signals["remote"] and "remote" in location_text) else (
            0.5 if signals["remote"] is None else 0.3
        )

        # weighting: semantic meaning matters most, then salary, then location
        final_score = 0.6 * sim_score + 0.25 * sal_score + 0.15 * loc_score
        scored.append((row, final_score, sim_score))

    # sort by combined score, highest first
    scored.sort(key=lambda x: x[1], reverse=True)
    top_results = scored[:top_n]

    return [
        {
            "rowid": row.rowid,
            "title": row.title,
            "company": row.company,
            "location": row.location,
            "min_salary": row.min_salary,
            "max_salary": row.max_salary,
            "currency": row.currency,
            "match_percentage": round(final_score * 100, 1),
            "semantic_similarity": round(sim_score * 100, 1),  # for debugging, can remove later
            "job_link": row.job_link,
            
        }
        for row, final_score, sim_score in top_results
    ]




@router.get("/jobs/new-since-last-check", response_model=list[JobResponse])
def peek_new_jobs(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(verify_bot_key)],
):
    state = db.get(BotState, 1)
    cutoff = state.last_checked_at if state else datetime.min.replace(tzinfo=UTC)
    stmt = select(Job).where(Job.first_seen_at > cutoff)
    return db.execute(stmt).scalars().all()



@router.post("/jobs/mark-checked", status_code=status.HTTP_204_NO_CONTENT)
def mark_checked(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(verify_bot_key)],
):
    state = db.get(BotState, 1)
    if state is None:
        state = BotState(id=1, last_checked_at=datetime.now(UTC))
        db.add(state)
    else:
        state.last_checked_at = datetime.now(UTC)
    db.commit()