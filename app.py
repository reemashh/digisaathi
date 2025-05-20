import streamlit as st
import requests

st.title("DigiSaathi Demo")

user_query = st.text_input("Ask your question:")

if st.button("Send"):
    if user_query.strip():
        try:
            response = requests.post("http://localhost:8000/query", json={"query": user_query})
            if response.status_code == 200:
                answer = response.json().get("response", "No response from API")
                st.write("**Answer:**", answer)
            else:
                st.error(f"API error: {response.status_code}")
        except Exception as e:
            st.error(f"Request failed: {e}")
    else:
        st.warning("Please enter a question.")
