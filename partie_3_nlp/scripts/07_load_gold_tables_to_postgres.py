from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text


BASE_DIR = Path(__file__).resolve().parents[1]

HOURLY_PATH = BASE_DIR / "outputs" / "hourly_sentiment_aggregates.csv"
TOPICS_PATH = BASE_DIR / "outputs" / "top_topics.csv"
SUMMARY_PATH = BASE_DIR / "outputs" / "trend_summary.csv"

POSTGRES_URI = "postgresql+psycopg2://app:app12345@localhost:5432/gold"


def load_csv_to_postgres(csv_path: Path, table_name: str, engine) -> None:
    df = pd.read_csv(csv_path)

    # Conversion automatique des colonnes dates si présentes
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower() or "hour" in col.lower() or "generated_at" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="ignore")

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False
    )

    print(f"Table chargée : {table_name} — {len(df)} lignes")


if __name__ == "__main__":
    engine = create_engine(POSTGRES_URI)

    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS public"))

    load_csv_to_postgres(
        csv_path=HOURLY_PATH,
        table_name="gold_hourly_sentiment",
        engine=engine
    )

    load_csv_to_postgres(
        csv_path=TOPICS_PATH,
        table_name="gold_top_topics",
        engine=engine
    )

    load_csv_to_postgres(
        csv_path=SUMMARY_PATH,
        table_name="gold_trend_summary",
        engine=engine
    )

    print("Chargement PostgreSQL terminé.")