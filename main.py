import os
from fastapi import FastAPI
from pydantic import BaseModel
import openai
import faiss
import pickle
import numpy as np

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Sample documents
documents = [
    "DigiSaathi is a digital assistant project using LLMs.",
    "It supports knowledge retrieval from local documents.",
    "Users can query and get instructions or videos in response.",
    "The project demonstrates RAG, embedding, and vector search."
]

# Create embeddings
EMBED_MODEL = "text-embedding-ada-002"


def get_embedding(text):
    result = openai.Embedding.create(input=text, model=EMBED_MODEL)
    return np.array(result['data'][0]['embedding'], dtype='float32')


# Build FAISS index
embeddings = [get_embedding(doc) for doc in documents]
index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(np.array(embeddings))


class Query(BaseModel):
    query: str


@app.post("/query")
async def handle_query(data: Query):
    query_emb = get_embedding(data.query)
    D, I = index.search(np.array([query_emb]), k=3)
    context = "\n".join([documents[i] for i in I[0]])

    prompt = f"""You are DigiSaathi, a helpful assistant. Use the context below to answer the question.
Context:
{context}

Question: {data.query}
Answer:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=200
    )
    return {"response": response['choices'][0]['message']['content']}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
