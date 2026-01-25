# MedBot-Intelligence

> **Intelligent Medical Document Assistant powered by AI**  
> *Transforming Clinical Data into Actionable Insights*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://www.docker.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.0+-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Microservices](#microservices)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Infrastructure](#infrastructure)
- [CI/CD](#cicd)
- [Documentation](#documentation)
- [License](#license)

---

## Overview

**MedBot-Intelligence** is a comprehensive microservices-based medical document processing platform that enables healthcare institutions to interrogate unstructured clinical documents using AI while ensuring HIPAA/GDPR compliance. The platform provides intelligent document analysis, de-identification, semantic search, and AI-powered question answering capabilities.

### Key Capabilities

- **Multi-Format Document Ingestion**: PDF, DOCX, HL7, FHIR
- **Privacy-First De-identification**: Automated PII/PHI removal with Presidio
- **Semantic Search**: FAISS-based vector search with embeddings
- **AI-Powered Q&A**: LLM integration for intelligent document querying
- **ML Predictions**: Clinical outcome predictions with model evaluation
- **Comprehensive Analytics**: Patient insights and comparative synthesis
- **Security & Compliance**: Audit logging, authentication, and authorization
- **Modern Web Interface**: Next.js/React-based clinical interface

---

## Architecture

The platform follows a **microservices architecture** with service discovery, message queuing, and centralized monitoring.

```
┌─────────────────────────────────────────────────────────────┐
│                    Clinical Interface                       │
│                (Next.js + React + TypeScript)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ API Gateway │ ← Port 8000
                    │   (FastAPI) │
                    └──────┬──────┘
                           │
    ┌──────────────────────┴──────────────────────┐
    │                                              │
    │          Microservices Layer                 │
    │                                              │
┌───┴────────┬──────────┬─────────┬────────┬──────▼──┬────────┐
│ DocIngestor│   DeID   │ Indexeur│ LLM QA │ ML      │Synthese│Audit│
│   :8001    │  :8002   │  :8003  │ :8004  │Predictor│ :8005  │:8006│
└───┬────────┴────┬─────┴────┬────┴───┬────┴────┬────┴───┬────┴──┬─┘
    │             │          │        │         │        │       │
    └─────────────┴──────────┴────────┴─────────┴────────┴───────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼─────┐      ┌───────▼──────┐    ┌───────▼──────┐
    │ RabbitMQ │      │  PostgreSQL  │    │    Redis     │
    │ :5672    │      │    :5432     │    │    :6379     │
    └──────────┘      └──────────────┘    └──────────────┘
```

### Service Discovery

- **Eureka Server** (:8761) - Netflix Eureka for dynamic service registration and discovery
- All microservices register with Eureka on startup
- API Gateway uses Eureka for service routing

---

## Features

### Document Processing
- **Multi-format support**: PDF, DOCX, HL7 v2.x, FHIR R4/R5
- **OCR capabilities**: Tesseract for scanned documents
- **Table extraction**: Automated table detection and parsing
- **Metadata extraction**: Author, dates, page count, document properties
- **Duplicate detection**: SHA256-based content hashing

### Privacy & Security
- **De-identification**: Microsoft Presidio for PII/PHI detection
- **Multiple strategies**: Redact, mask, synthesize, encrypt
- **Medical entity preservation**: Keep clinical terms intact
- **Audit logging**: Complete action tracking and compliance
- **HIPAA/GDPR compliance**: Industry-standard security measures

### AI & Machine Learning
- **Semantic indexing**: Sentence transformers + FAISS vector database
- **Question answering**: LLM integration (Ollama, OpenAI-compatible APIs)
- **ML predictions**: Clinical outcome models (Random Forest, XGBoost, CatBoost)
- **Model evaluation**: ROC curves, confusion matrices, training metrics
- **Comparative synthesis**: Multi-document analysis and summarization

### Infrastructure
- **Containerized deployment**: Docker + Docker Compose
- **Message queue**: RabbitMQ for async processing
- **Database**: PostgreSQL with multiple schemas
- **Caching**: Redis for performance optimization
- **Monitoring**: Prometheus + Grafana integration
- **CI/CD**: Jenkins pipeline with automated testing

---

## Microservices

### Core Services

| Service | Port | Description | Technologies |
|---------|------|-------------|--------------|
| **API Gateway** | 8000 | Central entry point, routing, authentication | FastAPI, Eureka Client |
| **Doc Ingestor** | 8001 | Document upload, parsing, storage | PyPDF2, python-docx, HL7apy, FHIR |
| **DeID** | 8002 | De-identification, anonymization | Presidio, spaCy, Transformers |
| **Indexeur Semantique** | 8003 | Semantic indexing, vector search | FAISS, Sentence Transformers |
| **LLM QA Module** | 8004 | Question answering, context retrieval | Ollama, LangChain, RAG |
| **ML Predictor** | 8007 | Clinical predictions, risk scoring | scikit-learn, XGBoost, CatBoost |
| **Synthese Comparative** | 8005 | Document comparison, synthesis | NLP, summarization |
| **Audit Logger** | 8006 | Security auditing, compliance tracking | PostgreSQL, structlog |

### Infrastructure Services

| Service | Port | Description |
|---------|------|-------------|
| **Eureka Server** | 8761 | Service discovery and registration |
| **PostgreSQL** | 5432 | Primary data store |
| **RabbitMQ** | 5672, 15672 | Message queue + Management UI |
| **Redis** | 6379 | Caching and session storage |
| **Prometheus** | 9090 | Metrics collection |
| **Grafana** | 3000 | Monitoring dashboards |

### Frontend

| Component | Port | Description |
|-----------|------|-------------|
| **Interface Clinique** | 3000 | Next.js web application |

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy
- **Validation**: Pydantic v2
- **Service Discovery**: py-eureka-client
- **Message Queue**: pika (RabbitMQ)
- **Caching**: redis-py

### AI/ML Libraries
- **NLP**: spaCy, Transformers (Hugging Face)
- **Privacy**: Microsoft Presidio Analyzer/Anonymizer
- **Embeddings**: sentence-transformers
- **Vector Search**: FAISS
- **LLM**: Ollama, LangChain
- **ML**: scikit-learn, XGBoost, CatBoost, pandas, numpy
- **Document Processing**: PyPDF2, python-docx, pdfplumber, pytesseract

### Frontend
- **Framework**: Next.js 16.0+
- **Language**: TypeScript 5+
- **UI Library**: React 19.2
- **Styling**: Tailwind CSS 4
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **Charts**: Chart.js, react-chartjs-2
- **Animation**: Framer Motion
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Service Discovery**: Netflix Eureka (Spring Boot)
- **Database**: PostgreSQL 15
- **Message Broker**: RabbitMQ 3.12
- **Cache**: Redis 7
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: Jenkins 2.400+

---

## Getting Started

### Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.11+ (for local development)
- **Node.js** 18+ and **npm** (for frontend development)
- **Git** 2.30+
- **Minimum 8GB RAM** (16GB recommended for full stack)
- **Windows 10/11** or **Linux** (WSL2 supported)

### Quick Start

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd MedBot-Intelligence
```

#### 2. Environment Configuration
```bash
# Copy the example environment file
cp env.local .env

# Edit .env with your configurations
# Update database passwords, API keys, etc.
```

#### 3. Start All Services
```powershell
# Windows PowerShell
.\scripts\setup-and-run-all.ps1
```

```bash
# Linux/macOS
docker-compose up -d
```

#### 4. Verify Services
```powershell
# Check service health
.\scripts\check-infrastructure.ps1

# View running containers
docker ps
```

#### 5. Access Applications

| Application | URL | Credentials |
|-------------|-----|-------------|
| **API Gateway** | http://localhost:8000 | - |
| **API Documentation** | http://localhost:8000/docs | - |
| **Eureka Dashboard** | http://localhost:8761 | - |
| **RabbitMQ Management** | http://localhost:15672 | docqa_rabbitmq / changeme |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Clinical Interface** | http://localhost:3000 | (dev mode) |

### Development Mode

#### Backend Services
```bash
# Start infrastructure only
docker-compose up postgres rabbitmq redis eureka-server -d

# Run a service locally (example: doc-ingestor)
cd services/doc-ingestor
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

#### Frontend
```bash
cd interface-clinique
npm install
npm run dev
```

---

## Infrastructure

### Database Schema

The platform uses PostgreSQL with multiple schemas:

- **public**: Shared tables, system configuration
- **doc_ingestor**: Document metadata, file storage references
- **deid**: De-identification records, entity mappings
- **indexeur**: Vector indices, embeddings metadata
- **llm_qa**: Q&A history, context retrieval logs
- **ml_predictor**: Model metadata, prediction results
- **audit**: Security logs, user actions

### Message Queue

RabbitMQ exchanges and queues:

- **document.uploaded** → doc-ingestor → deid
- **document.deidentified** → deid → indexeur-semantique
- **document.indexed** → indexeur → llm-qa-module
- **prediction.requested** → ml-predictor
- **audit.event** → audit-logger

### Data Storage

- **PostgreSQL volumes**: `postgres_data`
- **Document storage**: `document_storage`
- **FAISS indices**: `./data/faiss_indices`
- **Model cache**: `./models`
- **spaCy models**: `spacy_cache`

---

## CI/CD

### Jenkins Pipeline

The project includes a comprehensive Jenkins pipeline (`Jenkinsfile`) with:

- **Environment validation**: Check prerequisites
- **Dependency installation**: Python, Node.js packages
- **Linting**: Code quality checks
- **Unit tests**: Service-level testing
- **Integration tests**: End-to-end workflows
- **Docker builds**: Multi-service containerization
- **Deployment**: Automated rollout
- **Health checks**: Post-deployment verification

### Quick Start
```powershell
# Verify Jenkins prerequisites
.\.jenkins\health-check.ps1

# Start Jenkins (if using Docker)
docker run -d -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts
```

See [JENKINS_README.md](JENKINS_README.md) and [JENKINS_SETUP.md](JENKINS_SETUP.md) for detailed setup instructions.

---

## Documentation

### Comprehensive Guides

- **[MICROSERVICES_DETAILED_DOCUMENTATION.md](MICROSERVICES_DETAILED_DOCUMENTATION.md)** - In-depth technical documentation for all microservices
- **[EUREKA_INTEGRATION.md](EUREKA_INTEGRATION.md)** - Service discovery setup and usage
- **[JENKINS_SETUP.md](JENKINS_SETUP.md)** - Complete CI/CD configuration guide
- **[JENKINS_QUICK_START.md](JENKINS_QUICK_START.md)** - Fast-track Jenkins setup

### Interface Documentation

- **[interface-clinique/IMPLEMENTATION_SUMMARY.md](interface-clinique/IMPLEMENTATION_SUMMARY.md)** - Frontend architecture
- **[interface-clinique/QUICK_REFERENCE.md](interface-clinique/QUICK_REFERENCE.md)** - UI component reference

### Model Evaluation

- **[model_evaluation_results/MODEL_COMPARISON_REPORT.md](model_evaluation_results/MODEL_COMPARISON_REPORT.md)**
- **[model_evaluation_results/CONFUSION_MATRICES_ANALYSIS.md](model_evaluation_results/CONFUSION_MATRICES_ANALYSIS.md)**
- **[model_evaluation_results/TRAINING_CURVES_ANALYSIS.md](model_evaluation_results/TRAINING_CURVES_ANALYSIS.md)**

---

## Testing

### Run Tests
```bash
# Unit tests for a specific service
cd services/doc-ingestor
pytest tests/

# Integration tests
python test_analyzer.py
python test_eureka_integration.py
python test_presidio.py
python test_publish.py
```

### Test Data Generation
```bash
# Generate synthetic medical data
python scripts/data_collection/generate_synthetic_data.py

# Create large datasets for performance testing
python scripts/data_collection/generate_2gb_dataset.py
```

---

## Monitoring & Observability

### Prometheus Metrics

All services expose `/metrics` endpoints:
- Request counts and latencies
- Database connection pool stats
- Cache hit/miss rates
- Queue depths and processing times

### Grafana Dashboards

Pre-configured dashboards in `infrastructure/grafana/dashboards/`:
- System overview
- Service health
- Database performance
- Message queue metrics

### Structured Logging

All services use `structlog` for JSON-formatted logs:
```python
log.info("document_uploaded", 
         document_id=doc_id, 
         patient_id=patient_id, 
         file_size=size)
```

---

## Security & Compliance

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key management

### Data Protection
- End-to-end encryption for PHI
- At-rest encryption for database
- Secure credential management (environment variables)

### Audit Trail
- Complete user action logging
- Immutable audit records
- Compliance reporting

### HIPAA/GDPR Features
- Right to erasure (data deletion)
- Data portability (export)
- Breach notification logging
- Access control and monitoring

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- **Python**: Follow PEP 8, use `black` for formatting
- **TypeScript**: Follow Airbnb style guide, use Prettier
- **Commits**: Use conventional commits (feat:, fix:, docs:)

---

## Troubleshooting

### Common Issues

#### Services not starting
```powershell
# Check Docker daemon
docker info

# View service logs
docker-compose logs -f <service-name>

# Restart services
docker-compose restart
```

#### Database connection errors
```powershell
# Check PostgreSQL health
docker exec docqa-postgres pg_isready

# View database logs
docker logs docqa-postgres
```

#### Eureka registration failures
```powershell
# Verify Eureka server is running
curl http://localhost:8761/eureka/apps

# Check service environment variables
docker exec <container> env | grep EUREKA
```

---

## Scripts

### PowerShell Scripts (Windows)

| Script | Purpose |
|--------|---------|
| `setup-and-run-all.ps1` | Complete setup and launch |
| `run-all-services.ps1` | Start all services |
| `run-single-service.ps1` | Start individual service |
| `check-infrastructure.ps1` | Verify infrastructure health |
| `check_all_services_status.ps1` | Check all service statuses |
| `setup_eureka.ps1` | Configure Eureka server |

### Bash Scripts (Linux/macOS)

| Script | Purpose |
|--------|---------|
| `setup_eureka.sh` | Configure Eureka server |

### Python Scripts

| Script | Purpose |
|--------|---------|
| `scripts/ingest_data.py` | Bulk document ingestion |
| `scripts/train_models.py` | Train ML models |
| `scripts/evaluate_models.py` | Evaluate model performance |
| `scripts/show_patient_info.py` | Query patient data |

---

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.

---

## Authors & Acknowledgments

### Development Team
- Architecture and backend microservices
- Frontend interface development
- ML/AI model integration
- DevOps and infrastructure

### Technologies & Libraries
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework for production
- **Microsoft Presidio** - Privacy and PII protection
- **Netflix Eureka** - Service discovery
- **Hugging Face** - Transformers and embeddings
- **FAISS** - Vector similarity search

---

## Contact & Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Consult the [documentation](MICROSERVICES_DETAILED_DOCUMENTATION.md)
- Review the [FAQ](JENKINS_QUICK_START.md)

---




**Built for Healthcare Professionals**
