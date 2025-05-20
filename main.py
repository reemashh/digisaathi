import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import faiss
import numpy as np

# Initialize FastAPI
app = FastAPI()

# Initialize OpenAI client (v1+)
client = OpenAI(api_key="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")

# Sample documents — replace with actual chunks
documents = [
    "DigiSaathi is a digital assistant project using LLMs.",
    "It supports knowledge retrieval from local documents.",
    "Users can query and get instructions or videos in response.",
    "The project demonstrates RAG, embedding, and vector search.",
]

# Embed function using OpenAI v1+ style
def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

# Generate embeddings for documents
doc_embeddings = [get_embedding(doc) for doc in documents]
dimension = len(doc_embeddings[0])

# FAISS index setup
index = faiss.IndexFlatL2(dimension)
index.add(np.array(doc_embeddings).astype("float32"))

# Store doc text for reference
doc_lookup = {i: doc for i, doc in enumerate(documents)}

# Pydantic model for incoming request
class Query(BaseModel):
    query: str

@app.post("/query")
async def handle_query(data: Query):
    user_query = data.query
    query_embedding = np.array(get_embedding(user_query)).astype("float32").reshape(1, -1)

    # Search FAISS index
    D, I = index.search(query_embedding, k=3)
    retrieved = [doc_lookup[i] for i in I[0]]

    # Build prompt with retrieved context
    prompt = "You are DigiSaathi assistant.\n"
    prompt += "Context:\n" + "\n".join(retrieved) + "\n"
    prompt += f"User question: {user_query}\nAnswer:"

    # Call LLM
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.5,
    )
    answer = completion.choices[0].message.content
    return {"response": answer}

# Run locally if needed
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
