from pathlib import Path
import os

# Éviter que BERTopic / sentence-transformers tente de charger TensorFlow/Keras.
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["USE_TF"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import pandas as pd


try:
    from bertopic import BERTopic
    BERTOPIC_AVAILABLE = True
except Exception as error:
    print("BERTopic indisponible dans cet environnement.")
    print("Fallback rule-based utilisé pour garder le pipeline fonctionnel.")
    print(f"Cause : {error}")
    BERTOPIC_AVAILABLE = False


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = BASE_DIR / "outputs" / "posts_with_sentiment.csv"
OUTPUT_PATH = BASE_DIR / "outputs" / "enriched_posts.csv"
TOPICS_PATH = BASE_DIR / "outputs" / "top_topics.csv"

# BERTopic peut être lourd en local.
# On l'applique sur un échantillon si disponible, mais on conserve tous les posts.
MAX_POSTS_FOR_BERTOPIC = 3000


def fallback_topic(text: str) -> tuple[int, str, str]:
    """
    Fallback simple par règles.
    Les règles spécifiques passent avant les règles générales.
    """

    text = str(text).lower()

    if "mbappe" in text or "pulisic" in text or "ronaldo" in text or "messi" in text:
        return 3, "joueurs", "rule_based_fallback"

    if "goal" in text or "goals" in text or "score" in text or "win" in text or "bring it home" in text:
        return 8, "victoire / performance", "rule_based_fallback"

    if "england" in text or "france" in text or "italy" in text or "ecuador" in text:
        return 2, "équipes nationales", "rule_based_fallback"

    if "fan" in text or "fans" in text or "supporters" in text or "passion" in text:
        return 4, "supporters / ambiance", "rule_based_fallback"

    if (
        "armband" in text
        or "fine" in text
        or "yellow card" in text
        or "red card" in text
        or "referee" in text
        or "var" in text
        or "offside" in text
    ):
        return 5, "polémique / arbitrage", "rule_based_fallback"

    if "climate" in text or "netzero" in text or "fossil" in text:
        return 6, "climat / politique", "rule_based_fallback"

    if "crypto" in text or "web3" in text or "ebay" in text:
        return 7, "promotion / publicité", "rule_based_fallback"

    if "qatar" in text or "worldcup2022" in text or "fifaworldcup" in text or "world cup" in text:
        return 1, "coupe du monde / qatar", "rule_based_fallback"

    return 0, "autre", "rule_based_fallback"


def apply_fallback_topics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique un topic simple à tous les posts.
    Cela permet de ne jamais perdre de lignes.
    """
    df[["topic_id", "topic_label", "topic_method"]] = df["text_clean"].apply(
        lambda text: pd.Series(fallback_topic(text))
    )
    return df


def apply_bertopic_on_sample(full_df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique d'abord un fallback sur tous les posts,
    puis BERTopic uniquement sur un échantillon si l'environnement le permet.
    La sortie conserve toutes les lignes.
    """

    full_df = apply_fallback_topics(full_df)

    if not BERTOPIC_AVAILABLE:
        print("BERTopic non disponible. Fallback utilisé sur tous les posts.")
        return full_df

    valid_df = full_df[
        full_df["text_clean"].notna()
        & (full_df["text_clean"].astype(str).str.strip() != "")
    ].copy()

    if len(valid_df) < 30:
        print("Volume trop faible pour BERTopic. Fallback utilisé sur tous les posts.")
        return full_df

    sample_size = min(MAX_POSTS_FOR_BERTOPIC, len(valid_df))
    sample_df = valid_df.head(sample_size).copy()

    texts = sample_df["text_clean"].fillna("").astype(str).tolist()

    try:
        print("Lancement de BERTopic sur un échantillon...")
        print(f"Nombre total de posts conservés en sortie : {len(full_df)}")
        print(f"Nombre de posts utilisés pour BERTopic : {len(sample_df)}")

        topic_model = BERTopic(
            language="english",
            min_topic_size=5,
            calculate_probabilities=False,
            verbose=True
        )

        topics, _ = topic_model.fit_transform(texts)

        sample_df["topic_id"] = topics
        sample_df["topic_method"] = "bertopic_sample"

        def get_topic_label(topic_id):
            if topic_id == -1:
                return "autre"

            topic_words = topic_model.get_topic(topic_id)
            if not topic_words:
                return "autre"

            top_words = [word for word, _ in topic_words[:4]]
            return " / ".join(top_words)

        sample_df["topic_label"] = sample_df["topic_id"].apply(get_topic_label)

        full_df.loc[sample_df.index, "topic_id"] = sample_df["topic_id"]
        full_df.loc[sample_df.index, "topic_label"] = sample_df["topic_label"]
        full_df.loc[sample_df.index, "topic_method"] = sample_df["topic_method"]

        return full_df

    except Exception as error:
        print("Erreur pendant BERTopic. Fallback conservé sur tous les posts.")
        print(error)
        return full_df


def generate_top_topics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Génère un fichier de synthèse des topics.
    Ce fichier reste une sortie NLP, pas une table Gold finale.
    """

    top_topics = (
        df.groupby(["topic_id", "topic_label", "topic_method"])
          .agg(
              topic_post_count=("post_id", "count"),
              avg_sentiment_score=("sentiment_score", "mean")
          )
          .reset_index()
          .sort_values("topic_post_count", ascending=False)
    )

    return top_topics


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)

    total_posts = len(df)
    print(f"Nombre total de posts reçus après sentiment : {total_posts}")

    df = apply_bertopic_on_sample(df)

    df["processed_at"] = pd.Timestamp.now()

    top_topics = generate_top_topics(df)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    top_topics.to_csv(TOPICS_PATH, index=False, encoding="utf-8")

    print("Topic modeling terminé.")
    print(f"Fichier posts enrichis créé : {OUTPUT_PATH}")
    print(f"Fichier topics créé : {TOPICS_PATH}")
    print(f"Nombre de posts conservés dans enriched_posts.csv : {len(df)}")
    print()
    print(
        df[
            [
                "post_id",
                "text_clean",
                "sentiment_label",
                "sentiment_method",
                "topic_label",
                "topic_method"
            ]
        ].head(10)
    )
    print()
    print("Top topics :")
    print(top_topics.head(10))