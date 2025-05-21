import os
import time
import requests
import numpy as np
import faiss
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

print(">>> Running updated main.py using Hugging Face feature-extraction API <<<")

app = FastAPI()

# Enable CORS (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

if not HF_API_TOKEN:
    print("⚠️  WARNING: HF_API_TOKEN environment variable not set. Embedding calls may fail.")

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{EMBEDDING_MODEL}"

# Example knowledge base
documents = [
    "DigiSaathi is a digital assistant project using LLMs.",
    "It supports knowledge retrieval from local documents.",
    "Users can query and get instructions or videos in response.",
    "The project demonstrates RAG, embedding, and vector search.",
]

def get_embedding_hf(text: str, max_retries: int = 3) -> np.ndarray:
    """Fetch embedding from Hugging Face feature-extraction API with retry logic"""
    payload = {"inputs": text}
    
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                embedding = np.array(response.json()).astype("float32")
                if len(embedding.shape) > 1 and embedding.shape[0] == 1:
                    embedding = embedding[0]  # Unwrap if necessary
                return embedding

            if response.status_code == 503 and "loading" in response.text.lower():
                wait_time = min(2 ** attempt, 10)
                print(f"Model loading, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            error_msg = f"API Error (Status {response.status_code}): {response.text}"
            print(error_msg)
            raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            wait_time = min(2 ** attempt, 10)
            print(f"Request failed, retrying in {wait_time}s... Error: {str(e)}")
            time.sleep(wait_time)
    raise Exception("Failed to get embedding after max retries.")

# Build FAISS index from documents
def build_index():
    print("🔧 Building FAISS index...")
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    embeddings = []

    if not HF_API_TOKEN:
        print("⚠️  Using dummy vectors — HF_API_TOKEN not set.")
        for doc in documents:
            dummy = np.random.rand(EMBEDDING_DIM).astype("float32")
            dummy /= np.linalg.norm(dummy)
            embeddings.append(dummy)
    else:
        for doc in documents:
            try:
                emb = get_embedding_hf(doc)
                emb = emb / np.linalg.norm(emb)
                embeddings.append(emb)
                print(f"✅ Embedded: {doc[:30]}...")
            except Exception as e:
                print(f"❌ Failed to embed: {doc[:30]}... Error: {str(e)}")
                fallback = np.random.rand(EMBEDDING_DIM).astype("float32")
                fallback /= np.linalg.norm(fallback)
                embeddings.append(fallback)

    index.add(np.array(embeddings))
    print(f"📦 Index built with {len(embeddings)} vectors.")
    return index

# Initialize index once at startup
index = build_index()

# Pydantic model
class Query(BaseModel):
    query: str

@app.post("/query")
async def query_endpoint(q: Query):
    try:
        q_embedding = get_embedding_hf(q.query)
        q_embedding = q_embedding.reshape(1, -1)

        k = min(2, len(documents))  # Top-k results
        D, I = index.search(q_embedding, k=k)

        matched = [documents[i] for i in I[0] if i < len(documents)]

        if not matched:
            return {"response": "I couldn't find any relevant information for your query."}

        return {"response": "Top matches:\n" + "\n".join(matched)}

    except Exception as e:
        print(f"❌ Error in query endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

