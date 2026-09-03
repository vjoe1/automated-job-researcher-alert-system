import httpx
from config import API_URL, API_HEADERS, PAGE_SIZE



async def api_get(path: str, params: dict | None = None) -> dict | list:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{API_URL}{path}",
            params=params,
            headers=API_HEADERS
        )

        response.raise_for_status()
        return response.json()

    
async def api_post(path: str, json: dict | None = None) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}{path}", json=json, headers=API_HEADERS)
        response.raise_for_status()
        return response.json() if response.content else {}



async def get_job_count() -> int:
    data = await api_get("/jobs/count")
    return data["total"]



async def fetch_jobs(filters_dict: dict, offset: int = 0, limit: int = PAGE_SIZE) -> list[dict]:
    params = {k: v for k, v in filters_dict.items() if v is not None}
    params["limit"] = limit
    params["offset"] = offset
    return await api_get("/jobs", params=params)



async def fetch_similar_jobs(query: str, top_n: int = PAGE_SIZE) -> list[dict]:
    return await api_get("/bot/jobs/similar", params={"query": query, "top_n": top_n})



async def register_user(telegram_id: int, username: str | None):
    await api_post("/users/register", {"telegram_id": telegram_id, "username": username})



async def save_job_for_user(telegram_id: int, rowid: int):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_URL}/users/{telegram_id}/saved-jobs/{rowid}", headers=API_HEADERS)
        r.raise_for_status()


async def get_new_jobs_since_last_check() -> list[dict]:
    """Fetch all new jobs discovered since the last check cutoff."""
    return await api_get("/bot/jobs/new-since-last-check")


async def mark_jobs_checked():
    """Update the last_checked_at timestamp in the database."""
    await api_post("/bot/jobs/mark-checked")


async def get_all_user_ids() -> list[int]:
    """Retrieve all registered Telegram user IDs."""
    return await api_get("/users/all-ids")

async def update_notifications(telegram_id: int, enabled: bool):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/users/{telegram_id}/notifications",
            params={"enabled": enabled},
            headers=API_HEADERS
        )
        response.raise_for_status()
        return response.json()