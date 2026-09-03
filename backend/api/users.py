from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.models import Job, User, SavedJob
from database.database import get_db
from schemas.schemas import JobResponse, UserRegister
from core.security import verify_bot_key


router = APIRouter(prefix="/users", tags=["Users"])


def get_or_create_user(db: Session, telegram_id: int) -> User:
    user = db.execute(
        select(User).where(User.telegram_id == telegram_id)
    ).scalar_one_or_none()

    if user is None:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@router.post("/register")
def register_user(
    payload: UserRegister,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(verify_bot_key)],
):
    user = get_or_create_user(db, payload.telegram_id)

    if payload.username and user.username != payload.username:
        user.username = payload.username
        db.commit()

    return {"telegram_id": user.telegram_id, "username": user.username}


@router.get("/all-ids", response_model=list[int])
def get_all_user_ids(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(verify_bot_key)],
):
    users = db.execute(
        select(User.telegram_id)
        .where(User.notifications_enabled == True)
    ).scalars().all()

    return list(users)


@router.post("/{telegram_id}/saved-jobs/{rowid}", status_code=status.HTTP_201_CREATED)
def save_job(
    telegram_id: int,
    rowid: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(verify_bot_key)],
):
    job = db.get(Job, rowid)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    user = get_or_create_user(db, telegram_id)

    existing = db.execute(
        select(SavedJob).where(SavedJob.user_id == user.id, SavedJob.job_rowid == rowid)
    ).scalar_one_or_none()
    if existing:
        return {"detail": "Already saved"}

    db.add(SavedJob(user_id=user.id, job_rowid=rowid))
    db.commit()
    return {"detail": "Saved"}



@router.delete("/{telegram_id}/saved-jobs/{rowid}")
def unsave_job(
    telegram_id: int,
    rowid: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(verify_bot_key)],
):
    user = db.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    saved = db.execute(
        select(SavedJob).where(SavedJob.user_id == user.id, SavedJob.job_rowid == rowid)
    ).scalar_one_or_none()
    if not saved:
        raise HTTPException(status_code=404, detail="Not saved")

    db.delete(saved)
    db.commit()
    return {"detail": "Removed"}



@router.get("/{telegram_id}/saved-jobs", response_model=list[JobResponse])
def list_saved_jobs(
    telegram_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(verify_bot_key)],
):
    user = db.execute(
        select(User).where(User.telegram_id == telegram_id)
    ).scalar_one_or_none()

    if not user:
        return []

    stmt = (
        select(Job)
        .join(SavedJob, SavedJob.job_rowid == Job.rowid)
        .where(SavedJob.user_id == user.id)
    )

    return db.execute(stmt).scalars().all()

@router.post("/{telegram_id}/notifications")
def update_notifications(
    telegram_id: int,
    enabled: bool,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[None, Depends(verify_bot_key)],
):
    user = db.execute(
        select(User).where(User.telegram_id == telegram_id)
    ).scalar_one_or_none()

    if not user:
        return {"detail": "User not found"}

    user.notifications_enabled = enabled
    db.commit()

    return {
        "telegram_id": telegram_id,
        "notifications_enabled": user.notifications_enabled
    }
