from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import numpy as np
import faiss
import requests
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# ✅ Correct model URL for semantic search
API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}

texts = [
    "DigiSaathi is a digital assistant for banking queries.",
    "It supports knowledge retrieval and guided workflows.",
    "Users can query and get instructions on digital services.",
    "The project demonstrates RAG, FastAPI, and Streamlit integration."
]

def get_embedding(text: str):
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": [text]})  # Pass input as a list
    if response.status_code != 200:
        raise Exception(f"Embedding failed: {response.status_code} - {response.text}")
    return np.array(response.json()[0], dtype=np.float32)

# Build FAISS index
embeddings = [get_embedding(text) for text in texts]
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_endpoint(request: QueryRequest):
    try:
        query_vector = get_embedding(request.query)
        D, I = index.search(np.array([query_vector]), k=3)
        results = [texts[i] for i in I[0]]
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}
