from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime

from collectors.dataset_loader import load_dataset


with DAG(
    dag_id="social_posts_collect_hourly",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False
) as dag:

    collect_task = PythonOperator(
        task_id="load_csv_to_kafka",
        python_callable=load_dataset
    )