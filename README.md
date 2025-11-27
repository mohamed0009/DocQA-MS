# MedBot Intelligence

> **Intelligent Medical Document Assistant powered by AI**  
> *Transforming Clinical Data into Actionable Insights*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://www.docker.com/)

## 🎯 Overview

**MedBot Intelligence** enables healthcare institutions to interrogate unstructured clinical documents using natural language queries while ensuring:
- 🔒 **HIPAA/GDPR Compliance** - Complete data anonymization and audit trails
- 🤖 **AI-Powered Q&A** - LLM-based question answering with source citations
- 🔍 **Semantic Search** - Medical domain-specific embeddings and vector search
- 📊 **Patient Synthesis** - Comparative analysis and timeline generation
- 🏥 **Clinical Integration** - Support for PDF, DOCX, HL7, FHIR formats

## 🏗️ Architecture

The system consists of 7 microservices:

1. **DocIngestor** - Document ingestion and parsing (PDF, DOCX, HL7, FHIR)
2. **DeID** - Automated anonymization using NLP (spaCy, Presidio)
3. **IndexeurSémantique** - Semantic indexing with medical embeddings (FAISS)
4. **LLMQAModule** - RAG-based question answering (LangChain, GPT-4/Llama)
5. **SyntheseComparative** - Patient comparison and synthesis
6. **AuditLogger** - Complete audit trails for compliance
7. **InterfaceClinique** - Modern web interface (React, TypeScript)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- GPU (recommended for LLM inference)
- 32GB RAM (minimum)
- 500GB storage

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/medbot-intelligence.git
cd medbot-intelligence

# Copy environment variables
cp .env.example .env

# Edit .env with your configurations (API keys, database credentials, etc.)
nano .env

# Start all services with Docker Compose
docker-compose up -d

# Check service health
docker-compose ps
```

### Access the Application

- **Web Interface**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672
- **Grafana Monitoring**: http://localhost:3001

## 📚 Documentation

- [Architecture Documentation](docs/architecture/)
- [API Reference](docs/api/)
- [Deployment Guide](docs/deployment/)
- [User Manual](docs/user-guide.md)
- [Development Guide](docs/development.md)

## 🔧 Technology Stack

### Backend
- **Language**: Python 3.11
- **API Framework**: FastAPI
- **Message Queue**: RabbitMQ
- **Database**: PostgreSQL
- **Vector DB**: FAISS
- **LLM**: GPT-4 / Llama 2 / Mistral
- **NLP**: spaCy, Presidio, SentenceTransformers

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Auth**: Auth0
- **Charts**: Chart.js

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose / Kubernetes
- **API Gateway**: Kong / Nginx
- **Monitoring**: Prometheus + Grafana
- **Logs**: ELK Stack

## 🧪 Testing

```bash
# Run all tests
docker-compose run --rm test

# Run unit tests for a specific service
docker-compose run --rm doc-ingestor pytest tests/

# Run integration tests
pytest tests/integration/

# Run end-to-end tests
pytest tests/e2e/
```

## 🔒 Security & Compliance

- ✅ End-to-end encryption (TLS 1.3)
- ✅ Automated PII detection and anonymization
- ✅ Role-based access control (RBAC)
- ✅ Complete audit trails
- ✅ HIPAA compliance measures
- ✅ GDPR compliance (right to erasure, data portability)

## 📊 Performance

- Document ingestion: < 5s per document
- De-identification: < 2s per page
- Semantic search: < 500ms (top-10 results)
- LLM response: < 10s for complex queries
- Web interface: < 2s page load

## 🤝 Contributing

This project is part of academic research. For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

Apache 2.0 - see [LICENSE](LICENSE)

## 📖 Citation

If you use this software in your research, please cite:

```bibtex
@software{medbot_intelligence_2025,
  title={MedBot Intelligence: An AI-Powered Medical Document Assistant},
  subtitle={Microservices Architecture with LLM Integration},
  author={Your Name},
  year={2025},
  publisher={SoftwareX},
  doi={10.5281/zenodo.XXXXXXX}
}
```

## 👥 Authors

- **Pr. Oumayma OUEDRHIRI** - O.ouedrhiri@emsi.ma
- **Pr. Hiba TABBAA** - H.Tabbaa@emsi.ma
- **Pr. Mohamed LACHGAR** - lachgar.m@gmail.com

## 📞 Support

For issues and questions:
- GitHub Issues: [github.com/your-org/medbot-intelligence/issues](https://github.com/your-org/medbot-intelligence/issues)
- Email: support@medbot-intelligence.org

---

**⚠️ Medical Disclaimer**: This system is designed to assist healthcare professionals. It should not be used as the sole basis for medical decisions. Always verify AI-generated information with clinical expertise and judgment.
