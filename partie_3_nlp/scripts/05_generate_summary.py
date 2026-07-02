from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

ENRICHED_PATH = BASE_DIR / "outputs" / "enriched_posts.csv"
HOURLY_PATH = BASE_DIR / "outputs" / "hourly_sentiment_aggregates.csv"
TOPICS_PATH = BASE_DIR / "outputs" / "top_topics.csv"

SUMMARY_TXT_PATH = BASE_DIR / "outputs" / "trend_summary.txt"
SUMMARY_CSV_PATH = BASE_DIR / "outputs" / "trend_summary.csv"


def format_dict(data: dict) -> str:
    """
    Transforme un dictionnaire en texte lisible.
    """
    if not data:
        return "aucun élément significatif"

    return ", ".join([f"{key}: {value}" for key, value in data.items()])


def generate_summary(
    enriched_df: pd.DataFrame,
    hourly_df: pd.DataFrame,
    topics_df: pd.DataFrame
) -> tuple[str, str, str]:
    match_name = enriched_df["match_name"].iloc[0]
    match_id = enriched_df["match_id"].iloc[0]

    enriched_df["created_at"] = pd.to_datetime(enriched_df["created_at"], errors="coerce")

    start_date = enriched_df["created_at"].min()
    end_date = enriched_df["created_at"].max()

    total_posts = len(enriched_df)

    sentiment_counts = (
        enriched_df["sentiment_label"]
        .value_counts()
        .to_dict()
    )

    dominant_sentiment = (
        enriched_df["sentiment_label"]
        .value_counts()
        .idxmax()
    )

    top_topics = (
        topics_df.groupby("topic_label")["topic_post_count"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .to_dict()
    )

    negative_topics = (
        enriched_df[enriched_df["sentiment_label"] == "négatif"]["topic_label"]
        .value_counts()
        .head(3)
        .to_dict()
    )

    # Heure avec le plus grand volume de tweets
    hourly_volume = (
        hourly_df.groupby("event_hour")["total_posts"]
        .max()
        .sort_values(ascending=False)
    )

    if not hourly_volume.empty:
        peak_hour = hourly_volume.index[0]
        peak_volume = int(hourly_volume.iloc[0])
    else:
        peak_hour = "non disponible"
        peak_volume = 0

    # Heure avec sentiment le plus négatif
    hourly_sentiment = (
        hourly_df.groupby("event_hour")["sentiment_index"]
        .mean()
        .sort_values()
    )

    if not hourly_sentiment.empty:
        most_negative_hour = hourly_sentiment.index[0]
        most_negative_score = round(float(hourly_sentiment.iloc[0]), 3)
    else:
        most_negative_hour = "non disponible"
        most_negative_score = 0

    summary_text = f"""
Résumé automatique des tendances — {match_name}

Période analysée : du {start_date} au {end_date}.
Nombre de messages publics traités : {total_posts}.

Le sentiment dominant est : {dominant_sentiment}.
Répartition des sentiments : {format_dict(sentiment_counts)}.

Les sujets les plus visibles sont : {format_dict(top_topics)}.
Les sujets les plus associés aux réactions négatives sont : {format_dict(negative_topics)}.

Le pic d'activité le plus important est observé autour de {peak_hour}, avec environ {peak_volume} messages.
La période la moins positive est observée autour de {most_negative_hour}, avec un indice de sentiment de {most_negative_score}.
Interprétation :
L'analyse montre l'évolution de l'humeur des supporters autour de la Coupe du Monde 2022.
Les pics positifs peuvent être liés à l'enthousiasme autour des équipes, des joueurs ou de la compétition.
Les pics négatifs peuvent être liés à des polémiques, des critiques ou des sujets externes associés à l'événement.
Les topics détectés permettent d'identifier les thèmes qui génèrent le plus de réactions dans les tweets.

Ce résumé est destiné à être intégré dans le dashboard Superset comme encart d'aide à l'interprétation.
""".strip()

    return match_id, match_name, summary_text


if __name__ == "__main__":
    enriched_df = pd.read_csv(ENRICHED_PATH)
    hourly_df = pd.read_csv(HOURLY_PATH)
    topics_df = pd.read_csv(TOPICS_PATH)

    match_id, match_name, summary_text = generate_summary(
        enriched_df=enriched_df,
        hourly_df=hourly_df,
        topics_df=topics_df
    )

    SUMMARY_TXT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Fichier texte lisible
    with open(SUMMARY_TXT_PATH, "w", encoding="utf-8") as file:
        file.write(summary_text)

    # Fichier CSV pour le membre 4 / PostgreSQL / Superset
    summary_df = pd.DataFrame([
        {
            "match_id": match_id,
            "match_name": match_name,
            "summary_period": "all_available_period",
            "summary_text": summary_text,
            "generated_at": pd.Timestamp.now(),
            "summary_method": "template_from_nlp_aggregates"
        }
    ])

    summary_df.to_csv(SUMMARY_CSV_PATH, index=False, encoding="utf-8")

    print("Résumé généré avec succès.")
    print(f"Fichier TXT : {SUMMARY_TXT_PATH}")
    print(f"Fichier CSV : {SUMMARY_CSV_PATH}")
    print()
    print(summary_text)