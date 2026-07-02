from collections import Counter

import pandas as pd

from database.mongo import MongoManager
from database.postgres import PostgresManager


mongo = MongoManager()
postgres = PostgresManager()


def aggregate_sentiment():

    posts = mongo.get_posts()

    if not posts:

        return

    df = pd.DataFrame(posts)

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    df["hour_ts"] = (
        df["created_at"]
        .dt.floor("h")
    )

    grouped = df.groupby(
        ["hour_ts", "event_id"]
    )

    for (hour_ts, match_id), group in grouped:

        post_count = len(group)

        positive_count = (
            group["sentiment"]
            .apply(
                lambda x:
                x["label"] == "positive"
            )
            .sum()
        )

        neutral_count = (
            group["sentiment"]
            .apply(
                lambda x:
                x["label"] == "neutral"
            )
            .sum()
        )

        negative_count = (
            group["sentiment"]
            .apply(
                lambda x:
                x["label"] == "negative"
            )
            .sum()
        )

        avg_sentiment = (
            group["sentiment"]
            .apply(
                lambda x:
                x["score"]
            )
            .mean()
        )

        postgres.insert_sentiment_hourly(
            hour_ts,
            str(match_id),
            int(post_count),
            int(positive_count),
            int(neutral_count),
            int(negative_count),
            float(round(avg_sentiment, 3))
        )


def aggregate_topics():

    posts = mongo.get_posts()

    if not posts:

        return

    df = pd.DataFrame(posts)

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    df["hour_ts"] = (
        df["created_at"]
        .dt.floor("h")
    )

    for _, row in df.iterrows():

        topics = row.get("topics", [])

        counter = Counter(topics)

        for topic, occurrences in counter.items():

            postgres.insert_topic_hourly(

                row["hour_ts"],
                str(row["event_id"]),
                str(topic),
                int(occurrences)
            )


def run_aggregation():

    aggregate_sentiment()

    aggregate_topics()

    print("Aggregation completed.")