from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook


def test_mongo():
    hook = MongoHook(mongo_conn_id="mongo")
    client = hook.get_conn()

    db = client["grocery-store"]
    collection = db["admins"]

    docs = list(collection.find())
    print("Mongo Documents:", docs)


def test_snowflake():
    hook = SnowflakeHook(snowflake_conn_id="snowflake")

    conn = hook.get_conn()
    cur = conn.cursor()

    cur.execute("SELECT CURRENT_WAREHOUSE()")
    result = cur.fetchone()

    print("Snowflake warehouse:", result)


with DAG(
    dag_id="connection_test_dag",
    start_date=datetime(2024,1,1),
    schedule=None,
    catchup=False,
) as dag:

    mongo_test = PythonOperator(
        task_id="test_mongo_connection",
        python_callable=test_mongo
    )

    snowflake_test = PythonOperator(
        task_id="test_snowflake_connection",
        python_callable=test_snowflake
    )

    mongo_test >> snowflake_test
