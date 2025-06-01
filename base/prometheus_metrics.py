import logging
import os
import time
import json
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge, CollectorRegistry, multiprocess

PROMETHEUS_MULTIPROC_DIR = os.environ.get("PROMETHEUS_MULTIPROC_DIR") # "/tmp/prometheus"

# --- Define Logging Level from Environment Variable ---
# Get log level from environment, default to INFO if not set
LOG_LEVEL_STR = os.environ.get("LOG_LEVEL", "INFO").upper()
# Map string level to logging module's level constants
# Use getattr to safely get the level, defaulting to INFO if invalid string
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
    ]
)
logger = logging.getLogger(__name__)

# --- Prometheus Metrics for the FastAPI app ---
# Note: If running with multiple Uvicorn/Gunicorn workers,
# you'll need multiprocess mode for prometheus_client.
# This is a common setup in production.
registry = CollectorRegistry()
if PROMETHEUS_MULTIPROC_DIR:
    # Create PROMETHEUS_MULTIPROC_DIR if it doesn't exist
    os.makedirs(os.environ["PROMETHEUS_MULTIPROC_DIR"], exist_ok=True)
    multiprocess.MultiProcessCollector(registry)
    logger.info(f"Prometheus client configured for multiprocess in {os.environ['PROMETHEUS_MULTIPROC_DIR']}")
else:
    logger.info("PROMETHEUS_MULTIPROC_DIR not set or empty. Running Prometheus client in single-process mode.")

REQUEST_COUNT = Counter(
    'fastembed_http_requests_total',
    'Total number of FastEmbed HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)
REQUEST_LATENCY = Histogram(
    'fastembed_http_request_duration_seconds',
    'Latency of FastEmbed HTTP requests in seconds',
    ['method', 'endpoint', 'status_code'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float('inf')),
    registry=registry
)
# You can add a gauge for current active requests if desired
REQUEST_IN_PROGRESS = Gauge(
    'fastembed_http_requests_in_progress',
    'Number of current in-progress FastEmbed HTTP requests',
    ['method', 'endpoint'],
    registry=registry
)

# --- FastAPI Middleware for metrics ---
class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = str(request.url.path)

        # Skip metrics for the metrics endpoint itself
        if endpoint in ["/health", "/metrics", "/metrics/"]:
            return await call_next(request)

        REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
        start_time = time.time()
        status_code = 500 # Default to 500 in case of unhandled exception

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            logger.error(f"Unhandled exception during request to {endpoint}: {e}")
            raise # Re-raise the exception to be handled by FastAPI's default error handler
        finally:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint, status_code=status_code).observe(duration)
            REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()
            # Log the request details here, including metrics data
            log_entry = {
                "timestamp": time.time_ns(), # Nanoseconds for Loki
                "level": "INFO" if status_code < 400 else "ERROR",
                "request_id": str(uuid.uuid4()), # Unique ID for each request
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "processing_time_s": round(duration, 4) # Time in seconds
            }
            if status_code >= 400:
                log_entry["message"] = "HTTP Request Error"
            else:
                log_entry["message"] = "HTTP Request Processed"

            logger.info(json.dumps(log_entry))

# --- Mount Prometheus metrics endpoint ---
# This will expose /metrics on the same port as your FastAPI app (8000)
# You need to manually handle the registry for multiprocess
metrics_app = make_asgi_app(registry=registry)