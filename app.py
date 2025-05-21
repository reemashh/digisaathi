import threading
import uvicorn
import streamlit as st
import requests
import os
import time

from main import app as fastapi_app

# Start FastAPI in background thread
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="error")

threading.Thread(target=run_fastapi, daemon=True).start()
time.sleep(1)  # Let FastAPI boot up

# Streamlit UI
st.title("Streamlit + FastAPI + FAISS")

query = st.text_input("Ask something:")
if st.button("Search"):
    try:
        res = requests.post("http://localhost:8000/query", json={"query": query})
        if res.status_code == 200 and "results" in res.json():
            st.write("Top results:")
            for r in res.json()["results"]:
                st.markdown(f"- {r}")
        else:
            st.error("No results or error returned.")
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")

