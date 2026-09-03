from pydantic import BaseModel , ConfigDict
from enum import Enum


class JobResponse(BaseModel) :
    rowid: int
    title: str | None
    company: str | None
    location: str | None
    job_type: str | None
    experience: str | None
    min_years: int | None
    max_years: int | None
    min_salary: float | None
    max_salary: float | None
    currency: str | None
    posted: str | None
    job_link: str | None
    hiring: str | None

    model_config =ConfigDict(from_attributes=True)

class UserRegister(BaseModel):
    telegram_id: int
    username: str | None = None


class SortBy(str, Enum):
    newest = "newest"
    oldest = "oldest"
    salary_high = "salary_high"
    salary_low = "salary_low"
    company_asc = "company_asc"
    company_desc = "company_desc"




class PostedRange(str, Enum):
    today = "today"
    last_3_days = "last_3_days"
    last_week = "last_week"
    last_month = "last_month"



class RemoteMode(str, Enum):
    remote_only = "remote_only"
    remote_and_onsite = "remote_and_onsite"
    onsite_only = "onsite_only"



class ExperienceLevel(str, Enum):
    entry = "entry"
    mid = "mid"
    senior = "senior"
    staff = "staff"


class HiringStatus(str, Enum):
    actively_hiring = "actively_hiring"
    normal = "normal"

