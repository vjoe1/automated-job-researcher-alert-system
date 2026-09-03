import os
import psycopg
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("PSYCOPG_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

def init_db() -> None:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scraped_jobs (
                    company TEXT,
                    company_link TEXT,
                    hiring TEXT,
                    description TEXT,
                    employees TEXT,
                    title TEXT,
                    job_link TEXT PRIMARY KEY,
                    job_type TEXT,
                    salary TEXT,
                    experience TEXT,
                    location TEXT,
                    posted TEXT,
                    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen_at TIMESTAMP
                )
            """)


def save_checkpoint(all_data: list, page_number: int) -> None:
    if not all_data:
        return

    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.executemany("""
                    INSERT INTO scraped_jobs (
                        company, company_link, hiring, description, employees,
                        title, job_link, job_type, salary, experience, location, posted,
                        last_seen_at
                    )
                    VALUES (
                        %(company)s, %(company_link)s, %(hiring)s, %(description)s,
                        %(employees)s, %(title)s, %(job_link)s, %(job_type)s,
                        %(salary)s, %(experience)s, %(location)s, %(posted)s,
                        CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (job_link) DO UPDATE SET
                        company = EXCLUDED.company,
                        company_link = EXCLUDED.company_link,
                        hiring = EXCLUDED.hiring,
                        description = EXCLUDED.description,
                        employees = EXCLUDED.employees,
                        title = EXCLUDED.title,
                        job_type = EXCLUDED.job_type,
                        salary = EXCLUDED.salary,
                        experience = EXCLUDED.experience,
                        location = EXCLUDED.location,
                        posted = EXCLUDED.posted,
                        last_seen_at = CURRENT_TIMESTAMP
                """, all_data)

        print(f"✅ Page {page_number} done — {len(all_data)} jobs upserted")

    except Exception as e:
        print(f"ERROR on {page_number}: {e}")