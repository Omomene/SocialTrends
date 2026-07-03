import pandas as pd

from database.postgres import PostgresManager

postgres = PostgresManager()

def load_summary(csv_path):

    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():

        postgres.insert_trend_summary(
            row["match_id"],
            row["match_name"],
            row["summary_text"],
            row["generated_at"]
        )

    print("Trend summary loaded.")