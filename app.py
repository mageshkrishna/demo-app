from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="print_root_tree_structured",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    print_root = BashOperator(
        task_id="print_root_tree",
        bash_command="""
        for dir in / /opt /opt/airflow /home /dataflow /tmp; do
          echo "===== TREE OF $dir ====="
          find $dir -maxdepth 3 -print 2>/dev/null
          echo
        done
        """
    )
