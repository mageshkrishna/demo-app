import streamlit as st

st.set_page_config(page_title="Airflow Hooks Demo", layout="wide")

st.title("🪁 Airflow Hooks Demo (Streamlit)")
st.write("Run all Airflow hooks using a single button")

# ============================
# ONE BUTTON
# ============================

if st.button("🚀 Run All Airflow Hooks"):

    # ============================
    # S3 Hook
    # ============================
    st.subheader("📦 S3 Buckets")

    try:
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

        hook = S3Hook(aws_conn_id="aws_conn")
        client = hook.get_conn()
        response = client.list_buckets()

        buckets = [b["Name"] for b in response["Buckets"]]
        st.success("Buckets retrieved")
        st.write(buckets)

    except Exception as e:
        st.error(f"S3 failed: {e}")

    # ============================
    # IMAP Hook
    # ============================
    st.subheader("📧 Latest Email")

    try:
        from airflow.providers.imap.hooks.imap import ImapHook

        with ImapHook(imap_conn_id="imap_conn") as hook:
            hook.mail_client.select("INBOX")

            latest_id = list(hook._list_mail_ids_desc("ALL"))[0]
            raw = hook._fetch_mail_body(latest_id)

            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="ignore")

            lines = [
                line for line in raw.splitlines()
                if line.startswith("Subject:") or line.startswith("Delivered-To:")
            ]

            for line in lines:
                st.text(line)

    except Exception as e:
        st.error(f"IMAP failed: {e}")

    # ============================
    # SMTP Hook
    # ============================
    st.subheader("📨 SMTP Email")

    try:
        from airflow.providers.smtp.hooks.smtp import SmtpHook

        hook = SmtpHook(smtp_conn_id="smtp_conn")
        hook.get_conn()

        hook.send_email_smtp(
            to="receiver@example.com",
            subject="SMTP Hook Test (Streamlit)",
            html_content="<b>Hello from Streamlit + Airflow!</b>",
        )

        st.success("Email sent ✔️")

    except Exception as e:
        st.error(f"SMTP failed: {e}")

    # ============================
    # HTTP Hook
    # ============================
    st.subheader("🌐 HTTP API")

    try:
        from airflow.providers.http.hooks.http import HttpHook

        hook = HttpHook(http_conn_id="http", method="GET")
        response = hook.run("/api/breeds/image/random")

        st.write("Status Code:", response.status_code)
        st.json(response.json())

    except Exception as e:
        st.error(f"HTTP failed: {e}")

    # ============================
    # Postgres Hook
    # ============================
    st.subheader("🐘 Postgres Version")

    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook(postgres_conn_id="post")
        conn = hook.get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        st.write(version[0])

    except Exception as e:
        st.error(f"Postgres failed: {e}")
