import os
import psycopg
import pandas as pd
from dotenv import load_dotenv
from data_cleaning import (
    extract_years,
    extract_days_ago,
    extract_employees,
    extract_currency,
    normalize_currency,
    extract_salary_min_max,
    extract_salary_range,
)

from datetime import UTC, datetime

load_dotenv()

DATABASE_URL = os.getenv("PSYCOPG_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("PSYCOPG_DATABASE_URL is not set")

def update_jobs_database(df):
    now = datetime.now(UTC)

    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:

                for _, row in df.iterrows():

                    cur.execute(
                        """
                        UPDATE jobs_cleaned
                        SET
                            company = %(company)s,
                            company_link = %(company_link)s,
                            hiring = %(hiring)s,
                            description = %(description)s,
                            employees = %(employees)s,
                            title = %(title)s,
                            job_type = %(job_type)s,
                            salary = %(salary)s,
                            experience = %(experience)s,
                            location = %(location)s,
                            posted = %(posted)s,
                            last_seen_at = %(last_seen_at)s,
                            min_years = %(min_years)s,
                            max_years = %(max_years)s,
                            days_since_posted = %(days_since_posted)s,
                            min_employees = %(min_employees)s,
                            max_employees = %(max_employees)s,
                            currency = %(currency)s,
                            min_salary = %(min_salary)s,
                            max_salary = %(max_salary)s,
                            salary_clean = %(salary_clean)s
                        WHERE job_link = %(job_link)s
                        """,
                        {
                            "company": row["company"],
                            "company_link": row["company_link"],
                            "hiring": row["hiring"],
                            "description": row["description"],
                            "employees": row["employees"],
                            "title": row["title"],
                            "job_type": row["job_type"],
                            "salary": row["salary"],
                            "experience": row["experience"],
                            "location": row["location"],
                            "posted": row["posted"],
                            "last_seen_at": now,
                            "min_years": row["min_years"],
                            "max_years": row["max_years"],
                            "days_since_posted": row["days_since_posted"],
                            "min_employees": row["min_employees"],
                            "max_employees": row["max_employees"],
                            "currency": row["currency"],
                            "min_salary": row["min_salary"],
                            "max_salary": row["max_salary"],
                            "salary_clean": row["salary_clean"],
                            "job_link": row["job_link"],
                        },
                    )

                    if cur.rowcount == 0:
                        cur.execute(
                            """
                            INSERT INTO jobs_cleaned (
                                job_link,
                                company,
                                company_link,
                                hiring,
                                description,
                                employees,
                                title,
                                job_type,
                                salary,
                                experience,
                                location,
                                posted,
                                first_seen_at,
                                last_seen_at,
                                min_years,
                                max_years,
                                days_since_posted,
                                min_employees,
                                max_employees,
                                currency,
                                min_salary,
                                max_salary,
                                salary_clean,
                                embedding
                            )
                            VALUES (
                                %(job_link)s,
                                %(company)s,
                                %(company_link)s,
                                %(hiring)s,
                                %(description)s,
                                %(employees)s,
                                %(title)s,
                                %(job_type)s,
                                %(salary)s,
                                %(experience)s,
                                %(location)s,
                                %(posted)s,
                                %(first_seen_at)s,
                                %(last_seen_at)s,
                                %(min_years)s,
                                %(max_years)s,
                                %(days_since_posted)s,
                                %(min_employees)s,
                                %(max_employees)s,
                                %(currency)s,
                                %(min_salary)s,
                                %(max_salary)s,
                                %(salary_clean)s,
                                NULL
                            )
                            """,
                            {
                                "job_link": row["job_link"],
                                "company": row["company"],
                                "company_link": row["company_link"],
                                "hiring": row["hiring"],
                                "description": row["description"],
                                "employees": row["employees"],
                                "title": row["title"],
                                "job_type": row["job_type"],
                                "salary": row["salary"],
                                "experience": row["experience"],
                                "location": row["location"],
                                "posted": row["posted"],
                                "first_seen_at": now,
                                "last_seen_at": now,
                                "min_years": row["min_years"],
                                "max_years": row["max_years"],
                                "days_since_posted": row["days_since_posted"],
                                "min_employees": row["min_employees"],
                                "max_employees": row["max_employees"],
                                "currency": row["currency"],
                                "min_salary": row["min_salary"],
                                "max_salary": row["max_salary"],
                                "salary_clean": row["salary_clean"],
                            },
                        )

        print("Database updated successfully.")

    except Exception as e:
        print(f"Database update failed: {e}")

        
def main() :
    with psycopg.connect(DATABASE_URL) as conn:
        df = pd.read_sql("SELECT * FROM scraped_jobs", conn)
        df = df.replace("-", pd.NA)

    df[['min_years', 'max_years']] = df['experience'].apply(lambda x: pd.Series(extract_years(x)))
    df['days_since_posted'] = df['posted'].apply(extract_days_ago)
    df['days_since_posted'] = df['days_since_posted'].astype('Int64')
    df[['min_employees', 'max_employees']] = df['employees'].apply(lambda x: pd.Series(extract_employees(x)))
    df['currency'] = df['salary'].apply(extract_currency)
    df['currency'] = df['currency'].apply(normalize_currency)
    df[['min_salary', 'max_salary']] = df['salary'].apply(lambda x: pd.Series(extract_salary_min_max(x)))
    df['salary_clean'] = df.apply(lambda row: extract_salary_range(row['salary'], row['currency']), axis=1)
    df['min_salary'] = df['min_salary'].astype('Float64')
    df['max_salary'] = df['max_salary'].astype('Float64')
    df['min_employees'] = df['min_employees'].astype('Int64')
    df['max_employees'] = df['max_employees'].astype('Int64')
    df['min_years'] = df['min_years'].astype('Int64')
    df['max_years'] = df['max_years'].astype('Int64')
    df = df.astype(object).where(pd.notna(df), None)
    update_jobs_database(df)
    
if __name__ == "__main__":
    main()