from pathlib import Path
import pandas as pd


try:
    from bertopic import BERTopic
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "outputs" / "posts_with_sentiment.csv"
OUTPUT_PATH = BASE_DIR / "outputs" / "enriched_posts.csv"

# Limite utilisée pour éviter de surcharger la machine locale
MAX_POSTS_FOR_BERTOPIC = 3000


def fallback_topic(text: str) -> tuple[int, str, str]:
    text = str(text).lower()

    if "qatar" in text or "worldcup2022" in text or "fifaworldcup" in text:
        return 1, "coupe du monde / qatar", "rule_based_fallback"

    if "england" in text or "france" in text or "italy" in text or "ecuador" in text:
        return 2, "équipes nationales", "rule_based_fallback"

    if "mbappe" in text or "pulisic" in text or "ronaldo" in text or "messi" in text:
        return 3, "joueurs", "rule_based_fallback"

    if "fan" in text or "fans" in text or "supporters" in text or "passion" in text:
        return 4, "supporters / ambiance", "rule_based_fallback"

    if "armband" in text or "fine" in text or "yellow card" in text:
        return 5, "polémique / règlement", "rule_based_fallback"

    if "climate" in text or "netzero" in text or "fossil" in text:
        return 6, "climat / politique", "rule_based_fallback"

    if "crypto" in text or "web3" in text or "ebay" in text:
        return 7, "promotion / publicité", "rule_based_fallback"

    if "goal" in text or "win" in text or "bring it home" in text:
        return 8, "victoire / performance", "rule_based_fallback"

    return 0, "autre", "rule_based_fallback"


def apply_fallback_topics(df: pd.DataFrame) -> pd.DataFrame:
    df[["topic_id", "topic_label", "topic_method"]] = df["text_clean"].apply(
        lambda text: pd.Series(fallback_topic(text))
    )
    return df


def apply_bertopic(df: pd.DataFrame) -> pd.DataFrame:
    if not BERTOPIC_AVAILABLE:
        print("BERTopic non installé. Fallback activé.")
        return apply_fallback_topics(df)

    if len(df) < 30:
        print("Volume trop faible pour BERTopic. Fallback activé.")
        return apply_fallback_topics(df)

    texts = df["text_clean"].fillna("").astype(str).tolist()

    try:
        print("Lancement de BERTopic...")
        print(f"Nombre de tweets utilisés : {len(texts)}")

        topic_model = BERTopic(
            language="english",
            min_topic_size=30,
            calculate_probabilities=False,
            verbose=True
        )

        topics, _ = topic_model.fit_transform(texts)

        df["topic_id"] = topics
        df["topic_method"] = "bertopic"

        def get_topic_label(topic_id):
            if topic_id == -1:
                return "autre"

            topic_words = topic_model.get_topic(topic_id)
            if not topic_words:
                return "autre"

            top_words = [word for word, _ in topic_words[:4]]
            return " / ".join(top_words)

        df["topic_label"] = df["topic_id"].apply(get_topic_label)

        return df

    except Exception as error:
        print("Erreur BERTopic. Fallback activé.")
        print(error)
        return apply_fallback_topics(df)


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)

    total_posts = len(df)

    # Limitation volontaire pour respecter la contrainte faible puissance
    df = df.head(MAX_POSTS_FOR_BERTOPIC).copy()

    print(f"Nombre total de tweets disponibles : {total_posts}")
    print(f"Nombre de tweets envoyés au topic modeling : {len(df)}")

    df = apply_bertopic(df)

    df["processed_at"] = pd.Timestamp.now()

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("Topic modeling terminé.")
    print(f"Fichier créé : {OUTPUT_PATH}")

    print(
        df[
            [
                "post_id",
                "text_clean",
                "sentiment_label",
                "topic_label",
                "topic_method"
            ]
        ].head(10)
    )