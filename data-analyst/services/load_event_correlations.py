import pandas as pd

from database.postgres import PostgresManager


postgres = PostgresManager()


def load_event_correlations(csv_path):

    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():

        postgres.insert_event_correlation(

            row["event_id"],

            row["match_id"],

            row["event_time"],

            row["event_type"],

            float(row["volume_delta"]),

            float(row["sentiment_delta"]),

            row["dominant_topic_after"],

            row["correlation_strength"],

            row["explanation"]
        )

    print("Event correlations loaded.")