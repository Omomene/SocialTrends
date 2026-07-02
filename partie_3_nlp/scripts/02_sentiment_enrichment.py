from pathlib import Path
import pandas as pd
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "data" / "silver_posts.csv"
OUTPUT_PATH = BASE_DIR / "outputs" / "posts_with_sentiment.csv"


def create_match_id(match_name: str) -> str:
    text = str(match_name).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text


def classify_sentiment(compound_score: float) -> str:
    if compound_score >= 0.05:
        return "positif"

    if compound_score <= -0.05:
        return "négatif"

    return "neutre"


def detect_sentiment(text: str, analyzer: SentimentIntensityAnalyzer) -> tuple[str, float, str]:
    scores = analyzer.polarity_scores(str(text))

    compound_score = float(scores["compound"])
    sentiment_label = classify_sentiment(compound_score)

    sentiment_score = abs(compound_score)

    return sentiment_label, sentiment_score, "vader"


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)

    df = df[df["is_valid"].astype(str).str.lower() == "true"].copy()

    df["match_id"] = df["match_name"].apply(create_match_id)
    df["lang"] = df["language_group"]

    analyzer = SentimentIntensityAnalyzer()

    df[["sentiment_label", "sentiment_score", "sentiment_method"]] = df["text_clean"].apply(
        lambda text: pd.Series(detect_sentiment(text, analyzer))
    )

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("Analyse de sentiment terminée avec VADER.")
    print(f"Fichier créé : {OUTPUT_PATH}")
    print(
        df[
            [
                "post_id",
                "match_name",
                "text_clean",
                "sentiment_label",
                "sentiment_score",
                "sentiment_method"
            ]
        ].head(10)
    )