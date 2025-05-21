import streamlit as st
import requests

# Your backend API URL on Render
BACKEND_URL = "https://digisaathi-backend.onrender.com"

st.title("DigiSaathi - LLM Assistant")

query = st.text_input("Enter your question:")

if st.button("Ask"):
    if not query:
        st.warning("Please enter a question.")
    else:
        try:
            res = requests.post(f"{BACKEND_URL}/query", json={"query": query})
            if res.status_code == 200:
                answer = res.json().get("response")
                st.write(answer)
            else:
                st.error(f"Error from backend: {res.status_code}")
        except Exception as e:
            st.error(f"Failed to contact backend: {e}")

