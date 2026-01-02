# Document Intelligence Pipeline

A production-grade document intelligence system that automates extraction of structured data from PDFs, images, and scanned documents using vision AI models (Claude Sonnet 4.5 & GPT-4V).

## Features

### Core Capabilities
- **Multi-format Support**: PDF, JPEG, PNG, WebP, TIFF
- **Document Types**: Invoices, receipts, menus, forms, contracts
- **Vision AI Extraction**: Claude Sonnet 4.5 with GPT-4V fallback
- **Advanced Processing**: PDF conversion, image preprocessing, deskewing, OCR fallback
- **Validation & Enrichment**: Automated data validation and enrichment
- **Full-text Search**: PostgreSQL-powered search with fuzzy matching
- **Webhook Notifications**: Real-time updates on processing completion
- **Background Processing**: Async job queue with retry logic
- **Deduplication**: SHA-256 hash-based duplicate detection
- **Audit Trail**: Complete audit log of all operations

### Supported Document Types

#### Invoices
- Vendor and customer information
- Line items with quantities, prices, totals
- Tax, shipping, discounts
- Payment terms and methods

#### Receipts
- Merchant information
- Purchased items
- Payment details
- Automatic categorization

#### Menus
- Restaurant information
- Menu items with prices
- Dietary information (vegetarian, vegan, gluten-free)
- Allergen detection

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Client[Client Application]
        WebUI[Web Dashboard]
    end

    subgraph "API Layer"
        API[FastAPI Application<br/>Port 8000]
        Auth[Authentication<br/>Middleware]
        RateLimit[Rate Limiting]
    end

    subgraph "Processing Pipeline"
        Upload[Document Upload<br/>& Validation]
        Queue[Redis Queue<br/>arq]
        Worker[Background Worker<br/>Async Processing]

        subgraph "Document Processors"
            PDFProc[PDF Processor<br/>- Text Extraction<br/>- Page Conversion<br/>- Scanned Detection]
            ImgProc[Image Processor<br/>- EXIF Rotation<br/>- Deskewing<br/>- Enhancement]
        end

        subgraph "AI Extraction"
            Classifier[Document Classifier<br/>Claude Vision API]
            Extractor[Data Extractor<br/>Claude/GPT-4V]
        end

        subgraph "Validation"
            Validator[Data Validator<br/>- Math Checks<br/>- Format Validation]
            Enricher[Data Enrichment<br/>- Normalization<br/>- Vendor Lookup]
        end
    end

    subgraph "Storage Layer"
        S3[MinIO/S3<br/>Document Storage]
        Postgres[(PostgreSQL<br/>+ pgvector<br/>Structured Data)]
        Redis[(Redis<br/>Cache & Queue)]
    end

    subgraph "External Services"
        Claude[Anthropic Claude<br/>Sonnet 4.5]
        GPT4[OpenAI GPT-4V<br/>Fallback]
        Webhook[Webhook<br/>Notifications]
    end

    subgraph "Observability"
        Logs[Structured Logs<br/>structlog]
        Metrics[Prometheus<br/>Metrics]
    end

    Client --> API
    WebUI --> API
    API --> Auth
    Auth --> RateLimit
    RateLimit --> Upload
    Upload --> S3
    Upload --> Queue
    Upload --> Postgres

    Queue --> Worker
    Worker --> PDFProc
    Worker --> ImgProc

    PDFProc --> Classifier
    ImgProc --> Classifier

    Classifier --> Claude
    Classifier --> Extractor

    Extractor --> Claude
    Extractor --> GPT4
    Extractor --> Validator

    Validator --> Enricher
    Enricher --> Postgres
    Enricher --> Webhook

    Worker --> Redis
    Worker --> Logs
    Worker --> Metrics
    API --> Logs
    API --> Metrics

    style API fill:#4CAF50
    style Worker fill:#2196F3
    style Postgres fill:#FF9800
    style Claude fill:#9C27B0
    style PDFProc fill:#00BCD4
    style ImgProc fill:#00BCD4
