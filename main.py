from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    query: str

@app.post("/query")
async def handle_query(data: Query):
    user_query = data.query
    # Dummy response - replace with your actual logic
    return {"response": f"You asked: {user_query}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

