import streamlit as st
import requests

st.title("DigiSaathi - LLM Assistant")
query = st.text_input("Ask a question")

if query:
    res = requests.post("http://localhost:8000/query", json={"query": query})
    if res.ok:
        st.success(res.json()["response"])
    else:
        st.error("Failed to get response from backend")
