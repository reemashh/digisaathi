import streamlit as st
import requests

BACKEND_URL = "https://digisaathi.onrender.com"  # Update if needed

st.title("DigiSaathi - LLM Assistant")

query = st.text_input("Ask your question:")

if query:
    try:
        res = requests.post(f"{BACKEND_URL}/query", json={"query": query})
        st.write("**Answer:**", res.json()["response"])
    except Exception as e:
        st.error(f"Error contacting backend: {e}")
