import streamlit as st
import requests
import os

# Get backend URL from environment variable (default to localhost)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="DigiSaathi Assistant", page_icon="🤖")

st.title("DigiSaathi Assistant")
st.markdown(
    "Ask me anything about the project, its features, or how to use it!"
)

query = st.text_input("Your question:", placeholder="e.g. How does DigiSaathi retrieve information?")

if query:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={"query": query},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if "response" in result:
                st.success(result["response"])
            else:
                st.warning("No answer returned. Please try again.")

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")

st.markdown("---")
st.caption("Powered by Hugging Face + FAISS + Streamlit")

