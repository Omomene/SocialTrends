from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime
import boto3
import json

from pymongo import MongoClient
from langdetect import detect, LangDetectException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# =====================================================
# CONFIG
# =====================================================

MINIO_ENDPOINT = "http://minio:9000"
ACCESS_KEY = "minio"
SECRET_KEY = "minio12345"

MONGO_URI = "mongodb://app:app12345@mongo:27017"

analyzer = SentimentIntensityAnalyzer()

# =====================================================
# MINIO CLIENT
# =====================================================

def get_s3():

    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )


# =====================================================
# LANGUAGE DETECTION
# =====================================================

def detect_language(text):

    try:

        lang = detect(str(text))

        if lang in ["en", "fr", "es", "pt"]:
            return lang

        return "other"

    except LangDetectException:
        return "other"

    except Exception:
        return "other"


# =====================================================
# SENTIMENT (VADER)
# =====================================================

def get_sentiment(text):

    score = analyzer.polarity_scores(str(text))["compound"]

    if score >= 0.05:
        return "positive", score

    elif score <= -0.05:
        return "negative", score

    return "neutral", score


# =====================================================
# MAIN TASK
# =====================================================

def run_nlp():

    s3 = get_s3()

    response = s3.list_objects_v2(
        Bucket="silver"
    )

    files = response.get("Contents", [])

    json_files = [
        f for f in files
        if f["Key"].endswith(".json")
    ]

    if not json_files:

        print("No Silver JSON files found.")

        return

    latest = sorted(
        json_files,
        key=lambda x: x["LastModified"]
    )[-1]

    key = latest["Key"]

    print("Reading:", key)

    obj = s3.get_object(
        Bucket="silver",
        Key=key
    )

    posts = json.loads(
        obj["Body"].read().decode("utf-8")
    )

    results = []

    for row in posts:

        text = row.get("text_clean", "")

        language = detect_language(text)

        sentiment_label, sentiment_score = get_sentiment(text)

        results.append({

            "post_id": row.get("post_id"),

            "created_at": row.get("created_at"),

            "source": row.get("source"),

            "number_of_likes": row.get(
                "number_of_likes",
                0
            ),

            "text_clean": text,

            "language": language,

            # Placeholder until topic modelling is added
            "topic": "unknown",

            "sentiment_label": sentiment_label,

            "sentiment_score": sentiment_score,

            "processed_at": datetime.utcnow()

        })

    client = MongoClient(MONGO_URI)

    db = client["socialtrends"]

    collection = db["nlp_posts"]

    # Keep only latest batch
    collection.delete_many({})

    if results:

        collection.insert_many(results)

    print(f"Inserted {len(results)} documents into MongoDB.")


# =====================================================
# DAG
# =====================================================

with DAG(

    dag_id="social_nlp_hourly",

    start_date=datetime(2024, 1, 1),

    schedule="@hourly",

    catchup=False,

    tags=["nlp", "mongodb"]

) as dag:

    nlp_task = PythonOperator(

        task_id="run_nlp",

        python_callable=run_nlp

    )