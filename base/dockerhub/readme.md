<p style="text-align:center;" align="center">
  <img src="https://s3.svc.obaa.cloud/driver/fastembed-server-logo.png" width="200"/></a>  
</p>

# FastEmbed embeddings API: [Self-hosted] [CPU]

This document describes a Docker image designed to provide a readily deployable FastEmbed embeddings API service for your projects, optimized for CPU-based text embedding generation.

## Project Overview

This project offers a Docker container for running FastEmbed on CPU, enabling easy access to text embeddings for various NLP tasks in environments without GPU access.

## Docker Image
```bash
docker pull itsobaa/fastembed
```
* **\`itsobaa/fastembed:latest\` (CPU)**
    * **Size:** Approximately 119.41 MB [ `377MB uncompressed` ] 
    * **Purpose:** Optimized for CPU-based text embedding generation using the \`fastembed\` library. This smaller image is ideal for CPU-only environments.

## Usage

This service exposes a simple HTTP API on port \`8000\` within the container.

### Prerequisites

* **Docker:** Ensure Docker is installed on your system.

### Docker Compose Setup (Example)

Create a \`docker-compose.yml\` file:

```yaml
services:
  fastembed-cpu:
    container_name: fastembed-cpu
    image: itsobaa/fastembed:latest
    ports:
      - "8000:8000"
    volumes:
      - ./fastembed/storage/model_cache_cpu:/app/model_cache
    environment:
      - FASTEMBED_MODEL=BAAI/bge-small-en-v1.5 # Default model if not overridden
```

### Running the Service

1.  Save the \`docker-compose.yml\` file.
2.  Navigate to the directory in your terminal.
3.  Start the service: \`docker-compose up -d\`

### API Endpoint

* **Method:** \`POST\`
* **Path:** \`/embeddings\`
* **Content-Type:** \`application/json\`

### Request Parameters

```json
{
  "texts": ["text to embed 1", "another text to embed", ...],
  "dimension": 384 // Optional: specify embedding dimension if supported by the model
}
```

* \`texts\` (required): Array of text strings to embed.
* \`dimension\` (optional): Integer specifying the output embedding dimension. Check the model documentation for supported values.

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

* \`embeddings\`: Array of embedding vectors corresponding to the input texts.

### Usage Example (curl)

```bash
curl -X POST -H "Content-Type: application/json" -d '{"texts": ["Sample text."] }' http://localhost:8000/embeddings
```

You can also specify the \`dimension\` parameter:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"texts": ["Sample text."], "dimension": 512 }' http://localhost:8000/embeddings
```

### Embedding Model

The default embedding model used by this service is **\`BAAI/bge-small-en-v1.5\`** if the \`FASTEMBED_MODEL\` environment variable is not provided in your Docker Compose configuration.

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


For a full list of supported models, please refer to the [FastEmbed Supported Models](https://qdrant.github.io/fastembed/examples/Supported_Models/). You can change the model by setting the \`FASTEMBED_MODEL\` environment variable in your \`docker-compose.yml\` for this service.

### Additional Resources

* **FastEmbed Project:** [https://qdrant.github.io/fastembed/](https://qdrant.github.io/fastembed/)
* **Hugging Face Models:** [https://huggingface.co/models](https://huggingface.co/models)
* **Docker Documentation:** [https://docs.docker.com/](https://docs.docker.com/)
* **Docker Compose Documentation:** [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
`;
