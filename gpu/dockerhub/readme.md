<p style="text-align:center;" align="center">
  <img src="https://s3.svc.obaa.cloud/driver/fastembed-server-logo.png" width="200"/></a>
</p>

# FastEmbed embeddings API: [Self-hosted] [GPU]

This document describes a Docker image designed to provide a readily deployable FastEmbed embeddings API service for your projects, leveraging GPU acceleration for faster text embedding generation.

## Project Overview

This project offers a Docker container for running FastEmbed with GPU support, enabling accelerated text embedding generation for various NLP tasks on systems with NVIDIA GPUs.

## Docker Image
```bash
docker pull itsobaa/fastembed-gpu
```

* `itsobaa/fastembed-gpu:latest` (GPU)
    * **Size:** Approximately 2.34 GB [ `4.23GB uncompressed` ]
    * **Purpose:** Includes NVIDIA drivers and `fastembed-gpu` for GPU acceleration. It attempts to use the GPU and falls back to CPU if GPU initialization fails. Recommended for faster embedding generation on NVIDIA GPUs.

## Usage

This service exposes a simple HTTP API on port `8000` within the container.

### Prerequisites

* **Docker:** Ensure Docker is installed on your system.
* **NVIDIA Container Toolkit:** Ensure the NVIDIA Container Toolkit is installed and configured on your host machine to enable Docker to access your GPUs.

### Docker Compose Setup (Example)

Create a `docker-compose.yml` file:

```yaml
services:
  fastembed-gpu:
    container_name: fastembed-gpu
    image: itsobaa/fastembed-gpu:latest
    ports:
      - "8000:8000"
    volumes:
      - ./fastembed/storage/model_cache:/app/model_cache
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
     
    # Default configurations if not overridden

    # environment:
    #   - FASTEMBED_MODEL=BAAI/bge-small-en-v1.5
    #   - FASTEMBED_MAX_LENGTH=512
    #   - FASTEMBED_CACHE_DIR=/app/model_cache
    #   - FASTEMBED_THREADS=4
    #   - FASTEMBED_DOC_EMBED_TYPE=default
    #   - FASTEMBED_BATCH_SIZE=256
    #   - FASTEMBED_PARALLEL=None
```

### Running the Service

1.  Save the `docker-compose.yml` file.
2.  Navigate to the directory in your terminal.
3.  Start the service: `docker-compose up -d`

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

* `texts` (required): Array of text strings to embed.
* `dimension` (optional): Integer specifying the output embedding dimension. Check the model documentation for supported values.

### Response

```json
{
  "embeddings": [
    [[-0.08367343246936798,-0.06097422167658806,-0.01379495207220316,...,-0.022898558527231216],
    [-0.06326008588075638,0.03085922822356224,0.04183671623468399,...,-0.013004201464354992],
    ...
  ]
}
```

* `embeddings`: Array of embedding vectors corresponding to the input texts.

### Usage Example (curl)

```bash
curl -X POST -H "Content-Type: application/json" -d '{"texts": ["Sample text."] }' http://localhost:8000/embeddings
```

You can also specify the `dimension` parameter:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"texts": ["Sample text."], "dimension": 512 }' http://localhost:8000/embeddings
```

### Embedding Model Configuration

The FastEmbed model is configured using environment variables, with default values provided if not specified.

The following environment variables can be used to customize the `TextEmbedding` initialization:

* `FASTEMBED_MODEL`: Name of the FastEmbedding model to use (default: `BAAI/bge-small-en-v1.5`). See the [FastEmbed Supported Models](https://qdrant.github.io/fastembed/examples/Supported_Models/) for a list of available models.
* `FASTEMBED_MAX_LENGTH`: The maximum number of tokens (default: `512`).
* `FASTEMBED_CACHE_DIR`: The path to the cache directory (default: `./model_cache` inside the container).
* `FASTEMBED_THREADS`: The number of threads a single onnxruntime session can use (default: None).
* `FASTEMBED_DOC_EMBED_TYPE`: Specifies the document embedding type. Can be `"default"` or `"passage"` (default: `"default"`).
* `FASTEMBED_BATCH_SIZE`: Batch size for encoding (default: `256`). Higher values can improve speed but increase memory usage.
* `FASTEMBED_PARALLEL`: If `>1`, data-parallel encoding is used. If `0`, all available cores are used. If `None`, default onnxruntime threading is used (default: `None`).

You can set these environment variables in your Docker Compose file (as shown in the example) to customize the FastEmbed model and its behavior for this GPU-focused service.

Here are a few example models:

| Model                          | Dimension | Description                                                      | License     | Size (GB) |
| ------------------------------ | --------- | ---------------------------------------------------------------- | ----------- | --------- |
| BAAI/bge-small-en-v1.5         | 384       | Text embeddings, Unimodal (text), English, 512 sequence length | MIT         | 0.067     |
| sentence-transformers/all-MiniLM-L6-v2 | 384       | Text embeddings, Unimodal (text), English, 256 sequence length | Apache-2.0  | 0.090     |
| jinaai/jina-embeddings-v2-small-en | 512       | Text embeddings, Unimodal (text), English, 8192 sequence length | MIT         | 0.120     |
| nomic-ai/nomic-embed-text-v1.5     | 768       | Text embeddings, Multimodal (text, image), English, 2048 sequence length | Apache-2.0  | 0.520     |
| jinaai/jina-embeddings-v2-base-en  | 768       | Text embeddings, Unimodal (text), English, 8192 sequence length | Apache-2.0  | 0.520     |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2  | 768       | Text embeddings, Unimodal (text), Multilingual, 128 sequence length | Apache-2.0  | 1.000     |
| BAAI/bge-large-en-v1.5   | 1024       | Text embeddings, Unimodal (text), English, 512 sequence length | MIT         | 1.200     |


For a full list of supported models, please refer to the [FastEmbed Supported Models](https://qdrant.github.io/fastembed/examples/Supported_Models/). You can change the model by setting the `FASTEMBED_MODEL` environment variable in your `docker-compose.yml` for this service.

### Additional Resources

* **FastEmbed Project:** [https://qdrant.github.io/fastembed/](https://qdrant.github.io/fastembed/)
* **FastEmbed GPU Usage:** [https://qdrant.github.io/fastembed/examples/FastEmbed%5FGPU/](https://www.google.com/search?q=https://qdrant.github.io/fastembed/examples/FastEmbed%255FGPU/)
* **Hugging Face Models:** [https://huggingface.co/models](https://huggingface.co/models)
* **Docker Documentation:** [https://docs.docker.com/](https://docs.docker.com/)
* **Docker Compose Documentation:** [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
* **NVIDIA Container Toolkit Documentation:** [https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/user-guide.html](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/user-guide.html)
