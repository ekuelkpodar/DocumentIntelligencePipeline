"""Prometheus metrics for monitoring."""

from prometheus_client import Counter, Histogram, Gauge

# Document processing metrics
documents_uploaded_total = Counter(
    "documents_uploaded_total",
    "Total number of documents uploaded",
    ["document_type"],
)

documents_processed_total = Counter(
    "documents_processed_total",
    "Total number of documents processed",
    ["document_type", "status"],
)

document_processing_duration_seconds = Histogram(
    "document_processing_duration_seconds",
    "Document processing duration in seconds",
    ["document_type"],
    buckets=[1, 5, 10, 30, 60, 120, 300],
)

document_file_size_bytes = Histogram(
    "document_file_size_bytes",
    "Document file size in bytes",
    ["document_type"],
    buckets=[1024, 10240, 102400, 1048576, 10485760, 52428800],  # 1KB to 50MB
)

# Extraction metrics
extraction_requests_total = Counter(
    "extraction_requests_total",
    "Total number of extraction requests",
    ["model", "document_type"],
)

extraction_failures_total = Counter(
    "extraction_failures_total",
    "Total number of extraction failures",
    ["model", "document_type", "error_type"],
)

extraction_duration_seconds = Histogram(
    "extraction_duration_seconds",
    "Extraction duration in seconds",
    ["model", "document_type"],
    buckets=[1, 5, 10, 30, 60, 120],
)

extraction_confidence_score = Histogram(
    "extraction_confidence_score",
    "Extraction confidence scores",
    ["document_type"],
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0],
)

extraction_tokens_used = Histogram(
    "extraction_tokens_used",
    "Tokens used in extraction",
    ["model", "document_type", "token_type"],
    buckets=[100, 500, 1000, 2000, 5000, 10000],
)

# Storage metrics
storage_operations_total = Counter(
    "storage_operations_total",
    "Total storage operations",
    ["operation", "status"],
)

storage_operation_duration_seconds = Histogram(
    "storage_operation_duration_seconds",
    "Storage operation duration",
    ["operation"],
    buckets=[0.1, 0.5, 1, 2, 5, 10],
)

# Queue metrics
queue_jobs_enqueued_total = Counter(
    "queue_jobs_enqueued_total",
    "Total jobs enqueued",
    ["job_type"],
)

queue_jobs_completed_total = Counter(
    "queue_jobs_completed_total",
    "Total jobs completed",
    ["job_type", "status"],
)

queue_job_duration_seconds = Histogram(
    "queue_job_duration_seconds",
    "Queue job execution duration",
    ["job_type"],
    buckets=[1, 10, 30, 60, 300, 600],
)

queue_size = Gauge(
    "queue_size",
    "Current queue size",
    ["queue_name"],
)

# Webhook metrics
webhook_deliveries_total = Counter(
    "webhook_deliveries_total",
    "Total webhook deliveries attempted",
    ["event_type", "status"],
)

webhook_delivery_duration_seconds = Histogram(
    "webhook_delivery_duration_seconds",
    "Webhook delivery duration",
    ["event_type"],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30],
)

# API metrics
api_requests_total = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status_code"],
)

api_request_duration_seconds = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5],
)
