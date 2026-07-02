import pandas as pd

from kafka_pipeline.producer import SocialProducer
from kafka_pipeline.topics import TOPIC_RAW_POSTS


def load_dataset():

    producer = SocialProducer()

    df = pd.read_csv(
        "/opt/airflow/data/fifa_world_cup_2022_tweets.csv"
    )

    for _, row in df.iterrows():

        producer.send(
            TOPIC_RAW_POSTS,
            row.to_dict()
        )

    print(f"{len(df)} tweets sent to Kafka")