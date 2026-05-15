import streamlit as st
import pandas as pd

from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook


st.set_page_config(page_title="Neon PostgreSQL Viewer")

st.title("Neon PostgreSQL Tables")

CONN_ID = "test_streamlit"


def get_postgres_hook():
    """
    Load Airflow connection
    """
    hook = PostgresHook(postgres_conn_id=CONN_ID)
    return hook


def get_tables():
    hook = get_postgres_hook()

    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
    ORDER BY table_name;
    """

    df = hook.get_pandas_df(query)

    return df


def get_table_data(table_name):
    hook = get_postgres_hook()

    query = f"""
    SELECT *
    FROM {table_name}
    LIMIT 100;
    """

    df = hook.get_pandas_df(query)

    return df


try:
    tables_df = get_tables()

    if tables_df.empty:
        st.warning("No tables found")
    else:
        table_names = tables_df["table_name"].tolist()

        selected_table = st.selectbox(
            "Select Table",
            table_names
        )

        st.subheader(f"Preview: {selected_table}")

        data_df = get_table_data(selected_table)

        st.dataframe(data_df)

except Exception as e:
    st.error(str(e))
