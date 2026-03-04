import streamlit as st
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

st.title("Airflow Connection Tester")

tab1, tab2 = st.tabs(["MongoDB Test", "Snowflake Test"])


# ---------------- Mongo Test ----------------
with tab1:

    st.header("MongoDB Connection")

    if st.button("Run Mongo Test"):

        try:
            hook = MongoHook(mongo_conn_id="mongo")
            client = hook.get_conn()

            db = client["grocery-store"]
            collection = db["admins"]

            docs = list(collection.find().limit(10))

            st.success("Mongo Connection Successful")
            st.write(docs)

        except Exception as e:
            st.error(f"Mongo Connection Failed: {e}")


# ---------------- Snowflake Test ----------------
with tab2:

    st.header("Snowflake Connection")

    if st.button("Run Snowflake Test"):

        try:
            hook = SnowflakeHook(snowflake_conn_id="snowflake")

            conn = hook.get_conn()
            cur = conn.cursor()

            cur.execute("SELECT CURRENT_WAREHOUSE()")
            result = cur.fetchone()

            st.success("Snowflake Connection Successful")
            st.write({"Current Warehouse": result[0]})

        except Exception as e:
            st.error(f"Snowflake Connection Failed: {e}")
