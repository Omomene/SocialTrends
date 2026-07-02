from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime

from kafka_pipeline.consumer import SocialConsumer
from kafka_pipeline.producer import SocialProducer
from kafka_pipeline.topics import TOPIC_RAW_POSTS
from kafka_pipeline.topics import TOPIC_CLEAN_POSTS


def clean_posts():

    consumer = SocialConsumer(TOPIC_RAW_POSTS)

    producer = SocialProducer()

    for post in consumer.read():

        text = str(post.get("text", "")).strip()

        if len(text) < 5:
            continue

        producer.send(
            TOPIC_CLEAN_POSTS,
            post
        )


with DAG(
    dag_id="social_cleaning_hourly",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False
) as dag:

    cleaning_task = PythonOperator(
        task_id="clean_posts",
        python_callable=clean_posts
    )