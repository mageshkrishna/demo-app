from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="print_opt_airflow_shared_tree",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    print_shared = BashOperator(
        task_id="print_shared_tree",
        bash_command="""
        echo "===== FULL TREE OF /opt/airflow/shared ====="
        find /opt/airflow/shared -print 2>/dev/null
        echo "===== END TREE ====="
        """
    )
