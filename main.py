import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import faiss
import numpy as np

app = FastAPI()

# Allow CORS for your frontend domain (change this)
origins = [
    "https://digisaathi-frontend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # good small embedding model

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

# Sample documents
documents = [
    "DigiSaathi is a digital assistant project using LLMs.",
    "It supports knowledge retrieval from local documents.",
    "Users can query and get instructions or videos in response.",
    "The project demonstrates RAG, embedding, and vector search.",
]

def get_embedding_hf(text: str) -> np.ndarray:
    url = f"https://api-inference.huggingface.co/embeddings/{EMBEDDING_MODEL}"
    payload = {"inputs": text}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to get embedding: {response.text}")
    embedding = response.json()["embedding"]
    return np.array(embedding).astype('float32')

# Build FAISS index on startup
embedding_dim = 384  # dimension of all-MiniLM-L6-v2 embeddings
index = faiss.IndexFlatL2(embedding_dim)

embeddings = np.array([get_embedding_hf(doc) for doc in documents])
index.add(embeddings)

class Query(BaseModel):
    query: str

@app.post("/query")
async def query_endpoint(q: Query):
    try:
        q_emb = get_embedding_hf(q.query).reshape(1, -1)
        D, I = index.search(q_emb, k=2)
        matched_docs = [documents[i] for i in I[0]]
        response_text = "Top matches:\n" + "\n".join(matched_docs)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

