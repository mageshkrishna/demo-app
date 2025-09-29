from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def print_hello():
    print("Hello from the DAG!")

with DAG(
    dag_id="print_message_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    print_task = PythonOperator(
        task_id="print_hello_task",
        python_callable=print_hello,
    )

    print_task
