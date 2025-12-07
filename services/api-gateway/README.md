# API Gateway Service

The API Gateway serves as the single entry point for all client requests to the MedBot Intelligence platform. It routes requests to the appropriate microservices and handles cross-cutting concerns.

## Features

- **Unified API Interface**: Single endpoint for all client applications
- **Request Routing**: Intelligent routing to backend microservices
- **Health Monitoring**: Aggregated health checks for all services
- **CORS Management**: Centralized CORS configuration
- **Error Handling**: Consistent error responses across all services

## Architecture

The API Gateway proxies requests to:
- **Doc Ingestor** (port 8001): Document upload and processing
- **DeID** (port 8002): De-identification services
- **Indexeur Sémantique** (port 8003): Semantic search and indexing
- **LLM QA Module** (port 8004): Question answering
- **Synthèse Comparative** (port 8005): Comparative analysis
- **Audit Logger** (port 8006): Audit logging

## API Endpoints

### Health
- `GET /api/v1/health` - Check health of all services

### Documents
- `POST /api/v1/documents/upload` - Upload a document
- `GET /api/v1/documents/{id}` - Get document by ID
- `GET /api/v1/documents/` - List documents

### Q&A
- `POST /api/v1/qa/ask` - Ask a question
- `GET /api/v1/qa/history/{patient_id}` - Get Q&A history

### Search
- `POST /api/v1/search/semantic` - Semantic search
- `GET /api/v1/search/` - Keyword search

### Comparative Analysis
- `POST /api/v1/comparative/analyze` - Analyze multiple documents
- `GET /api/v1/comparative/patient/{patient_id}` - Get patient timeline

### Audit
- `GET /api/v1/audit/logs` - Get audit logs
- `GET /api/v1/audit/stats` - Get audit statistics

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --reload --port 8000
```

## Docker

```bash
# Build
docker build -t medbot-api-gateway .

# Run
docker run -p 8000:8000 medbot-api-gateway
```

## Configuration

Environment variables:
- `DOC_INGESTOR_URL`: URL for document ingestor service
- `DEID_URL`: URL for de-identification service
- `INDEXEUR_SEMANTIQUE_URL`: URL for semantic indexing service
- `LLM_QA_URL`: URL for Q&A service
- `SYNTHESE_COMPARATIVE_URL`: URL for comparative analysis service
- `AUDIT_LOGGER_URL`: URL for audit logging service
- `CORS_ORIGINS`: Allowed CORS origins
- `SECRET_KEY`: Secret key for JWT tokens

## Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
