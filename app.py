import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Environment Variables Viewer",
    layout="wide"
)

st.title("🔐 Environment Variables Viewer")

# --- Options ---
mask_sensitive = st.checkbox("Mask sensitive values (recommended)", value=True)
search = st.text_input("🔍 Search (key or value)", placeholder="PATH, HOME, TOKEN...")

# --- Load environment variables ---
env_data = []
for key, value in os.environ.items():
    display_value = value
    if mask_sensitive and any(s in key.lower() for s in ["key", "token", "secret", "password"]):
        display_value = "********"
    env_data.append({
        "Key": key,
        "Value": display_value
    })

df = pd.DataFrame(env_data)

# --- Search filter ---
if search:
    search_lower = search.lower()
    df = df[
        df["Key"].str.lower().str.contains(search_lower)
        | df["Value"].str.lower().str.contains(search_lower)
    ]

# --- Display ---
st.write(f"Showing **{len(df)}** environment variables")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
