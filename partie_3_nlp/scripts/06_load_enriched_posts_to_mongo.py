from pathlib import Path
import pandas as pd
from pymongo import MongoClient


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = BASE_DIR / "outputs" / "enriched_posts.csv"

MONGO_URI = "mongodb://app:app12345@localhost:27017/"
DATABASE_NAME = "socialtrends"
COLLECTION_NAME = "enriched_posts"


def build_document(row: pd.Series) -> dict:
    return {
        "post_id": row.get("post_id"),
        "source": row.get("source"),
        "created_at": str(row.get("created_at")),
        "match": {
            "match_id": row.get("match_id"),
            "match_name": row.get("match_name")
        },
        "text": {
            "raw": row.get("text_raw"),
            "clean": row.get("text_clean")
        },
        "language": {
            "detected": row.get("language"),
            "group": row.get("language_group")
        },
        "nlp": {
            "sentiment": {
                "label": row.get("sentiment_label"),
                "score": float(row.get("sentiment_score")) if pd.notna(row.get("sentiment_score")) else None,
                "method": row.get("sentiment_method")
            },
            "topic": {
                "id": int(row.get("topic_id")) if pd.notna(row.get("topic_id")) else None,
                "label": row.get("topic_label"),
                "method": row.get("topic_method")
            },
            "processed_at": str(row.get("processed_at"))
        },
        "ingestion_timestamp": str(row.get("ingestion_timestamp"))
    }


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH)

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    documents = [
        build_document(row)
        for _, row in df.iterrows()
    ]

    # Nettoyage avant rechargement pour éviter les doublons pendant les tests
    collection.delete_many({})

    if documents:
        collection.insert_many(documents)

    # Index utile pour les recherches
    collection.create_index("post_id", unique=True)
    collection.create_index("match.match_id")
    collection.create_index("created_at")
    collection.create_index("nlp.sentiment.label")
    collection.create_index("nlp.topic.label")

    print("Chargement MongoDB terminé.")
    print(f"Base : {DATABASE_NAME}")
    print(f"Collection : {COLLECTION_NAME}")
    print(f"Documents insérés : {collection.count_documents({})}")