```

### Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Queue
    participant Worker
    participant Storage
    participant AI as Claude/GPT-4V
    participant DB as PostgreSQL
    participant Webhook

    Client->>API: POST /documents (upload PDF/image)
    API->>API: Validate file (size, type, hash)
    API->>Storage: Upload to S3/MinIO
    API->>DB: Create document record (status: pending)
    API->>Queue: Enqueue processing job
    API-->>Client: 202 Accepted (document_id)

    Queue->>Worker: Dequeue job
    Worker->>DB: Update status: processing
    Worker->>Storage: Download document

    alt PDF Document
        Worker->>Worker: PDF Processor<br/>- Extract text<br/>- Convert to images<br/>- Detect if scanned
    else Image Document
        Worker->>Worker: Image Processor<br/>- EXIF rotation<br/>- Deskew<br/>- Enhance contrast
    end

    Worker->>DB: Update status: extracting
    Worker->>AI: Classify document type
    AI-->>Worker: document_type + confidence

    Worker->>AI: Extract structured data<br/>(with type-specific prompt)
    AI-->>Worker: JSON response with data

    Worker->>DB: Update status: validating
    Worker->>Worker: Validate extraction<br/>- Check required fields<br/>- Verify math<br/>- Format validation

    Worker->>Worker: Enrich data<br/>- Normalize values<br/>- Vendor lookup

    Worker->>DB: Store structured data<br/>(invoices/receipts/menus tables)
    Worker->>DB: Update status: completed

    Worker->>Webhook: Send completion notification
    Webhook-->>Client: POST webhook with results

    Client->>API: GET /documents/{id}
    API->>DB: Fetch document + extraction
    API-->>Client: 200 OK (full results)
```

### Data Flow Architecture

```mermaid
graph LR
    subgraph "Input"
        PDF[PDF Files]
        IMG[Images<br/>JPEG/PNG/TIFF]
    end

    subgraph "Preprocessing"
        HASH[SHA-256 Hash<br/>Deduplication]
        VALIDATE[File Validation<br/>Size/Type Check]
        STORE[S3 Storage]
    end

    subgraph "Processing"
        CONVERT[Format Conversion<br/>PDF→Images]
        ENHANCE[Image Enhancement<br/>Deskew/Denoise]
        OCR[OCR Fallback<br/>Tesseract]
    end

    subgraph "AI Extraction"
        CLASS[Classification<br/>Invoice/Receipt/Menu]
        EXTRACT[Data Extraction<br/>Structured JSON]
    end

    subgraph "Validation & Storage"
        VALID[Validation<br/>Math/Format Checks]
        ENRICH[Enrichment<br/>Normalization]
        PERSIST[(PostgreSQL<br/>Typed Tables)]
    end

    subgraph "Output"
        API_RESP[REST API<br/>JSON Response]
        SEARCH[Full-Text Search<br/>pg_trgm]
        ANALYTICS[Analytics Queries<br/>Spending/Trends]
        WEBHOOK[Webhook Events]
    end

    PDF --> HASH
    IMG --> HASH
    HASH --> VALIDATE
    VALIDATE --> STORE
    STORE --> CONVERT
    CONVERT --> ENHANCE
    ENHANCE --> OCR
    OCR --> CLASS
    CLASS --> EXTRACT
    EXTRACT --> VALID
    VALID --> ENRICH
    ENRICH --> PERSIST
    PERSIST --> API_RESP
    PERSIST --> SEARCH
    PERSIST --> ANALYTICS
    PERSIST --> WEBHOOK

    style CLASS fill:#9C27B0
    style EXTRACT fill:#9C27B0
    style PERSIST fill:#FF9800
```

### Database Schema Overview

