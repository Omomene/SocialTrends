from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime

from kafka_pipeline.consumer import SocialConsumer
from kafka_pipeline.producer import SocialProducer

from kafka_pipeline.topics import (
    TOPIC_RAW_POSTS,
    TOPIC_CLEAN_POSTS
)

from storage.minio_storage import save_json


def clean_posts():

    consumer = SocialConsumer(TOPIC_RAW_POSTS)
    producer = SocialProducer()

    cleaned_posts = []

    processed = 0
    skipped = 0

    for post in consumer.read():

        text = str(post.get("text", "")).strip()

        if len(text) < 5:
            skipped += 1
            continue

        producer.send(
            TOPIC_CLEAN_POSTS,
            post
        )

        cleaned_posts.append(post)

        processed += 1


    save_json(
        bucket="silver",
        prefix="clean_posts",
        data=cleaned_posts
    )

    print(f"Processed : {processed}")
    print(f"Skipped   : {skipped}")


with DAG(
    dag_id="social_cleaning_hourly",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False,
) as dag:

    cleaning_task = PythonOperator(
        task_id="clean_posts",
        python_callable=clean_posts,
    )