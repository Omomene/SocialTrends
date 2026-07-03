from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta
import re

from kafka_pipeline.consumer import SocialConsumer
from kafka_pipeline.topics import TOPIC_RAW_POSTS
from storage.minio_storage import save_json


# =========================
# CLEAN FUNCTION
# =========================
def clean_text(text: str) -> str:

    text = str(text).strip().lower()

    # remove urls
    text = re.sub(r"http\S+|www\S+|https\S+", " ", text)

    # remove mentions
    text = re.sub(r"@\w+", " ", text)

    # remove hashtag symbol (keep word)
    text = re.sub(r"#", "", text)

    # remove special chars
    text = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# =========================
# DAG TASK
# =========================
def clean_posts():

    consumer = SocialConsumer(TOPIC_RAW_POSTS)

    cleaned_posts = []
    processed = 0
    skipped = 0

    for post in consumer.read():

        text_raw = post.get("Tweet", "")

        text_clean = clean_text(text_raw)

        if len(text_clean) < 5:
            skipped += 1
            continue

        cleaned_posts.append({
            "post_id": post.get("Unnamed: 0"),
            "created_at": post.get("Date Created"),
            "source": post.get("Source of Tweet"),
            "number_of_likes": post.get("Number of Likes"),  # KEEP THIS
            "text_raw": text_raw,
            "text_clean": text_clean
        })

        processed += 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ✅ CORRECT CALL (NO key= !!!)
    save_json(
        bucket="silver",
        prefix="clean_posts",
        data=cleaned_posts
    )

    print("Processed:", processed)
    print("Skipped:", skipped)
    print("Saved:", len(cleaned_posts))


# =========================
# DAG
# =========================
with DAG(
    dag_id="social_cleaning_hourly",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False,
    dagrun_timeout=timedelta(minutes=10)
) as dag:

    cleaning_task = PythonOperator(
        task_id="clean_posts",
        python_callable=clean_posts
    )