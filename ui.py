import os
import requests
import streamlit as st

# Load backend URL from environment variable or default to localhost
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("DigiSaathi - LLM Assistant")

# Input box for user query
user_query = st.text_input("Ask DigiSaathi:")

if st.button("Submit") and user_query:
    try:
        res = requests.post(f"{BACKEND_URL}/query", json={"query": user_query})
        response = res.json().get("response", "No response from backend.")
        st.write("### Response:")
        st.write(response)
    except Exception as e:
        st.error(f"Error contacting backend: {e}")

