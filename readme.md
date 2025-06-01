<p style="text-align:center;" align="center">
  <img src="https://s3.svc.obaa.cloud/driver/fastembed-server-logo.png" width="200"/></a>
</p>

# FastEmbed API Server: [Self-hosted] [CPU] [GPU]

This document describes a set of Docker images designed to provide readily deployable FastEmbed embeddings API services for your projects. The aim is to simplify the integration of text embedding generation with both CPU and GPU acceleration, now featuring integrated monitoring and structured logging.

---

## Project Overview

This project offers Docker containers for running FastEmbed as a service, enabling easy access to text embeddings for various NLP tasks. By providing both CPU and GPU options, you can choose the best performance based on your available hardware. Both variants now include built-in **Prometheus metrics** for HTTP request performance monitoring and **structured JSON logging** for detailed event analysis.

---

## Docker Images

Two Docker images are available:

```bash
docker pull itsobaa/fastembed
```

1.  **`itsobaa/fastembed:latest` (CPU)**
    * **Size:** Approximately 245.3 MB [`397MB uncompressed`]
    * **Purpose:** Optimized for CPU-based text embedding generation using the `fastembed` library, now with enhanced observability features.

```bash
docker pull itsobaa/fastembed-gpu
```

2.  **`itsobaa/fastembed-gpu:latest` (GPU)**
    * **Size:** Approximately 2.7 GB [`4.25GB uncompressed`]
    * **Purpose:** Includes NVIDIA drivers and `fastembed-gpu` for GPU acceleration. It attempts to use the GPU and falls back to CPU if GPU initialization fails. Recommended for faster embedding generation on NVIDIA GPUs, also with enhanced observability.

---

## Usage

Both services expose an identical HTTP API on port `8000` within their respective containers, along with a dedicated metrics endpoint.

### Prerequisites

* **Docker:** Ensure Docker is installed on your system.
* **Docker Compose (Recommended):** Simplifies managing and running the services.
* **NVIDIA Container Toolkit (for GPU variant):** Ensure the NVIDIA Container Toolkit is installed and configured on your host machine to enable Docker to access your GPUs.
* **Prometheus:** For collecting metrics from the `/metrics` endpoints.
* **Grafana:** For visualizing metrics and logs.
* **Loki & Promtail:** For centralized log aggregation.

### Docker Compose Setup (Example)

Create a `docker-compose.yml` file. This example includes both CPU and GPU FastEmbed services, alongside a basic monitoring stack (Prometheus, Grafana, Loki, Promtail) to demonstrate the full observability setup.

```yaml
version: '3.8'

services:
  fastembed-cpu:
    container_name: fastembed-cpu
    image: itsobaa/fastembed:latest
    ports:
      - "8490:8000" # Exposes API and metrics on host port 8490
    volumes:
      - ./fastembed/storage/model_cache:/app/model_cache # For caching models
    environment:
      # Optional: FastEmbed model configurations
      # - FASTEMBED_MODEL=BAAI/bge-small-en-v1.5
      # - FASTEMBED_MAX_LENGTH=512
      # - FASTEMBED_CACHE_DIR=/app/model_cache
      # - FASTEMBED_THREADS=4
      # - FASTEMBED_DOC_EMBED_TYPE=default
      # - FASTEMBED_BATCH_SIZE=256
      # - FASTEMBED_PARALLEL=None

      # Monitoring & Logging Configuration
      - LOG_LEVEL=INFO # Set logging verbosity (DEBUG, INFO, WARNING, ERROR)
      # PROMETHEUS_MULTIPROC_DIR is used for multi-worker aggregation.
      # If running with a single Uvicorn worker, leave this unset or empty.
      # If running with multiple workers (e.g., via Gunicorn), set this to a path.
      # - PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus 
      # Mount a volume for PROMETHEUS_MULTIPROC_DIR if used:
      # volumes:
      #   - fastembed_metrics_tmp:/tmp/prometheus_cpu

    networks:
      - fastembed_network # Connect to a common network for observability services


  fastembed-gpu:
    container_name: fastembed-gpu
    image: itsobaa/fastembed-gpu:latest
    ports:
      - "8491:8000" # Exposes API and metrics on host port 8491
    volumes:
      - ./fastembed/storage/model_cache:/app/model_cache
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      # Optional: FastEmbed model configurations
      # - FASTEMBED_MODEL=BAAI/bge-small-en-v1.5
      # - FASTEMBED_MAX_LENGTH=512
      # - FASTEMBED_CACHE_DIR=/app/model_cache
      # - FASTEMBED_THREADS=4
      # - FASTEMBED_DOC_EMBED_TYPE=default
      # - FASTEMBED_BATCH_SIZE=256
      # - FASTEMBED_PARALLEL=None

      # Monitoring & Logging Configuration
      - LOG_LEVEL=INFO # Set logging verbosity (DEBUG, INFO, WARNING, ERROR)
      # PROMETHEUS_MULTIPROC_DIR is used for multi-worker aggregation.
      # If running with a single Uvicorn worker, leave this unset or empty.
      # If running with multiple workers (e.g., via Gunicorn), set this to a path.
      # - PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus 
      # Mount a volume for PROMETHEUS_MULTIPROC_DIR if used:
      # volumes:
      #   - fastembed_metrics_tmp:/tmp/prometheus_gpu

```

