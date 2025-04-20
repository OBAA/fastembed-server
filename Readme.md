# FastEmbed API Server: [CPU & GPU Options]

This document describes a set of Docker images designed to provide readily deployable FastEmbed embeddings API services for your projects. The aim is to simplify the integration of text embedding generation with both CPU and GPU acceleration.

## Project Overview

This project offers Docker containers for running FastEmbed as a service, enabling easy access to text embeddings for various NLP tasks. By providing both CPU and GPU options, you can choose the best performance based on your available hardware.

## Docker Images

Two Docker images are available:

1.  **`dcr.svc.obaa.cloud/fastembed:v0.6.0` (CPU)**
    * **Size:** Approximately 377MB
    * **Purpose:** Optimized for CPU-based text embedding generation using the `fastembed` library. This smaller image is ideal for CPU-only environments.

2.  **`dcr.svc.obaa.cloud/fastembed-gpu:v0.6.0` (GPU)**
    * **Size:** Approximately 4.23GB
    * **Purpose:** Includes NVIDIA drivers and `fastembed-gpu` for GPU acceleration. It attempts to use the GPU and falls back to CPU if GPU initialization fails. Recommended for faster embedding generation on NVIDIA GPUs.

## Usage

Both services expose an identical HTTP API on port `8000` within their respective containers.

### Prerequisites

* **Docker:** Ensure Docker is installed on your system.
* **Docker Compose (Recommended):** Simplifies managing and running the services.

### Docker Compose Setup (Example)

Create a `docker-compose.yml` file:

```yaml
services:

  fastembed-cpu:
    container_name: fastembed-cpu
    image: dcr.svc.obaa.cloud/fastembed:v0.6.0
    ports:
      - "8490:8000"
    volumes:
      - ./fastembed/storage/model_cache_cpu:/app/model_cache
    environment:
      - FASTEMBED_MODEL=BAAI/bge-small-en-v1.5 # Default model if not overridden

  fastembed-gpu:
    container_name: fastembed-gpu
    image: dcr.svc.obaa.cloud/fastembed-gpu:v0.6.0
    ports:
      - "8491:8000"
    environment:
      - FASTEMBED_MODEL=nomic-ai/nomic-embed-text-v1.5 # Default model if not overridden
    volumes:
      - ./fastembed/storage/model_cache_gpu:/app/model_cache
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Running the Services

1.  Save the `docker-compose.yml` file.
2.  Navigate to the directory in your terminal.
3.  Start the services: `docker-compose up -d`

### API Endpoint

* **Method:** `POST`
* **Path:** `/embeddings`
* **Content-Type:** `application/json`

### Request Parameters

```json
{
  "texts": ["text to embed 1", "another text to embed", ...],
  "dimension": 384 // Optional: specify embedding dimension if supported by the model
}
```

* **`texts` (required):** Array of text strings to embed.
* **`dimension` (optional):** Integer specifying the output embedding dimension. Check the model documentation for supported values.

### Response

```json
{
  "embeddings": [
    [0.1, 0.2, ..., 0.n],
    [0.5, 0.6, ..., 0.n],
    ...
  ]
}
```

* **`embeddings`:** Array of embedding vectors corresponding to the input texts.

### Usage Example (curl)

**CPU Service (localhost:8490):**

```bash
curl -X POST -H "Content-Type: application/json" -d '{"texts": ["Sample text."] }' http://localhost:8490/embeddings
```

**GPU Service (localhost:8491):**

```bash
curl -X POST -H "Content-Type: application/json" -d '{"texts": ["Sample text."], "dimension": 512 }' http://localhost:8491/embeddings
```

### Embedding Model

The default embedding model used by both services is **`BAAI/bge-small-en-v1.5`** if the `FASTEMBED_MODEL` environment variable is not provided in your Docker Compose configuration.

Here are a few example models:

| Model                          | Dimension | Description                                                      | License     | Size (GB) |
| ------------------------------ | --------- | ---------------------------------------------------------------- | ----------- | --------- |
| BAAI/bge-small-en-v1.5         | 384       | Text embeddings, Unimodal (text), English, 512 sequence length | MIT         | 0.067     |
| sentence-transformers/all-MiniLM-L6-v2 | 384       | Text embeddings, Unimodal (text), English, 256 sequence length | Apache-2.0  | 0.090     |
| jinaai/jina-embeddings-v2-small-en | 512       | Text embeddings, Unimodal (text), English, 8192 sequence length | MIT         | 0.120     |
| nomic-ai/nomic-embed-text-v1.5     | 768       | Text embeddings, Multimodal (text, image), English, 2048 sequence length | Apache-2.0  | 0.520     |
| jinaai/jina-embeddings-v2-base-en	 | 768       | Text embeddings, Unimodal (text), English, 8192 sequence length | Apache-2.0  | 0.520     |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2	 | 768       | Text embeddings, Unimodal (text), Multilingual, 128 sequence length | Apache-2.0  | 1.000     |
| BAAI/bge-large-en-v1.5	 | 1024       | Text embeddings, Unimodal (text), English, 512 sequence length | MIT         | 1.200     |




For a full list of supported models, please refer to the [FastEmbed Supported Models](https://qdrant.github.io/fastembed/examples/Supported_Models/). You can change the model by setting the `FASTEMBED_MODEL` environment variable in your `docker-compose.yml` for each service.

### Additional Resources

* **FastEmbed Project:** [https://qdrant.github.io/fastembed/](https://qdrant.github.io/fastembed/)
* **FastEmbed GPU Usage:** [https://qdrant.github.io/fastembed/examples/FastEmbed%5FGPU/](https://www.google.com/search?q=https://qdrant.github.io/fastembed/examples/FastEmbed%255FGPU/)
* **Hugging Face Models:** [https://huggingface.co/models](https://huggingface.co/models)
* **Docker Documentation:** [https://docs.docker.com/](https://docs.docker.com/)
* **Docker Compose Documentation:** [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
`;

