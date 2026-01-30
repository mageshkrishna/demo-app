from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="verify_dbt_project_file",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    verify = BashOperator(
        task_id="verify",
        bash_command="""
        echo "=== LIST /opt/airflow/dags ==="
        ls -la /opt/airflow/dags
        echo
        echo "=== FILE TYPE ==="
        file /opt/airflow/dags/dbt_project.yml || echo "file not found"
        echo
        echo "=== FILE CONTENT ==="
        cat /opt/airflow/dags/dbt_project.yml || echo "cannot read file"
        """
    )
