import os
import threading
import uvicorn
import subprocess
import time

# Import the FastAPI app from main.py
from main import app

# Function to run FastAPI in a thread
def run_api():
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# Function to run Streamlit in a separate process
def run_streamlit():
    # Wait a moment to let the API start up
    time.sleep(2)
    
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8501))
    
    # Set BACKEND_URL environment variable for the Streamlit app
    my_env = os.environ.copy()
    my_env["BACKEND_URL"] = f"http://localhost:{os.environ.get('API_PORT', 8000)}"
    
    # Run Streamlit as a subprocess
    subprocess.run([
        "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0"
    ], env=my_env)

if __name__ == "__main__":
    # Start the FastAPI server in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Start Streamlit in the main thread
    run_streamlit()
