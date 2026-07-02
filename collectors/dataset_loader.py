import io
from datetime import datetime

import pandas as pd

from kafka_pipeline.producer import SocialProducer
from kafka_pipeline.topics import TOPIC_RAW_POSTS

from storage.minio_client import get_minio


def load_dataset():

    producer = SocialProducer()
    minio = get_minio()

    df = pd.read_csv(
        "/opt/airflow/data/fifa_world_cup_2022_tweets.csv"
    )

    # -----------------------------
    # Save raw dataset to Bronze
    # -----------------------------

    csv_buffer = io.BytesIO()

    df.to_csv(
        csv_buffer,
        index=False
    )

    csv_buffer.seek(0)

    filename = (
        f"tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    minio.put_object(
        Bucket="bronze",
        Key=filename,
        Body=csv_buffer,
        ContentLength=csv_buffer.getbuffer().nbytes,
        ContentType="text/csv"
    )

    print(f"Saved {filename} to Bronze")

    # -----------------------------
    # Publish rows to Kafka
    # -----------------------------

    for _, row in df.iterrows():

        producer.send(
            TOPIC_RAW_POSTS,
            row.to_dict()
        )

    print(f"{len(df)} tweets sent to Kafka")