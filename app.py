from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess

# ============================
# Task functions
# ============================

def run_s3():
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook

    hook = S3Hook(aws_conn_id="aws_conn")
    client = hook.get_conn()
    response = client.list_buckets()

    buckets = [b["Name"] for b in response["Buckets"]]
    print("S3 Buckets:", buckets)


def run_imap():
    from airflow.providers.imap.hooks.imap import ImapHook

    with ImapHook(imap_conn_id="imap_conn") as hook:
        hook.mail_client.select("INBOX")

        latest_id = list(hook._list_mail_ids_desc("ALL"))[0]
        raw = hook._fetch_mail_body(latest_id)

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="ignore")

        headers = [
            line for line in raw.splitlines()
            if line.startswith("Subject:") or line.startswith("Delivered-To:")
        ]

        for h in headers:
            print(h)


def run_smtp():
    from airflow.providers.smtp.hooks.smtp import SmtpHook

    hook = SmtpHook(smtp_conn_id="smtp_conn")
    hook.get_conn()

    hook.send_email_smtp(
        to="receiver@example.com",
        subject="SMTP Hook Test (Airflow DAG)",
        html_content="<b>Hello from Airflow DAG!</b>",
    )


def run_http():
    from airflow.providers.http.hooks.http import HttpHook

    hook = HttpHook(http_conn_id="http", method="GET")
    response = hook.run("/api/breeds/image/random")

    print("Status:", response.status_code)
    print("Response:", response.json())


def run_postgres():
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    hook = PostgresHook(postgres_conn_id="post")
    conn = hook.get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print("Postgres version:", version[0])


# ============================
# DAG definition
# ============================

with DAG(
    dag_id="run_all_airflow_hooks",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,   # manual trigger
    catchup=False,
    tags=["hooks", "demo"],
) as dag:

    s3_task = PythonOperator(
        task_id="s3_hook",
        python_callable=run_s3,
    )

    imap_task = PythonOperator(
        task_id="imap_hook",
        python_callable=run_imap,
    )

    smtp_task = PythonOperator(
        task_id="smtp_hook",
        python_callable=run_smtp,
    )

    http_task = PythonOperator(
        task_id="http_hook",
        python_callable=run_http,
    )

    postgres_task = PythonOperator(
        task_id="postgres_hook",
        python_callable=run_postgres,
    )

    # ============================
    # Execution order
    # ============================

    s3_task >> imap_task >> smtp_task >> http_task >> postgres_task
