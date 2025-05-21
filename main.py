import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import faiss
import numpy as np
import time

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API token from environment variable
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    print("WARNING: HF_API_TOKEN environment variable not set. API calls may fail.")

# The correct model path for embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # dimension of all-MiniLM-L6-v2 embeddings

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# Sample documents
documents = [
    "DigiSaathi is a digital assistant project using LLMs.",
    "It supports knowledge retrieval from local documents.",
    "Users can query and get instructions or videos in response.",
    "The project demonstrates RAG, embedding, and vector search.",
]

def get_embedding_hf(text: str, max_retries=3) -> np.ndarray:
    """Get embeddings from Hugging Face API with retry logic"""
    # Fixed URL format for Hugging Face API
    url = f"https://api-inference.huggingface.co/models/{EMBEDDING_MODEL}"
    
    payload = {"inputs": text, "options": {"wait_for_model": True}}
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                # Return the embedding and handle different response formats
                embedding = np.array(response.json()).astype('float32')
                # If we get a list of lists for a single input, take the first one
                if len(embedding.shape) > 1 and embedding.shape[0] == 1:
                    embedding = embedding[0]
                return embedding
            
            # If model is loading, wait and retry
            if response.status_code == 503 and "loading" in response.text.lower():
                wait_time = min(2 ** attempt, 10)  # Exponential backoff
                print(f"Model loading, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            # Otherwise, raise an exception with details
            error_msg = f"API Error (Status {response.status_code}): {response.text}"
            print(error_msg)
            raise Exception(error_msg)
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = min(2 ** attempt, 10)
                print(f"Request failed, retrying in {wait_time}s... Error: {str(e)}")
                time.sleep(wait_time)
            else:
                raise Exception(f"Failed to get embedding after {max_retries} attempts: {str(e)}")
    
    raise Exception("Failed to get embedding: Max retries exceeded")

# Function to build FAISS index
def build_index():
    print("Building FAISS index...")
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    
    # Try to get embeddings with better error handling
    try:
        embeddings = []
        
        # Check if we have a valid API token
        if not HF_API_TOKEN:
            print("WARNING: HF_API_TOKEN not set. Using dummy embeddings for demonstration.")
            # Use random embeddings as fallback for demo purposes
            for doc in documents:
                dummy_embedding = np.random.rand(EMBEDDING_DIM).astype('float32')
                dummy_embedding = dummy_embedding / np.linalg.norm(dummy_embedding)
                embeddings.append(dummy_embedding)
                print(f"Created dummy embedding for: {doc[:30]}...")
        else:
            # Try to get real embeddings
            for doc in documents:
                try:
                    embedding = get_embedding_hf(doc)
                    embeddings.append(embedding)
                    print(f"Got embedding for document: {doc[:30]}...")
                except Exception as e:
                    print(f"Failed to get embedding for document: {doc[:30]}... Error: {str(e)}")
                    # Use a normalized random vector as fallback (better than zeros)
                    fallback = np.random.rand(EMBEDDING_DIM).astype('float32')
                    fallback = fallback / np.linalg.norm(fallback)
                    embeddings.append(fallback)
        
        if embeddings:
            embeddings_array = np.array(embeddings)
            index.add(embeddings_array)
            print(f"Added {len(embeddings)} embeddings to the index")
            return index
        else:
            raise Exception("No embeddings could be created")
    except Exception as e:
        print(f"Error building index: {str(e)}")
        # Return an empty index as fallback
        return faiss.IndexFlatL2(EMBEDDING_DIM)

# Initialize index at startup
index = build_index()

class Query(BaseModel):
    query: str

@app.post("/query")
async def query_endpoint(q: Query):
    try:
        # Get query embedding
        query_embedding = get_embedding_hf(q.query)
        
        # Handle different response shapes from the API
        if len(query_embedding.shape) > 1:
            # If we get a 2D array (like [batch_size, embedding_dim])
            q_emb = query_embedding.reshape(-1)
        else:
            # If we already have a 1D array
            q_emb = query_embedding
            
        # Ensure proper shape for FAISS search
        q_emb = q_emb.reshape(1, -1)
        
        # Search for similar documents
        k = min(2, len(documents))  # Don't try to retrieve more docs than we have
        D, I = index.search(q_emb, k=k)
        
        # Format response
        matched_docs = [documents[i] for i in I[0] if i < len(documents)]
        
        if not matched_docs:
            return {"response": "I couldn't find any relevant information for your query."}
        
        response_text = "Top matches:\n" + "\n".join(matched_docs)
        return {"response": response_text}
    
    except Exception as e:
        print(f"Error in query endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Simple endpoint to check if the API is running"""
    return {"status": "healthy"}
