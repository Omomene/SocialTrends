from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime

import pandas as pd
from pymongo import MongoClient
import psycopg2


# =====================================================
# CONFIG
# =====================================================

MONGO_URI = "mongodb://app:app12345@mongo:27017"

POSTGRES_CONFIG = {
    "host": "postgres",
    "database": "socialtrends",
    "user": "app",
    "password": "app12345"
}


# =====================================================
# MONGO
# =====================================================

def get_mongo():

    client = MongoClient(MONGO_URI)

    return client["socialtrends"]


# =====================================================
# POSTGRES
# =====================================================

def get_postgres():

    return psycopg2.connect(**POSTGRES_CONFIG)


# =====================================================
# LOAD EVENTS CSV
# =====================================================

def load_events():

    return pd.read_csv(
        "/opt/airflow/data/match_events.csv"
    )


# =====================================================
# SIMPLE MATCHING ENGINE
# =====================================================

def match_event(text, events_df):

    if not text:
        return None

    text = text.lower()

    for _, row in events_df.iterrows():

        player = str(row["player"]).lower() if pd.notna(row["player"]) else ""
        team = str(row["team"]).lower() if pd.notna(row["team"]) else ""
        event_type = str(row["event_type"]).lower()

        # Highest priority -> player

        if player and player in text:
            return row

        # Goal detection

        if "goal" in text and "goal" in event_type:
            return row

        # Team detection

        if team and team in text:
            return row

    return None


# =====================================================
# MAIN PIPELINE
# =====================================================

def run_gold_pipeline():

    mongo = get_mongo()

    posts = list(
        mongo.nlp_posts.find()
    )

    events = load_events()

    print(f"Mongo posts : {len(posts)}")
    print(f"Match events : {len(events)}")

    conn = get_postgres()

    cur = conn.cursor()

    # Prevent duplicates

    cur.execute("TRUNCATE TABLE social_gold;")

    inserted = 0
    matched = 0

    for post in posts:

        text = post.get("text_clean", "")

        event = match_event(text, events)

        if event is not None:
            matched += 1

        cur.execute(
            """
            INSERT INTO social_gold
            (
                post_id,
                created_at,
                text_clean,
                language,
                sentiment_label,
                sentiment_score,
                topic,
                likes,
                source,
                match_name,
                team,
                player,
                event_type,
                processed_at
            )
            VALUES
            (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            )
            """,
            (
                post.get("post_id"),
                post.get("created_at"),
                text,
                post.get("language", "unknown"),
                post.get("sentiment_label"),
                post.get("sentiment_score"),
                post.get("topic", "unknown"),
                post.get("number_of_likes", 0),
                post.get("source"),

                event["match"] if event is not None else None,
                event["team"] if event is not None else None,
                event["player"] if event is not None else None,
                event["event_type"] if event is not None else None,

                datetime.utcnow()
            )
        )

        inserted += 1

    conn.commit()

    cur.close()
    conn.close()

    print("----------------------------------")
    print(f"Inserted rows : {inserted}")
    print(f"Matched events: {matched}")
    print("----------------------------------")


# =====================================================
# DAG
# =====================================================

with DAG(
    dag_id="social_gold_aggregation_hourly",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["gold", "postgres"]
) as dag:

    gold_task = PythonOperator(
        task_id="build_gold_table",
        python_callable=run_gold_pipeline
    )