import streamlit as st
import requests
import os

st.title("DigiSaathi - LLM Assistant")
query = st.text_input("Ask a question")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if query:
    res = requests.post(f"{BACKEND_URL}/query", json={"query": user_query})
    if res.ok:
        st.success(res.json()["response"])
    else:
        st.error("Failed to get response from backend")
