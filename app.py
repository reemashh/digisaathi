import os
import threading
import uvicorn
import streamlit as st
import requests
import time

from main import app as fastapi_app

# Start FastAPI in background
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="error")

threading.Thread(target=run_fastapi, daemon=True).start()

# Wait a moment to let FastAPI boot
time.sleep(1)

# Read port from environment (Render uses $PORT)
streamlit_port = int(os.environ.get("PORT", 8501))

# Streamlit interface
st.title("Streamlit + FastAPI (Render)")

query = st.text_input("Enter your query:")
if st.button("Send to FastAPI"):
    try:
        res = requests.post("http://localhost:8000/query", json={"query": query})
        st.write("Response:", res.json())
    except Exception as e:
        st.error(f"Error: {e}")