```mermaid
erDiagram
    DOCUMENTS ||--o{ EXTRACTIONS : has
    DOCUMENTS ||--o| INVOICES : contains
    DOCUMENTS ||--o| RECEIPTS : contains
    DOCUMENTS ||--o| MENUS : contains
    EXTRACTIONS ||--o| INVOICES : validated_to
    EXTRACTIONS ||--o| RECEIPTS : validated_to
    EXTRACTIONS ||--o| MENUS : validated_to
    INVOICES ||--o{ INVOICE_LINE_ITEMS : has
    RECEIPTS ||--o{ RECEIPT_LINE_ITEMS : has
    MENUS ||--o{ MENU_ITEMS : has
    WEBHOOK_SUBSCRIPTIONS ||--o{ WEBHOOK_DELIVERIES : triggers
    DOCUMENTS ||--o{ AUDIT_LOG : tracked_by

    DOCUMENTS {
        uuid id PK
        string filename
        string mime_type
        bigint file_size_bytes
        string file_hash UK
        enum document_type
        enum status
        timestamp created_at
    }

    EXTRACTIONS {
        uuid id PK
        uuid document_id FK
        jsonb structured_data
        float confidence_score
        enum confidence_level
        string extraction_model
    }

    INVOICES {
        uuid id PK
        uuid document_id FK
        string vendor_name
        date invoice_date
        decimal total_amount
        string currency
    }

    RECEIPTS {
        uuid id PK
        uuid document_id FK
        string merchant_name
        date transaction_date
        decimal total_amount
        string category
    }

    MENUS {
        uuid id PK
        uuid document_id FK
        string restaurant_name
        string cuisine_type
    }
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- API Keys:
  - Anthropic API key (required)
  - OpenAI API key (optional, for fallback)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd DocumentIntelligencePipeline
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis on port 6379
- MinIO on ports 9000 (API) and 9001 (Console)
- FastAPI application on port 8000
- Background worker for processing

4. **Run database migrations**
```bash
docker-compose exec api alembic upgrade head
```

5. **Verify installation**
```bash
curl http://localhost:8000/health
```

## API Usage

### Authentication
All API requests require an API key in the header:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/documents
```

### Upload Document
```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "X-API-Key: your-api-key" \
  -F "file=@invoice.pdf" \
  -F "document_type=invoice"
```

## Project Structure

The project follows a modular architecture with clear separation of concerns:

```
document-intelligence/
├── src/
│   ├── api/              # FastAPI routes, schemas, middleware
│   ├── core/             # Core business logic and exceptions
│   ├── processors/       # PDF and image processing
│   ├── extractors/       # Vision AI extraction logic
│   ├── validators/       # Data validation and enrichment
│   ├── db/               # Database models and repositories
│   ├── storage/          # S3/MinIO storage backends
│   ├── queue/            # Background job processing
│   └── utils/            # Logging, metrics, helpers
├── alembic/              # Database migrations
├── tests/                # Comprehensive test suite
├── scripts/              # Utility scripts
└── docs/                 # Additional documentation
```

## Development Status

This project is a comprehensive implementation with the following components:

✅ **Completed:**
- Project structure and configuration
- Database schema with PostgreSQL + pgvector
- Alembic migrations setup
- Core exception handling
- Utility modules (logging, metrics, hashing, retry)
- PDF processor with advanced features
- Image processor with preprocessing
- Extraction prompts (invoice, receipt, menu, classification)
- Docker and docker-compose setup
- Comprehensive documentation

🚧 **To Be Implemented:**
- Vision extractor (Claude/GPT-4V integration)
- Validators and enrichment logic
- SQLAlchemy database models
- Storage backends (S3/MinIO interface)
- Database repositories
- Core pipeline orchestration
- API schemas (Pydantic models)
- API routes and endpoints
- Background worker and queue tasks
- FastAPI main application
- Test suite

## Next Steps

To continue development:

1. **Implement Vision Extractors** ([src/extractors/vision_extractor.py](src/extractors/vision_extractor.py))
2. **Create Database Models** ([src/db/models/](src/db/models/))
3. **Implement Storage Backends** ([src/storage/](src/storage/))
4. **Build API Layer** ([src/api/](src/api/))
5. **Create Main Application** ([src/main.py](src/main.py))
6. **Write Tests** ([tests/](tests/))

## Configuration

See [.env.example](.env.example) for all configuration options.

Key environment variables:
- `ANTHROPIC_API_KEY`: Required for Claude API
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `S3_*`: Storage configuration

## License

[Your License Here]

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request