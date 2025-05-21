import threading
import uvicorn
import streamlit as st
import requests
import os
import time

from main import app as fastapi_app

# Launch FastAPI in background
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="error")

threading.Thread(target=run_fastapi, daemon=True).start()
time.sleep(1)

# Streamlit UI
st.title("Streamlit + FastAPI + FAISS Demo")

query = st.text_input("Enter your question:")
if st.button("Search"):
    try:
        response = requests.post("http://localhost:8000/query", json={"query": query})
        if response.status_code == 200 and "results" in response.json():
            st.subheader("Top Matches:")
            for result in response.json()["results"]:
                st.markdown(f"- {result}")
        else:
            st.error("Error or no results.")
    except Exception as e:
        st.error(f"Backend error: {e}")

