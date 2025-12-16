from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowException
import logging


def query_http_and_postgres():
    log = logging.getLogger("airflow.task")

    # -----------------------
    # HTTP call
    # -----------------------
    try:
        log.info("Starting HTTP request...")
        http_hook = HttpHook(http_conn_id="http", method="GET")
        response = http_hook.run("/api/breeds/image/random")

        log.info("HTTP status: %s", response.status_code)

        if response.status_code != 200:
            log.error("HTTP request failed: %s", response.text)
            raise AirflowException("HTTP request failed")

        log.info("HTTP response: %s", response.text)

    except Exception as e:
        log.exception("HTTP call failed")
        raise

    # -----------------------
    # Postgres query
    # -----------------------
    try:
        log.info("Connecting to Postgres...")
        pg_hook = PostgresHook(postgres_conn_id="post")
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        log.info("Postgres version: %s", version)

    except Exception as e:
        log.exception("Postgres query failed")
        raise

    finally:
        try:
            cursor.close()
            conn.close()
            log.info("Postgres connection closed")
        except Exception:
            pass


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
