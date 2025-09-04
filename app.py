import streamlit as st
from sqlalchemy import text
from dataflow.dataflow import Dataflow

# --- Initialize Dataflow SDK ---
dataflow = Dataflow()
db = dataflow.connection("conn_id")  # Replace with your real connection ID

st.title("📊 Dummy Postgres Table Creator")

if st.button("Create Table"):
    try:
        # Example: Create a dummy table
        create_sql = text("""
        CREATE TABLE IF NOT EXISTS dummy_users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INT
        );
        """)
        db.execute(create_sql)

        # Insert sample data
        insert_sql = text("""
        INSERT INTO dummy_users (name, age)
        VALUES ('Alice', 25), ('Bob', 30), ('Charlie', 22)
        ON CONFLICT DO NOTHING;
        """)
        db.execute(insert_sql)

        st.success("✅ Table created and sample data inserted!")

    except Exception as e:
        st.error(f"❌ Error: {e}")

if st.button("Show Data"):
    try:
        result = db.execute(text("SELECT * FROM dummy_users;"))
        rows = result.fetchall()
        st.write(rows)
    except Exception as e:
        st.error(f"❌ Error: {e}")
