from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

POSTS_PATH = BASE_DIR / "outputs" / "enriched_posts.csv"
EVENTS_PATH = BASE_DIR / "data" / "match_events_sample.csv"
OUTPUT_PATH = BASE_DIR / "outputs" / "event_correlation_report.csv"


def sentiment_to_numeric(label: str) -> int:
    mapping = {
        "positif": 1,
        "neutre": 0,
        "négatif": -1
    }
    return mapping.get(str(label).lower(), 0)


def detect_correlation_strength(volume_delta: float, sentiment_delta: float) -> str:
    """
    Simple business rule to qualify the strength of the event/social reaction.
    """

    abs_sentiment_delta = abs(sentiment_delta)

    if volume_delta >= 0.5 and abs_sentiment_delta >= 0.4:
        return "forte"

    if volume_delta >= 0.2 or abs_sentiment_delta >= 0.25:
        return "moyenne"

    return "faible"


def get_dominant_topic(posts_df: pd.DataFrame) -> str:
    if posts_df.empty:
        return "aucun"

    return posts_df["topic_label"].value_counts().idxmax()


def correlate_events(posts: pd.DataFrame, events: pd.DataFrame, window_minutes: int = 15) -> pd.DataFrame:
    results = []

    posts["created_at"] = pd.to_datetime(posts["created_at"])
    posts["sentiment_numeric"] = posts["sentiment_label"].apply(sentiment_to_numeric)

    events["event_time"] = pd.to_datetime(events["event_time"])

    for _, event in events.iterrows():
        event_time = event["event_time"]
        match_id = event["match_id"]

        before_start = event_time - pd.Timedelta(minutes=window_minutes)
        before_end = event_time

        after_start = event_time
        after_end = event_time + pd.Timedelta(minutes=window_minutes)

        posts_match = posts[posts["match_id"] == match_id]

        posts_before = posts_match[
            (posts_match["created_at"] >= before_start)
            & (posts_match["created_at"] < before_end)
        ]

        posts_after = posts_match[
            (posts_match["created_at"] >= after_start)
            & (posts_match["created_at"] < after_end)
        ]

        count_before = len(posts_before)
        count_after = len(posts_after)

        if count_before == 0:
            volume_delta = 1.0 if count_after > 0 else 0.0
        else:
            volume_delta = (count_after - count_before) / count_before

        sentiment_before = posts_before["sentiment_numeric"].mean() if count_before > 0 else 0
        sentiment_after = posts_after["sentiment_numeric"].mean() if count_after > 0 else 0
        sentiment_delta = sentiment_after - sentiment_before

        dominant_topic_before = get_dominant_topic(posts_before)
        dominant_topic_after = get_dominant_topic(posts_after)

        correlation_strength = detect_correlation_strength(
            volume_delta=volume_delta,
            sentiment_delta=sentiment_delta
        )

        explanation = (
            f"Après l'événement '{event['event_type']}' à la minute {event['event_minute']}, "
            f"le volume passe de {count_before} à {count_after} posts dans une fenêtre de {window_minutes} minutes. "
            f"L'indice de sentiment évolue de {round(sentiment_before, 2)} à {round(sentiment_after, 2)}. "
            f"Le sujet dominant après l'événement est '{dominant_topic_after}'."
        )

        results.append({
            "match_id": match_id,
            "event_id": event["event_id"],
            "event_time": event_time,
            "event_minute": event["event_minute"],
            "event_type": event["event_type"],
            "event_description": event["description"],
            "window_minutes": window_minutes,
            "posts_before": count_before,
            "posts_after": count_after,
            "volume_delta": round(volume_delta, 3),
            "sentiment_before": round(sentiment_before, 3),
            "sentiment_after": round(sentiment_after, 3),
            "sentiment_delta": round(sentiment_delta, 3),
            "dominant_topic_before": dominant_topic_before,
            "dominant_topic_after": dominant_topic_after,
            "correlation_strength": correlation_strength,
            "explanation": explanation
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    posts_df = pd.read_csv(POSTS_PATH)
    events_df = pd.read_csv(EVENTS_PATH)

    correlation_df = correlate_events(
        posts=posts_df,
        events=events_df,
        window_minutes=15
    )

    correlation_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("Event correlation report generated:")
    print(OUTPUT_PATH)
    print()
    print(correlation_df[
        [
            "event_minute",
            "event_type",
            "posts_before",
            "posts_after",
            "sentiment_delta",
            "dominant_topic_after",
            "correlation_strength"
        ]
    ])