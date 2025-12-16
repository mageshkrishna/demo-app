from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

def query_postgres():
    hook = PostgresHook(postgres_conn_id="post")
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print("Postgres version:", version)

with DAG(
    dag_id="print_message_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    print_task = PythonOperator(
        task_id="print_hello_task",
        python_callable=query_postgres,
    )
