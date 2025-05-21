import os
import streamlit as st
import requests

# Get backend URL from environment variable with fallback to localhost
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="DigiSaathi - LLM Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("DigiSaathi - LLM Assistant 🤖")

# Add some basic description
st.markdown("""
DigiSaathi is an AI assistant that can answer your questions about digital technologies.
Ask a question below to get started!
""")

# Initialize session state for displaying loading indicator
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Create the query input
query = st.text_input("Enter your question:", key="query_input")

# Function to query the backend
def query_backend(question):
    try:
        # Show spinner during API call
        with st.spinner("DigiSaathi is thinking..."):
            response = requests.post(
                f"{BACKEND_URL}/query", 
                json={"query": question},
                headers={"Content-Type": "application/json"},
                timeout=30  # Set a reasonable timeout
            )
            
            if response.status_code == 200:
                return response.json().get("response"), None
            else:
                return None, f"Error from backend (status {response.status_code}): {response.text}"
    except requests.exceptions.Timeout:
        return None, "The request timed out. The server might be busy or experiencing issues."
    except requests.exceptions.ConnectionError:
        return None, f"Could not connect to the backend at {BACKEND_URL}. Please check if the server is running."
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"

# Add a "Clear" button next to the query input
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("Clear"):
        st.session_state.query_input = ""
        st.experimental_rerun()

# Handle the query submission
if st.button("Ask DigiSaathi"):
    if not query:
        st.warning("Please enter a question.")
    else:
        st.session_state.processing = True
        answer, error = query_backend(query)
        st.session_state.processing = False
        
        if error:
            st.error(error)
        else:
            # Display the response in a nice format
            st.subheader("Answer:")
            st.markdown(answer)

# Add a health check indicator in the sidebar
st.sidebar.title("System Status")
try:
    health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if health_response.status_code == 200:
        st.sidebar.success("Backend system is online ✅")
    else:
        st.sidebar.warning("Backend system may have issues ⚠️")
except:
    st.sidebar.error("Backend system is offline ❌")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 DigiSaathi Project")
