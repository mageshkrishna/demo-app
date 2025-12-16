from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook


def query_http_and_postgres():
    # -----------------------
    # HTTP call
    # -----------------------
    http_hook = HttpHook(http_conn_id="http", method="GET")
    response = http_hook.run("/api/breeds/image/random")

    print("HTTP status:", response.status_code)
    print("HTTP response:", response.text)

    # -----------------------
    # Postgres query
    # -----------------------
    pg_hook = PostgresHook(postgres_conn_id="post")
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print("Postgres version:", version)

    cursor.close()
    conn.close()


with DAG(
    dag_id="http_and_postgres_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["http", "postgres"],
) as dag:

    run_task = PythonOperator(
        task_id="call_http_and_query_postgres",
        python_callable=query_http_and_postgres,
    )
