from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime

import pandas as pd

from storage.postgres_client import get_postgres


def load_events():

    df = pd.read_csv(
        "/opt/airflow/data/match_events.csv"
    )

    conn = get_postgres()

    cursor = conn.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO football_events
            (
                event_time,
                match_name,
                event_type,
                team,
                player
            )
            VALUES (%s,%s,%s,%s,%s)
            """,
            (
                row["event_time"],
                row["match"],
                row["event_type"],
                row["team"],
                row["player"]
            )
        )

    conn.commit()

    cursor.close()

    conn.close()


with DAG(
    dag_id="social_events_ingestion_hourly",
    start_date=datetime(2024,1,1),
    schedule="@hourly",
    catchup=False
) as dag:

    load_task = PythonOperator(
        task_id="load_match_events",
        python_callable=load_events
    )