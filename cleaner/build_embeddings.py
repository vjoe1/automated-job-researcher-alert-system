import os
import json
import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


load_dotenv()

DATABASE_URL = os.getenv("PSYCOPG_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("PSYCOPG_DATABASE_URL is not set")

print("Loading model (first run only, will be cached after)...")

model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")


conn = psycopg.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
    SELECT rowid, title, description
    FROM jobs_cleaned
    WHERE embedding IS NULL
""")

rows = cur.fetchall()

print(f"Computing embeddings for {len(rows)} jobs...")


# Prepare texts and rowids
valid_rowids = []
texts = []

for rowid, title, description in rows:

    text = f"{title or ''}. {description or ''}".strip()

    if not text or text == ".":
        continue

    valid_rowids.append(rowid)
    texts.append(text)


if texts:

    BATCH_SIZE = 64

    all_embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    print("Saving results to the database...")

    for i, (rowid, embedding) in enumerate(
        zip(valid_rowids, all_embeddings),
        start=1
    ):
        cur.execute(
                    """
                    UPDATE jobs_cleaned
                    SET embedding = %(embedding)s
                    WHERE rowid = %(rowid)s
                    """,
                    {
                        "embedding": json.dumps(embedding.tolist()),
                        "rowid": rowid,
                    },
                )
        if i % 200 == 0:
            print(f"  {i}/{len(valid_rowids)}...")
            conn.commit()

    conn.commit()

else:
    print("No new jobs need embeddings.")


conn.close()

print("Done! All jobs now have embeddings.")

