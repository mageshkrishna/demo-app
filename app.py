import os
import streamlit as st

# --- MUST be set BEFORE importing airflow ---
os.environ.setdefault(
    "AIRFLOW__SECRETS__BACKEND",
    "airflow_utils.import_variable_connection.AirflowConnectionsAndVariableImport"
)

from airflow.providers.http.hooks.http import HttpHook


st.title("Dog API via Airflow HttpHook 🐶")

if st.button("Fetch Random Dog Image"):
    try:
        hook = HttpHook(http_conn_id="http", method="GET")
        response = hook.run("/api/breeds/image/random")

        if response.status_code == 200:
            data = response.json()
            st.success("API call successful!")
            st.image(data["message"], caption="Random Dog 🐕")
        else:
            st.error(f"Failed with status {response.status_code}")
            st.text(response.text)

    except Exception as e:
        st.error("Error calling API")
        st.exception(e)
