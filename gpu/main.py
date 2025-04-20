import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastembed import TextEmbedding
from contextlib import asynccontextmanager

app = FastAPI()
embedding_model = None

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
MODEL_NAME = os.environ.get("FASTEMBED_MODEL", DEFAULT_MODEL)

class EmbeddingRequest(BaseModel):
    texts: list[str]

class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedding_model
    try:
        embedding_model = TextEmbedding(
            model_name=MODEL_NAME,
            providers=["CUDAExecutionProvider"],
            cache_dir="./model_cache"
        )
        print(f"FastEmbed model '{embedding_model.model_name}' loaded successfully (GPU enabled).")
        yield
    except Exception as e:
        print(f"Error loading FastEmbed model with CUDA: {e}")
        print(f"Falling back to CPU.")
        try:
            embedding_model = TextEmbedding(
                model_name=MODEL_NAME, 
                providers=["CPUExecutionProvider"],
                cache_dir="./model_cache"
            )
            print(f"FastEmbed model '{embedding_model.model_name}' loaded successfully (CPU).")
            yield
        except Exception as fallback_e:
            print(f"Error loading FastEmbed model on CPU: {fallback_e}")
            yield            
    finally:
        print("Application shutdown.")

app = FastAPI(lifespan=lifespan)

@app.post("/embeddings", response_model=EmbeddingResponse)
async def get_embeddings(request: EmbeddingRequest):
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model not loaded.")
    try:
        embeddings = embedding_model.embed(request.texts)
        return {"embeddings": list(embeddings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {e}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "model": embedding_model.model_name if embedding_model else None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)