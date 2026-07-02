from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime

from kafka_pipeline.consumer import SocialConsumer
from kafka_pipeline.topics import TOPIC_CLEAN_POSTS

from nlp.language_detection import detect_language
from plugins.operators.sentiment_operator import run_sentiment
from plugins.operators.topic_operator import run_topic

from storage.mongo_client import get_mongo


def process_nlp():

    db = get_mongo()

    collection = db.social_posts

    consumer = SocialConsumer(
        TOPIC_CLEAN_POSTS
    )

    for post in consumer.read():

        post["language"] = detect_language(
            post.get("text", "")
        )

        post = run_sentiment(post)

        post = run_topic(post)

        collection.insert_one(post)


with DAG(
    dag_id="social_nlp_hourly",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False
) as dag:

    nlp_task = PythonOperator(
        task_id="run_nlp",
        python_callable=process_nlp
    )