from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PROJECT_DIR = "/opt/airflow/shared/dbt_project"

with DAG(
    dag_id="dbt_debug_two_tasks_shared",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    create_dbt_project = BashOperator(
        task_id="create_dbt_project",
        bash_command=f"""
        echo "=== Creating dbt project in shared dir ==="
        mkdir -p {PROJECT_DIR}

        cat > {PROJECT_DIR}/dbt_project.yml <<EOF
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

        echo "=== Files in {PROJECT_DIR} ==="
        ls -la {PROJECT_DIR}
        """
    )

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command=f"""
        echo "=== Running dbt debug from shared dir ==="
        ls -la {PROJECT_DIR}
        dbt debug --project-dir {PROJECT_DIR}
        """
    )

    create_dbt_project >> dbt_debug