---

### Running the Services with Observability

1.  Save the `docker-compose.yml` file.
2.  Navigate to that directory in your terminal.
3.  Start all services: `docker-compose up -d`

### API Endpoints

* **FastEmbed API (CPU):**
    * **Method:** `POST`
    * **Path:** `/embeddings`
    * **Content-Type:** `application/json`
    * **Host Port:** `8490`
* **FastEmbed API (GPU):**
    * **Method:** `POST`
    * **Path:** `/embeddings`
    * **Content-Type:** `application/json`
    * **Host Port:** `8491`

* **Prometheus Metrics Endpoint:**
    * **Method:** `GET`
    * **Path:** `/metrics`
    * **Container Port:** `8000` (accessed via host ports `8490` for CPU, `8491` for GPU)
    * **Purpose:** Exposes HTTP request metrics (total requests, latency, in-progress requests) in Prometheus exposition format.

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
    [0.1, 0.2, ..., 0.n],
    [0.5, 0.6, ..., 0.n],
    ...
  ]
}
```

* `embeddings`: Array of embedding vectors corresponding to the input texts.

### Usage Example (curl)

**CPU Service (localhost:8490):**

```bash
curl -X POST -H "Content-Type: application/json" -d '{"texts": ["Sample text."] }' http://localhost:8490/embeddings
```

**GPU Service (localhost:8491):**

```bash
curl -X POST -H "Content-Type: application/json" -d '{"texts": ["Sample text."], "dimension": 512 }' http://localhost:8491/embeddings
```

---

## Monitoring and Logging

The FastEmbed API services are now instrumented for robust observability:

### Metrics (`/metrics`)

* **Endpoints:**
    * CPU: `http://localhost:8490/metrics`
    * GPU: `http://localhost:8491/metrics`
* **Type:** Prometheus Exposition Format
* **Metrics Collected:**
    * `fastembed_http_requests_total`: Total count of HTTP requests, labeled by `method`, `endpoint`, and `status_code`.
    * `fastembed_http_request_duration_seconds`: Histogram of HTTP request durations, labeled by `method`, `endpoint`, and `status_code`. Use this to calculate average latency, p90, p99, etc.
    * `fastembed_http_requests_in_progress`: Gauge indicating the number of currently active HTTP requests, labeled by `method` and `endpoint`.
* **Access:** You can view these raw metrics directly in your browser or configure Prometheus to scrape these endpoints.

### Logging

* **Format:** Structured JSON format (e.g., `{"timestamp": ..., "level": "INFO", "endpoint": "/embeddings", ...}`).
* **Destination:** Logs are written to `stdout`/`stderr` from the containers, then collected by Promtail and sent to Loki.
* **Purpose:** Provides detailed, per-request context for debugging, error tracing, and granular analysis. Includes `request_id`, processing time, and status code for each API call.
* **Access:** View logs in Grafana (using Loki as a data source).

### Key Observability Components

* **Prometheus:** Scrapes metrics from the `/metrics` endpoints of both FastEmbed services.
* **Grafana:** Provides dashboards for visualizing FastEmbed metrics and logs.
* **Loki:** Centralized log aggregation for FastEmbed application logs.
* **Promtail:** Agent that collects logs from the FastEmbed containers and sends them to Loki.

### Getting Container-Level CPU/Memory/GPU Metrics

For comprehensive CPU, memory, and **GPU usage** of your FastEmbed containers, it's highly recommended to deploy external tools. Consider these options:

