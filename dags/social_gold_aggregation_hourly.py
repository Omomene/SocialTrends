from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime

from storage.mongo_client import get_mongo
from storage.postgres_client import get_postgres


def aggregate_sentiment():

    mongo = get_mongo()

    posts = mongo.social_posts.find()

    conn = get_postgres()

    cursor = conn.cursor()

    positive = 0
    neutral = 0
    negative = 0

    total = 0

    for post in posts:

        sentiment = post.get("sentiment")

        total += 1

        if sentiment == "positive":
            positive += 1

        elif sentiment == "negative":
            negative += 1

        else:
            neutral += 1

    cursor.execute(
        """
        INSERT INTO sentiment_hourly
        (
            hour_bucket,
            match_name,
            positive_count,
            neutral_count,
            negative_count,
            total_posts
        )
        VALUES
        (
            NOW(),
            'World Cup',
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            positive,
            neutral,
            negative,
            total
        )
    )

    conn.commit()

    cursor.close()

    conn.close()


with DAG(
    dag_id="social_gold_aggregation_hourly",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False
) as dag:

    aggregation_task = PythonOperator(
        task_id="aggregate_sentiment",
        python_callable=aggregate_sentiment
    )