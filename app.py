import threading
import uvicorn
import streamlit as st
import requests
import os
import time

from main import app as fastapi_app

# --- Start FastAPI backend in background thread ---
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="error")

threading.Thread(target=run_fastapi, daemon=True).start()
time.sleep(1)  # Let FastAPI initialize

# --- Streamlit UI ---
st.set_page_config(page_title="DigiSaathi Assistant", layout="centered")
st.title("🤖 DigiSaathi – Your Digital Banking Assistant")

st.markdown("""
Welcome to **DigiSaathi** — a smart assistant for digital banking help.
Type your question below to retrieve relevant instructions or guidance.
""")

query = st.text_input("💬 Ask DigiSaathi:")

if st.button("🔍 Search DigiSaathi"):
    if query.strip() == "":
        st.warning("Please enter a valid query to continue.")
    else:
        with st.spinner("DigiSaathi is thinking..."):
            try:
                response = requests.post("http://localhost:8000/query", json={"query": query})
                if response.status_code == 200 and "results" in response.json():
                    st.subheader("📚 Relevant Results:")
                    for result in response.json()["results"]:
                        st.markdown(f"- {result}")
                else:
                    st.error("DigiSaathi couldn't find a match.")
            except Exception as e:
                st.error(f"❌ Internal error: {e}")

