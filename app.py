import os
import streamlit as st

# Secrets backend
os.environ["AIRFLOW__SECRETS__BACKEND"] = (
    "airflow_utils.import_variable_connection.AirflowConnectionsAndVariableImport"
)


# --------------------------------------------------
# Now it is SAFE to import Airflow hooks
# --------------------------------------------------
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook


st.title("Airflow Hooks in Streamlit 🚀")

# -----------------------
# HTTP example
# -----------------------
if st.button("Fetch Random Dog Image"):
    try:
        hook = HttpHook(http_conn_id="http", method="GET")
        response = hook.run("/api/breeds/image/random")

        if response.status_code == 200:
            data = response.json()
            st.image(data["message"], caption="Random Dog 🐶")
        else:
            st.error(response.text)
    except Exception as e:
        st.exception(e)

st.divider()

# -----------------------
# Postgres example
# -----------------------
if st.button("Check Postgres Version"):
    try:
        pg_hook = PostgresHook(postgres_conn_id="post")
        conn = pg_hook.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]

        st.success("Connected to Postgres ✅")
        st.code(version)

        cur.close()
        conn.close()
    except Exception as e:
        st.exception(e)
