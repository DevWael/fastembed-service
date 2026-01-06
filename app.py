from fastapi import FastAPI, HTTPException
from fastembed import TextEmbedding
from pydantic import BaseModel
from typing import List, Union
import uvicorn

app = FastAPI(title="Embedding Service", version="1.0.0")

# Initialize embedding model on startup
# Using the correct FastEmbed model name
embedding_model = TextEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str = "sentence-transformers/all-MiniLM-L6-v2"

class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[dict]
    model: str
    usage: dict

@app.get("/")
async def root():
    return {
        "message": "Embedding Service API",
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "max_tokens": 256,
        "dimensions": 384
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    try:
        # Convert single string to list
        texts = [request.input] if isinstance(request.input, str) else request.input
        
        # Generate embeddings
        embeddings = list(embedding_model.embed(texts))
        
        # Format response (OpenAI-compatible)
        data = [
            {
                "object": "embedding",
                "index": idx,
                "embedding": emb.tolist()
            }
            for idx, emb in enumerate(embeddings)
        ]
        
        # Calculate token usage (approximate)
        total_tokens = sum(len(t.split()) for t in texts)
        
        return EmbeddingResponse(
            data=data,
            model=request.model,
            usage={
                "prompt_tokens": total_tokens,
                "total_tokens": total_tokens
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
