import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastembed import TextEmbedding
from contextlib import asynccontextmanager

app = FastAPI()
embedding_model = None

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
MODEL_NAME = os.environ.get("FASTEMBED_MODEL", DEFAULT_MODEL)
MAX_LENGTH = int(os.environ.get("FASTEMBED_MAX_LENGTH", "512"))
CACHE_DIR = os.environ.get("FASTEMBED_CACHE_DIR")
THREADS = os.environ.get("FASTEMBED_THREADS")
doc_embed_type = os.environ.get("FASTEMBED_DOC_EMBED_TYPE", "default")
DOC_EMBED_TYPE=  doc_embed_type if doc_embed_type in ["default", "passage"] else "default"
BATCH_SIZE = int(os.environ.get("FASTEMBED_BATCH_SIZE", "256"))
PARALLEL = os.environ.get("FASTEMBED_PARALLEL")

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
            max_length=MAX_LENGTH,
            cache_dir=CACHE_DIR if CACHE_DIR else "./model_cache",
            threads=int(THREADS) if THREADS else None,
            doc_embed_type=DOC_EMBED_TYPE,
            batch_size=BATCH_SIZE,
            parallel=int(PARALLEL) if PARALLEL else None,
            providers=["CUDAExecutionProvider"]
        )
        print(f"FastEmbed model '{embedding_model.model_name}' loaded successfully (GPU enabled).")
        yield
    except Exception as e:
        print(f"Error loading FastEmbed model with CUDA: {e}")
        print(f"Falling back to CPU.")
        try:
            embedding_model = TextEmbedding(
                model_name=MODEL_NAME,
                max_length=MAX_LENGTH,
                cache_dir=CACHE_DIR if CACHE_DIR else "./model_cache",
                threads=int(THREADS) if THREADS else None,
                doc_embed_type=DOC_EMBED_TYPE,
                batch_size=BATCH_SIZE,
                parallel=int(PARALLEL) if PARALLEL else None,
                providers=["CPUExecutionProvider"],
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
