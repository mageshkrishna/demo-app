from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="dbt_debug_two_tasks",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    create_dbt_project = BashOperator(
        task_id="create_dbt_project",
        bash_command="""
        echo "=== Creating dbt project ==="
        mkdir -p /tmp/dbt_project

        cat > /tmp/dbt_project/dbt_project.yml <<EOF
name: "dbt_mini"
version: "1.0"
profile: "dbt_mini"
model-paths: []
analysis-paths: []
seed-paths: []
macro-paths: []
snapshot-paths: []
target-path: "target"
clean-targets: ["target"]
EOF

        echo "=== dbt_project.yml content ==="
        cat /tmp/dbt_project/dbt_project.yml

        echo "=== Files in /tmp/dbt_project ==="
        ls -la /tmp/dbt_project
        """
    )

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command="""
        echo "=== Running dbt debug ==="
        dbt debug --project-dir /tmp/dbt_project
        echo "=== dbt debug finished ==="
        """
    )

    create_dbt_project >> dbt_debug
