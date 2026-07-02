from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = BASE_DIR / "outputs" / "enriched_posts.csv"

HOURLY_OUTPUT_PATH = BASE_DIR / "outputs" / "hourly_sentiment_aggregates.csv"
TOPICS_OUTPUT_PATH = BASE_DIR / "outputs" / "top_topics.csv"


def sentiment_to_numeric(label: str) -> int:
    """
    Convertit le sentiment en score numérique.
    positif = 1, neutre = 0, négatif = -1
    """
    mapping = {
        "positif": 1,
        "neutre": 0,
        "négatif": -1
    }
    return mapping.get(str(label).lower(), 0)


def get_dominant_sentiment(group: pd.DataFrame) -> str:
    """
    Retourne le sentiment le plus fréquent dans une période.
    """
    if group.empty:
        return "neutre"

    return group["sentiment_label"].value_counts().idxmax()


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH)

    # Conversion des dates
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    if df["created_at"].isna().any():
        raise ValueError("Certaines valeurs created_at ne sont pas convertibles en datetime.")

    # Agrégation par heure
    df["event_hour"] = df["created_at"].dt.floor("h")

    # Score numérique de sentiment
    df["sentiment_numeric"] = df["sentiment_label"].apply(sentiment_to_numeric)

    # Agrégats par match, heure et sentiment
    hourly_by_sentiment = (
        df.groupby(["match_id", "match_name", "event_hour", "sentiment_label"])
        .agg(
            post_count=("post_id", "count"),
            avg_sentiment_score=("sentiment_score", "mean")
        )
        .reset_index()
    )

    # Agrégats globaux par heure
    hourly_global = (
        df.groupby(["match_id", "match_name", "event_hour"])
        .agg(
            total_posts=("post_id", "count"),
            sentiment_index=("sentiment_numeric", "mean")
        )
        .reset_index()
    )

    # Sentiment dominant par heure
    dominant_sentiment = (
        df.groupby(["match_id", "match_name", "event_hour"])
        .apply(get_dominant_sentiment)
        .reset_index(name="dominant_sentiment")
    )

    hourly_global = hourly_global.merge(
        dominant_sentiment,
        on=["match_id", "match_name", "event_hour"],
        how="left"
    )

    # Fusion : détail par sentiment + indicateurs globaux
    hourly_aggregates = hourly_by_sentiment.merge(
        hourly_global,
        on=["match_id", "match_name", "event_hour"],
        how="left"
    )

    # Top topics par heure
    top_topics = (
        df.groupby(["match_id", "match_name", "event_hour", "topic_label"])
        .agg(
            topic_post_count=("post_id", "count"),
            avg_topic_sentiment=("sentiment_numeric", "mean")
        )
        .reset_index()
        .sort_values(
            ["match_id", "event_hour", "topic_post_count"],
            ascending=[True, True, False]
        )
    )

    HOURLY_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    hourly_aggregates.to_csv(HOURLY_OUTPUT_PATH, index=False, encoding="utf-8")
    top_topics.to_csv(TOPICS_OUTPUT_PATH, index=False, encoding="utf-8")

    print("Agrégats générés avec succès.")
    print(f"Fichier sentiment horaire : {HOURLY_OUTPUT_PATH}")
    print(f"Fichier top topics : {TOPICS_OUTPUT_PATH}")
    print()
    print("Aperçu des agrégats horaires :")
    print(hourly_aggregates.head(10))
    print()
    print("Aperçu des top topics :")
    print(top_topics.head(10))