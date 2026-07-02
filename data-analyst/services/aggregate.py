from collections import Counter

import pandas as pd

from database.mongo import MongoManager
from database.postgres import PostgresManager


mongo = MongoManager()
postgres = PostgresManager()


def sentiment_to_numeric(label):

    mapping = {
        "positif": 1,
        "neutre": 0,
        "négatif": -1
    }

    return mapping.get(str(label).lower(), 0)


def aggregate_sentiment():

    posts = mongo.get_posts()

    if not posts:
        print("No posts found in MongoDB.")
        return

    df = pd.DataFrame(posts)

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["created_at"]
    )

    df["hour_ts"] = (
        df["created_at"]
        .dt.floor("h")
    )

    grouped = df.groupby(
        ["hour_ts", "match_id"]
    )

    for (hour_ts, match_id), group in grouped:

        post_count = len(group)

        positive_count = (
            group["sentiment"]
            .apply(
                lambda x: x["label"] == "positif"
            )
            .sum()
        )

        neutral_count = (
            group["sentiment"]
            .apply(
                lambda x: x["label"] == "neutre"
            )
            .sum()
        )

        negative_count = (
            group["sentiment"]
            .apply(
                lambda x: x["label"] == "négatif"
            )
            .sum()
        )

        avg_sentiment = (
            group["sentiment"]
            .apply(
                lambda x: x["score"]
            )
            .mean()
        )

        group["sentiment_numeric"] = (
            group["sentiment"]
            .apply(
                lambda x: sentiment_to_numeric(
                    x["label"]
                )
            )
        )

        sentiment_index = (
            group["sentiment_numeric"]
            .mean()
        )

        dominant_sentiment = (
            group["sentiment"]
            .apply(
                lambda x: x["label"]
            )
            .value_counts()
            .idxmax()
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

        postgres.insert_sentiment_timeline(
            hour_ts,
            str(match_id),
            float(round(sentiment_index, 3)),
            dominant_sentiment,
            int(post_count)
        )

    print("Sentiment aggregation completed.")


def aggregate_topics():

    posts = mongo.get_posts()

    if not posts:
        print("No posts found in MongoDB.")
        return

    df = pd.DataFrame(posts)

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["created_at"]
    )

    df["hour_ts"] = (
        df["created_at"]
        .dt.floor("h")
    )

    grouped = df.groupby(
        ["hour_ts", "match_id"]
    )

    for (hour_ts, match_id), group in grouped:

        topic_counter = Counter()

        for _, row in group.iterrows():

            topic_data = row.get("topic")

            if not topic_data:
                continue

            topic_label = topic_data.get("label")

            if not topic_label:
                continue

            topic_counter[topic_label] += 1

        for topic, count in topic_counter.items():

            postgres.insert_topic_hourly(
                hour_ts,
                str(match_id),
                str(topic),
                int(count)
            )

    print("Topic aggregation completed.")


def run_aggregation():

    print("Starting sentiment aggregation...")

    aggregate_sentiment()

    print("Starting topic aggregation...")

    aggregate_topics()

    print("Aggregation completed successfully.")