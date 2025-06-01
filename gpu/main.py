import os
import json
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastembed import TextEmbedding
from contextlib import asynccontextmanager
from prometheus_metrics import PrometheusMiddleware, metrics_app, logger

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
MODEL_NAME = os.environ.get("FASTEMBED_MODEL", DEFAULT_MODEL)
MAX_LENGTH = int(os.environ.get("FASTEMBED_MAX_LENGTH", "512"))
CACHE_DIR = os.environ.get("FASTEMBED_CACHE_DIR")
THREADS = os.environ.get("FASTEMBED_THREADS")
doc_embed_type = os.environ.get("FASTEMBED_DOC_EMBED_TYPE", "default")
DOC_EMBED_TYPE=  doc_embed_type if doc_embed_type in ["default", "passage"] else "default"
BATCH_SIZE = int(os.environ.get("FASTEMBED_BATCH_SIZE", "256"))
PARALLEL = os.environ.get("FASTEMBED_PARALLEL")

embedding_model = None

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
            cache_dir=CACHE_DIR,
            threads=int(THREADS) if THREADS else None,
            doc_embed_type=DOC_EMBED_TYPE,
            batch_size=BATCH_SIZE,
            parallel=int(PARALLEL) if PARALLEL else None,
            providers=["CUDAExecutionProvider"]
        )
        logger.info(f"FastEmbed model '{embedding_model.model_name}' loaded successfully (GPU enabled).")
        yield
    except Exception as e:
        logger.error(f"Error loading FastEmbed model with CUDA: {e}")
        logger.info(f"Falling back to CPU.")
        try:
            embedding_model = TextEmbedding(
                model_name=MODEL_NAME,
                max_length=MAX_LENGTH,
                cache_dir=CACHE_DIR,
                threads=int(THREADS) if THREADS else None,
                doc_embed_type=DOC_EMBED_TYPE,
                batch_size=BATCH_SIZE,
                parallel=int(PARALLEL) if PARALLEL else None,
                providers=["CPUExecutionProvider"],
            )
            logger.info(f"FastEmbed model '{embedding_model.model_name}' loaded successfully (CPU).")
            yield
        except Exception as fallback_e:
            logger.error(f"Error loading FastEmbed model on CPU: {fallback_e}")
            yield
    finally:
        logger.info("Application shutdown.")

app = FastAPI(lifespan=lifespan)

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Mount Prometheus metrics client app
app.mount("/metrics/", metrics_app)

@app.post("/embeddings", response_model=EmbeddingResponse)
async def get_embeddings(request: EmbeddingRequest):
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model not loaded.")
    start_time = time.time()
    # Generate a unique request ID (e.g., using UUID)
    import uuid
    request_id = str(uuid.uuid4())
    logger.info(f"Received request {request_id} for /embeddings with {len(request.texts)} texts.")
    try:
        embeddings = embedding_model.embed(request.texts)
        processing_time = time.time() - start_time
        # Ensure the log entry is a single line, especially for file parsing
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "endpoint": "/embeddings",
            "request_id": request_id,
            "input_count": len(request.texts),
            "processing_time_ms": int(processing_time * 1000),
            "status_code": 200
        }
        # Dump log entry to JSON string
        logger.info(json.dumps(log_entry)) 
        return {"embeddings": list(embeddings)}
    except Exception as e:
        processing_time = time.time() - start_time # Still log time for errors
        error_log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "endpoint": "/embeddings",
            "request_id": request_id,
            "input_count": len(request.texts), # Include input count even on error
            "processing_time_ms": int(processing_time * 1000),
            "status_code": 500,
            "error_message": str(e),
            "error_type": type(e).__name__
        }
        logger.error(json.dumps(error_log_entry), exc_info=True) # Log JSON string for error
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {e}")

@app.get("/health")
async def health_check():
    model_name = embedding_model.model_name if embedding_model else None
    logger.info(f"Health check requested. Model status: {'loaded' if model_name else 'not loaded'}, model_name: {model_name}")
    return {"status": "ok", "model": embedding_model.model_name if embedding_model else None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
