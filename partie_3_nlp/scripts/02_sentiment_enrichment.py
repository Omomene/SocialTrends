from pathlib import Path
import os

# Éviter TensorFlow/Keras et forcer PyTorch
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["USE_TF"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import re
import pandas as pd
import torch
from transformers import pipeline


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = BASE_DIR / "data" / "silver_posts.csv"
OUTPUT_PATH = BASE_DIR / "outputs" / "posts_with_sentiment.csv"

# Cache Hugging Face dans le projet pour éviter de saturer le cache Windows
HF_CACHE_DIR = BASE_DIR / "hf_cache"
os.environ["HF_HOME"] = str(HF_CACHE_DIR)
os.environ["TRANSFORMERS_CACHE"] = str(HF_CACHE_DIR)

# Modèle multilingue demandé / plus adapté aux réseaux sociaux
HF_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

# Pour tester rapidement. Mets 500 ou 3000 après validation.
MAX_POSTS = 3000

# Petit batch pour éviter les erreurs mémoire
BATCH_SIZE = 2


def create_match_id(match_name: str) -> str:
    text = str(match_name).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text


def classify_sentiment(hf_label: str) -> str:
    """
    Convertit les labels du modèle Cardiff en français.
    Le modèle peut renvoyer :
    - negative / neutral / positive
    - LABEL_0 / LABEL_1 / LABEL_2
    """
    hf_label = str(hf_label).lower()

    if hf_label in ["positive", "label_2"]:
        return "positif"

    if hf_label in ["negative", "label_0"]:
        return "négatif"

    return "neutre"


def analyze_texts(texts: list[str], analyzer) -> list[dict]:
    results = analyzer(
        texts,
        truncation=True,
        max_length=128,
        batch_size=BATCH_SIZE
    )

    output = []

    for result in results:
        output.append({
            "sentiment_label": classify_sentiment(result["label"]),
            "sentiment_score": float(result["score"]),
            "sentiment_method": "hugging_face_xlm_roberta"
        })

    return output


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)

    print(f"Nombre de posts reçus depuis Silver : {len(df)}")

    df = df[df["is_valid"].astype(str).str.lower() == "true"].copy()
    df = df[df["text_clean"].notna()].copy()
    df = df[df["text_clean"].astype(str).str.strip() != ""].copy()

    if MAX_POSTS is not None:
        df = df.head(MAX_POSTS).copy()

    print(f"Nombre de posts valides pour le sentiment : {len(df)}")

    df["match_id"] = df["match_name"].apply(create_match_id)
    df["lang"] = df["language_group"]

    print(f"Chargement du modèle multilingue : {HF_MODEL}")

    analyzer = pipeline(
        "sentiment-analysis",
        model=HF_MODEL,
        tokenizer=HF_MODEL,
        framework="pt",
        device=-1,
        model_kwargs={
            "cache_dir": str(HF_CACHE_DIR)
        }
    )

    print("Début de l'analyse de sentiment...")

    texts = df["text_clean"].astype(str).tolist()
    sentiment_results = analyze_texts(texts, analyzer)

    sentiment_df = pd.DataFrame(sentiment_results)

    df = pd.concat(
        [
            df.reset_index(drop=True),
            sentiment_df.reset_index(drop=True)
        ],
        axis=1
    )

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("Analyse de sentiment terminée avec le modèle multilingue Hugging Face.")
    print(f"Fichier créé : {OUTPUT_PATH}")
    print()
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