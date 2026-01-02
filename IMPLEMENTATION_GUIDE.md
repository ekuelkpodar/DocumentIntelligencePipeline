# Implementation Guide

This document provides a roadmap for completing the Document Intelligence Pipeline implementation.

## Current Status

### ✅ Completed Components

1. **Project Infrastructure**
   - [pyproject.toml](pyproject.toml) - Poetry dependency management
   - [.env.example](.env.example) - Environment configuration template
   - [.gitignore](.gitignore) - Git ignore rules
   - [Dockerfile](Dockerfile) - Container image definition
   - [docker-compose.yml](docker-compose.yml) - Multi-container orchestration

2. **Configuration & Settings**
   - [src/config.py](src/config.py) - Pydantic settings management
   - Environment variable validation and parsing

3. **Database Layer**
   - [alembic/](alembic/) - Migration framework setup
   - [alembic/versions/001_initial_schema.py](alembic/versions/001_initial_schema.py) - Complete database schema
   - PostgreSQL with pgvector and pg_trgm extensions
   - Tables: documents, extractions, invoices, receipts, menus, webhooks, audit_log

4. **Core Utilities**
   - [src/utils/logging.py](src/utils/logging.py) - Structured logging with structlog
   - [src/utils/metrics.py](src/utils/metrics.py) - Prometheus metrics
   - [src/utils/hashing.py](src/utils/hashing.py) - File hashing for deduplication
   - [src/utils/retry.py](src/utils/retry.py) - Retry decorators with exponential backoff
   - [src/core/exceptions.py](src/core/exceptions.py) - Custom exception hierarchy

5. **Document Processing**
   - [src/processors/base.py](src/processors/base.py) - Abstract processor interface
   - [src/processors/pdf_processor.py](src/processors/pdf_processor.py) - Full PDF processing with:
     - PDF to image conversion
     - Text extraction
     - Scanned PDF detection
     - Image optimization
     - Metadata extraction
   - [src/processors/image_processor.py](src/processors/image_processor.py) - Image processing with:
     - EXIF rotation
     - Deskewing
     - Contrast enhancement
     - Denoising
     - Format conversion

6. **Extraction Prompts**
   - [src/extractors/prompts/classification.py](src/extractors/prompts/classification.py) - Document type classification
   - [src/extractors/prompts/invoice.py](src/extractors/prompts/invoice.py) - Invoice extraction template
   - [src/extractors/prompts/receipt.py](src/extractors/prompts/receipt.py) - Receipt extraction template
   - [src/extractors/prompts/menu.py](src/extractors/prompts/menu.py) - Menu extraction template

## 🚧 Components to Implement

### High Priority (Core Functionality)

#### 1. Vision Extractors
**File**: `src/extractors/vision_extractor.py`

Implement Claude/GPT-4V integration:
```python
class VisionExtractor(BaseExtractor):
    async def extract(self, pages, document_type, template) -> ExtractionResult
    async def classify(self, pages) -> tuple[str, float]
    async def _call_claude(self, messages, max_tokens)
    async def _call_openai_fallback(self, messages, max_tokens)
```

Key features:
- Anthropic Claude API integration
- OpenAI fallback support
- Retry logic with exponential backoff
- JSON response parsing
- Multi-page handling
- Token tracking

**Dependencies**: anthropic, openai

#### 2. Database Models
**Directory**: `src/db/models/`

Create SQLAlchemy models matching the database schema:
- `document.py` - Document model
- `extraction.py` - Extraction model
- `invoice.py` - Invoice and InvoiceLineItem models
- `receipt.py` - Receipt and ReceiptLineItem models
- `menu.py` - Menu and MenuItem models
- `template.py` - ExtractionTemplate model
- `audit.py` - AuditLog model

**File**: `src/db/session.py`
- Async SQLAlchemy engine and session factory
- Connection pooling
- Transaction management

#### 3. Storage Backends
**Directory**: `src/storage/`

- `base.py` - Abstract storage interface
- `s3.py` - S3/MinIO implementation using boto3
  - Upload files
  - Download files
  - Generate presigned URLs
  - Delete files
- `local.py` - Local filesystem implementation (development)

#### 4. Database Repositories
**Directory**: `src/db/repositories/`

- `document_repo.py` - Document CRUD operations
- `extraction_repo.py` - Extraction operations
- `search_repo.py` - Full-text search queries

Pattern:
```python
class DocumentRepository:
    async def create(self, document: DocumentCreate) -> Document
    async def get_by_id(self, id: UUID) -> Document | None
    async def get_by_hash(self, file_hash: str) -> Document | None
    async def update_status(self, id: UUID, status: ProcessingStatus)
    async def list(self, filters: DocumentFilters) -> list[Document]
```

#### 5. Validators
**Directory**: `src/validators/`

- `base.py` - Abstract validator interface
- `invoice_validator.py` - Invoice validation logic
  - Required field checks
  - Math validation (line items sum to subtotal)
  - Date validation
  - Format validation
- `receipt_validator.py` - Receipt validation
- `menu_validator.py` - Menu validation
- `enrichment.py` - Data enrichment (vendor normalization, etc.)

#### 6. Core Pipeline
**File**: `src/core/pipeline.py`

Orchestrate the entire processing flow:
```python
class DocumentPipeline:
    async def process_document(self, file, external_id, document_type, webhook_url)
    # Steps:
    # 1. Validate and upload file
    # 2. Create document record
    # 3. Process document (PDF/image)
    # 4. Classify if needed
    # 5. Extract data
    # 6. Validate and enrich
    # 7. Store structured data
    # 8. Send webhook
```

