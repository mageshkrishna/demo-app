from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="find_dbt_project_yml_opt_airflow",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    find_file = BashOperator(
        task_id="find_dbt_project_yml",
        bash_command="""
        echo "===== SEARCHING FOR dbt_project.yml INSIDE /opt/airflow ====="
        find /opt/airflow/ -type f -name "dbt_project.yml" 2>/dev/null || echo "NOT FOUND"
        echo "===== SEARCH COMPLETE ====="
        """
    )
