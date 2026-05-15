from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime


def list_tables():
    hook = PostgresHook(postgres_conn_id="neon_postgres")

    conn = hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """)

    tables = cursor.fetchall()

    print("Tables in database:")

    for table in tables:
        print(table[0])

    cursor.close()
    conn.close()


def query_table():
    hook = PostgresHook(postgres_conn_id="neon_postgres")

    conn = hook.get_conn()
    cursor = conn.cursor()

    # Replace with your actual table
    cursor.execute("SELECT * FROM your_table_name LIMIT 10;")

    rows = cursor.fetchall()

    print("Table rows:")

    for row in rows:
        print(row)

    cursor.close()
    conn.close()


with DAG(
    dag_id="neon_postgres_connection_dag",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["neon", "postgres"],
) as dag:

    get_tables = PythonOperator(
        task_id="get_tables",
        python_callable=list_tables,
    )

    fetch_data = PythonOperator(
        task_id="fetch_data",
        python_callable=query_table,
    )

    get_tables >> fetch_data
