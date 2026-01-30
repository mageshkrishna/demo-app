from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="print_pwd",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    print_pwd = BashOperator(
        task_id="print_pwd",
        bash_command="pwd"
    )
