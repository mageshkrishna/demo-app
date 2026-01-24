import streamlit as st
import time
import random

# Page config
st.set_page_config(
    page_title="Dummy Streamlit App",
    page_icon="🚀",
    layout="centered"
)

# Title
st.title("🚀 Dummy Streamlit App")
st.caption("For testing deployments, Kubernetes, ingress, etc.")

# Sidebar
st.sidebar.header("Controls")
name = st.sidebar.text_input("Enter your name", "Magesh")
refresh = st.sidebar.button("Refresh Data")

# Main content
st.subheader("Hello 👋")
st.write(f"Welcome **{name}**!")

# Dummy metric
st.subheader("Live Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("CPU Usage", f"{rand
