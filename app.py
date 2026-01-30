from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="dbt_debug_runtime_project",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command="""
        mkdir -p /tmp/dbt_project
        cat << 'EOF' > /tmp/dbt_project/dbt_project.yml
        name: "dbt_mini"
        version: "1.0"
        profile: "dbt_mini"
        model-paths: []
        EOF

        dbt debug --project-dir /tmp/dbt_project
        """
)
