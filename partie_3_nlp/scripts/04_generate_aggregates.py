from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = BASE_DIR / "outputs" / "enriched_posts.csv"

HOURLY_OUTPUT_PATH = BASE_DIR / "outputs" / "hourly_sentiment_aggregates.csv"
TOPICS_OUTPUT_PATH = BASE_DIR / "outputs" / "top_topics.csv"


def sentiment_to_numeric(label):

    mapping = {
        "positif": 1,
        "neutre": 0,
        "négatif": -1
    }

    return mapping.get(str(label).lower(), 0)


if __name__ == "__main__":

    df = pd.read_csv(INPUT_PATH)

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df = df.dropna(subset=["created_at"])

    df["event_hour"] = (
        df["created_at"]
        .dt.floor("h")
    )

    df["sentiment_numeric"] = (
        df["sentiment_label"]
        .apply(sentiment_to_numeric)
    )

    hourly = (
        df.groupby(
            ["match_id", "match_name", "event_hour"]
        )
        .agg(
            total_posts=("post_id", "count"),
            sentiment_index=("sentiment_numeric", "mean")
        )
        .reset_index()
    )

    topics = (
        df.groupby(
            ["match_id",
             "match_name",
             "event_hour",
             "topic_label"]
        )
        .agg(
            topic_post_count=("post_id", "count")
        )
        .reset_index()
    )

    hourly.to_csv(
        HOURLY_OUTPUT_PATH,
        index=False
    )

    topics.to_csv(
        TOPICS_OUTPUT_PATH,
        index=False
    )

    print("Summary helper files generated.")