* **cAdvisor:** Ideal for detailed per-container CPU, memory, and basic I/O metrics.
* **Prometheus Node Exporter with NVIDIA GPU Exporter:** For host-level metrics and highly detailed NVIDIA GPU utilization metrics.

---

## Embedding Model Configuration

The FastEmbed model is configured using environment variables, with default values provided if not specified.

The following environment variables can be used to customize the `TextEmbedding` initialization:

* `FASTEMBED_MODEL`: Name of the FastEmbedding model to use (default: `BAAI/bge-small-en-v1.5`). See the [FastEmbed Supported Models](https://qdrant.github.io/fastembed/examples/Supported_Models/) for a list of available models.
* `FASTEMBED_MAX_LENGTH`: The maximum number of tokens (default: `512`).
* `FASTEMBED_CACHE_DIR`: The path to the cache directory (default: `./model_cache` inside the container).
* `FASTEMBED_THREADS`: The number of threads a single onnxruntime session can use (default: `None`).
* `FASTEMBED_DOC_EMBED_TYPE`: Specifies the document embedding type. Can be `"default"` or `"passage"` (default: `"default"`).
* `FASTEMBED_BATCH_SIZE`: Batch size for encoding (default: `256`). Higher values can improve speed but increase memory usage.
* `FASTEMBED_PARALLEL`: If `>1`, data-parallel encoding is used. If `0`, all available cores are used. If `None`, default onnxruntime threading is used (default: `None`).

You can set these environment variables in your Docker Compose file (as shown in the example) to customize the FastEmbed model and its behavior for each service.

Here are a few example models:

| Model                                         | Dimension | Description                                                      | License    | Size (GB) |
| :-------------------------------------------- | :-------- | :--------------------------------------------------------------- | :--------- | :-------- |
| BAAI/bge-small-en-v1.5                        | 384       | Text embeddings, Unimodal (text), English, 512 sequence length | MIT        | 0.067     |
| sentence-transformers/all-MiniLM-L6-v2        | 384       | Text embeddings, Unimodal (text), English, 256 sequence length | Apache-2.0 | 0.090     |
| jinaai/jina-embeddings-v2-small-en            | 512       | Text embeddings, Unimodal (text), English, 8192 sequence length | MIT        | 0.120     |
| nomic-ai/nomic-embed-text-v1.5                | 768       | Text embeddings, Multimodal (text, image), English, 2048 sequence length | Apache-2.0 | 0.520     |
| jinaai/jina-embeddings-v2-base-en             | 768       | Text embeddings, Unimodal (text), English, 8192 sequence length | Apache-2.0 | 0.520     |
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | 768       | Text embeddings, Unimodal (text), Multilingual, 128 sequence length | Apache-2.0 | 1.000     |
| BAAI/bge-large-en-v1.5                        | 1024      | Text embeddings, Unimodal (text), English, 512 sequence length | MIT        | 1.200     |


For a full list of supported models, please refer to the [FastEmbed Supported Models](https://qdrant.github.io/fastembed/examples/Supported_Models/). You can change the model by setting the `FASTEMBED_MODEL` environment variable in your `docker-compose.yml` for each service.

---

### Additional Resources

* **FastEmbed Project:** [https://qdrant.github.io/fastembed/](https://qdrant.github.io/fastembed/)
* **FastEmbed GPU Usage:** [https://qdrant.github.io/fastembed/examples/FastEmbed%5FGPU/](https://qdrant.github.io/fastembed/examples/FastEmbed%5FGPU/)
* **Hugging Face Models:** [https://huggingface.co/models](https://huggingface.co/models)
* **Docker Documentation:** [https://docs.docker.com/](https://docs.docker.com/)
* **Docker Compose Documentation:** [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
* **NVIDIA Container Toolkit Documentation:** [https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/user-guide.html](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/user-guide.html)
* **Prometheus Documentation:** [https://prometheus.io/docs/](https://prometheus.io/docs/)
* **Grafana Documentation:** [https://grafana.com/docs/](https://grafana.com/docs/)
* **Loki Documentation:** [https://grafana.com/docs/loki/latest/](https://grafana.com/docs/loki/latest/)
* **Promtail Documentation:** [https://grafana.com/docs/loki/latest/clients/promtail/](https://grafana.com/docs/loki/latest/clients/promtail/)