### Medium Priority (API Layer)

#### 7. API Schemas
**Directory**: `src/api/schemas/`

Pydantic models for request/response:
- `document.py` - DocumentCreate, DocumentResponse, DocumentDetail
- `extraction.py` - ExtractionResponse, ExtractionCorrection
- `search.py` - SearchQuery, SearchResults
- `common.py` - Pagination, ErrorResponse

#### 8. API Routes
**Directory**: `src/api/routes/`

- `documents.py` - Document upload, status, management
- `extractions.py` - Extraction results, corrections
- `search.py` - Search and query endpoints
- `webhooks.py` - Webhook management
- `health.py` - Health checks

#### 9. API Middleware
**File**: `src/api/middleware.py`

- Authentication (API key validation)
- Request logging
- Error handling
- Rate limiting
- CORS configuration

#### 10. Main Application
**File**: `src/main.py`

FastAPI application setup:
- App initialization
- Router registration
- Middleware setup
- Startup/shutdown events
- Exception handlers

### Lower Priority (Background Processing)

#### 11. Background Worker
**Directory**: `src/queue/`

- `worker.py` - arq worker configuration
- `tasks.py` - Background task definitions
  - `process_document_task`
  - `send_webhook_task`
  - `cleanup_old_documents_task`
- `callbacks.py` - Webhook delivery logic

### Testing

#### 12. Test Suite
**Directory**: `tests/`

- `conftest.py` - Pytest fixtures
- `fixtures/` - Sample documents (PDF, images)
- `unit/` - Unit tests for each component
- `integration/` - End-to-end integration tests

Key test scenarios:
- PDF processing (valid, encrypted, corrupted)
- Image processing (rotation, deskew)
- Extraction (all document types)
- Validation (correct and incorrect data)
- API endpoints (CRUD operations)
- Search functionality

## Implementation Order

Recommended implementation sequence:

### Phase 1: Core Extraction (Week 1)
1. Database models and session
2. Storage backends (S3 + local)
3. Vision extractors
4. Database repositories
5. Test with sample documents

### Phase 2: Validation & Pipeline (Week 2)
6. Validators for each document type
7. Core pipeline orchestration
8. Integration tests

### Phase 3: API Layer (Week 3)
9. API schemas
10. API routes
11. Middleware and main app
12. API integration tests

### Phase 4: Background Processing (Week 4)
13. Background worker
14. Webhook delivery
15. Scheduled tasks

### Phase 5: Polish & Testing (Week 5)
16. Comprehensive test coverage
17. Performance optimization
18. Documentation updates
19. Deployment guide

## Quick Start Guide

### For New Developers

1. **Setup environment**
```bash
poetry install
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

2. **Start infrastructure**
```bash
docker-compose up -d postgres redis minio minio-setup
```

3. **Run migrations**
```bash
poetry run alembic upgrade head
```

4. **Pick a component to implement**
- Check the "Components to Implement" section above
- Start with Database Models or Storage Backends
- Follow the interfaces defined in base classes
- Write tests as you go

5. **Run tests**
```bash
poetry run pytest tests/unit/test_your_component.py
```

## Architecture Decisions

### Why async/await?
- FastAPI is async-native
- Better performance for I/O-bound operations (API calls, DB, storage)
- Supports concurrent document processing

### Why arq over Celery?
- Native async support
- Simpler configuration
- Redis-based (already using Redis)
- Better integration with asyncio

### Why SQLAlchemy ORM?
- Type safety with async support
- Relationship management
- Migration support via Alembic
- Wide adoption and community

### Why MinIO for development?
- S3-compatible API
- Easy local setup
- Production can use real S3
- No cloud costs during development

## Tips & Best Practices

1. **Always use structured logging**
```python
logger = get_logger(__name__)
logger.info("processing_document", document_id=doc_id, type=doc_type)
```

2. **Handle errors gracefully**
```python
try:
    result = await some_operation()
except SpecificError as e:
    logger.error("operation_failed", error=str(e))
    raise ProcessingError(f"Failed to process: {e}")
```

3. **Use type hints everywhere**
```python
async def process_document(
    file: UploadFile,
    document_type: str | None = None
) -> ProcessedDocument:
    ...
```

4. **Write testable code**
- Use dependency injection
- Mock external services (AI APIs, storage)
- Test edge cases

5. **Monitor performance**
```python
from src.utils.metrics import extraction_duration_seconds

with extraction_duration_seconds.labels(model="claude", type="invoice").time():
    result = await extractor.extract(pages)
```

## Common Patterns

### Repository Pattern
```python
class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document: DocumentCreate) -> Document:
        db_document = Document(**document.model_dump())
        self.session.add(db_document)
        await self.session.commit()
        await self.session.refresh(db_document)
        return db_document
```

### Dependency Injection
```python
async def get_document_repo(
    session: AsyncSession = Depends(get_session)
) -> DocumentRepository:
    return DocumentRepository(session)

@router.get("/documents/{document_id}")
async def get_document(
    document_id: UUID,
    repo: DocumentRepository = Depends(get_document_repo)
):
    return await repo.get_by_id(document_id)
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [arq Documentation](https://arq-docs.helpmanual.io/)

## Questions?

For questions or clarifications:
1. Check the specification in the original requirements
2. Review similar implementations in completed components
3. Refer to library documentation
4. Ask for help in team channels

Good luck with the implementation! 🚀
