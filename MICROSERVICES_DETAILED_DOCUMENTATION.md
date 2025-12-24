# 📚 MedBot Intelligence - Detailed Microservices Documentation

> **Comprehensive Technical Overview of All Microservices**  
> *Last Updated: December 20, 2025*

---

## 🏛️ System Architecture Overview

MedBot Intelligence is a **microservices-based medical document processing platform** that enables healthcare institutions to interrogate unstructured clinical documents using AI while ensuring HIPAA/GDPR compliance.

### Architecture Components
```
┌─────────────────┐
│ InterfaceClinique│ ← Web UI (React + TypeScript)
└────────┬────────┘
         │
    ┌────▼────┐
    │   API   │ ← API Gateway (Port 8000)
    │ Gateway │
    └────┬────┘
         │
    ┌────┴─────────────────────────────────────┐
    │                                          │
    │         Microservices Layer              │
    │                                          │
├───▼───────┬──────────┬──────────┬────────┬──▼────────┐
│DocIngestor│   DeID   │Indexeur  │LLM QA  │Synthese  │Audit│
│  :8001    │  :8002   │ :8003    │ :8004  │ :8005    │:8006│
└───┬───────┴──────┬───┴────┬─────┴───┬────┴────┬─────┴──┬──┘
    │              │        │         │         │        │
    └──────────────┴────────┴─────────┴─────────┴────────┘
                           │
                    ┌──────▼────────┐
                    │   RabbitMQ    │ ← Message Queue
                    └───────────────┘
                           │
                    ┌──────▼────────┐
                    │  PostgreSQL   │ ← Databases
                    └───────────────┘
```

---

## 1️⃣ DocIngestor Service

### 📌 Overview
**Port:** 8001  
**Purpose:** Document ingestion, parsing, and initial processing  
**Status:** ✅ 100% Operational

### 🎯 Core Responsibilities
- Accept and validate document uploads (PDF, DOCX, HL7, FHIR)
- Parse documents and extract text, metadata, and structure
- Perform OCR on scanned documents
- Calculate file hashes for deduplication
- Store documents in PostgreSQL
- Publish processing events to RabbitMQ

### 🔧 Technical Features

#### Supported Document Formats
1. **PDF Documents**
   - Native text extraction using PyPDF2
   - Table extraction with pdfplumber
   - OCR for scanned documents (Tesseract)
   - Metadata extraction (author, dates, page count)
   
2. **DOCX Documents**
   - Text and paragraph extraction
   - Table detection and parsing
   - Document properties and metadata
   
3. **HL7 v2.x Messages**
   - PID segments (patient information)
   - OBX segments (observations and results)
   - NTE segments (clinical notes)
   - MSH segments (message metadata)
   
4. **FHIR Resources (R4/R5)**
   - DocumentReference resources
   - Patient resources
   - Observation resources
   - Bundle support (multiple resources)

#### File Management Features
- File size validation (configurable limits)
- Extension whitelisting
- SHA256 content hashing
- Duplicate detection
- Secure file storage
- Transaction management

### 🌐 API Endpoints

#### 1. Upload Document
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

Parameters:
  file: <binary>
  patient_id: string (optional)
  document_type: string (optional)
  author: string (optional)
  department: string (optional)

Response:
{
  "id": "uuid",
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1234567,
  "status": "completed",
  "content_hash": "sha256...",
  "created_at": "2025-12-20T19:00:00",
  "message": "Document processed successfully"
}
```

#### 2. List Documents
```http
GET /api/v1/documents?page=1&page_size=20&patient_id=PAT001

Response:
{
  "total": 42,
  "page": 1,
  "page_size": 20,
  "documents": [...]
}
```

#### 3. Get Document by ID
```http
GET /api/v1/documents/{document_id}

Response:
{
  "id": "uuid",
  "filename": "report.pdf",
  "content": "extracted text...",
  "metadata": {...},
  "status": "completed"
}
```

#### 4. Update Document Metadata
```http
PATCH /api/v1/documents/{document_id}
Content-Type: application/json

{
  "patient_id": "PAT002",
  "document_type": "ordonnance"
}
```

#### 5. Delete Document
```http
DELETE /api/v1/documents/{document_id}
```

### 📊 Performance Metrics
- PDF Processing: ~2-5 seconds per document
- OCR Processing: ~5-10 seconds per page
- DOCX Processing: ~1-2 seconds
- HL7/FHIR Processing: <1 second
- Database Operations: <100ms

### 🗄️ Database Schema
```sql
Table: documents
- id: UUID (PK)
- filename: VARCHAR(255)
- file_type: VARCHAR(50)
- file_size: BIGINT
- content: TEXT
- content_hash: VARCHAR(64)
- patient_id: VARCHAR(100)
- document_type: VARCHAR(100)
- author: VARCHAR(255)
- department: VARCHAR(255)
- metadata: JSONB
- status: VARCHAR(50)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### 🔗 Integration Points
- **Input:** HTTP file uploads
- **Output:** RabbitMQ queue `document_uploaded`
- **Storage:** Local filesystem + PostgreSQL

---

## 2️⃣ DeID Service (De-identification)

### 📌 Overview
**Port:** 8002  
**Purpose:** Automated PII detection and anonymization  
**Status:** ✅ 100% Operational

### 🎯 Core Responsibilities
- Detect personally identifiable information (PII)
- Anonymize sensitive data using multiple strategies
- Preserve medical terminology and context
- Ensure HIPAA/GDPR compliance
- Maintain complete audit trails

### 🔧 Technical Features

#### PII Detection Capabilities
Uses **Presidio** and **spaCy** for detecting:
- 👤 **Names** (patients, doctors, family members)
- 📧 **Email addresses**
- 📞 **Phone numbers**
- 🏠 **Addresses** (street, city, state, zip)
- 🆔 **Social Security Numbers**
- 🏥 **Patient IDs** and medical record numbers
- 📅 **Dates** (birth dates, appointment dates)
- 🏢 **Organizations** and hospitals
- 🌐 **URLs** and IP addresses
- 💳 **Credit card numbers**

#### Confidence Scoring
- Default threshold: **0.85**
- Adjustable per document type
- Reduces false positives

#### Medical Entity Preservation
Intelligently preserves medical context:
- ✅ Disease names (e.g., "Type 2 Diabetes Mellitus")
- ✅ Medications (e.g., "Metformin 500mg BID")
- ✅ Procedures (e.g., "Appendectomy")
- ✅ Lab values (e.g., "HbA1c: 7.2%")
- ✅ Medical abbreviations

### 🛡️ Four Anonymization Strategies

#### 1. Redact Strategy
Replace sensitive data with `[REDACTED]`
```
Input:  "Patient John Smith, SSN 123-45-6789"
Output: "Patient [REDACTED], SSN [REDACTED]"
```

#### 2. Replace Strategy
Use generic placeholders
```
Input:  "Contact john@email.com or 555-1234"
Output: "Contact [EMAIL] or [PHONE]"
```

#### 3. Hash Strategy
Cryptographic hashing (SHA256)
```
Input:  "Dr. Jane Doe"
Output: "Dr. [HASH_a1b2c3d4]"
```
- Consistent: Same input → Same hash
- Useful for linkage without revealing identity

#### 4. Synthesize Strategy
Generate realistic fake data (using Faker)
```
Input:  "Patient ID: PAT12345, DOB: 1980-05-15"
Output: "Patient ID: PAT67890, DOB: 1975-03-22"
```
- Maintains data utility
- Preserves demographic distributions
- Best for analytics and research

### 🌐 API Endpoints

#### 1. Anonymize Text
```http
POST /api/v1/anonymization/anonymize
Content-Type: application/json

{
  "text": "Patient John Smith (SSN: 123-45-6789) visited...",
  "strategy": "synthesize",
  "preserve_medical": true,
  "confidence_threshold": 0.85
}

Response:
{
  "anonymized_text": "Patient Jane Doe (SSN: 987-65-4321) visited...",
  "entities_found": 2,
  "entities": [
    {
      "type": "PERSON",
      "text": "John Smith",
      "start": 8,
      "end": 18,
      "confidence": 0.95
    }
  ],
  "strategy_used": "synthesize"
}
```

#### 2. Analyze PII (Detection Only)
```http
POST /api/v1/anonymization/analyze
Content-Type: application/json

{
  "text": "Contact Dr. Jane Doe at jane@hospital.com"
}

Response:
{
  "entities": [
    {"type": "PERSON", "text": "Jane Doe", "confidence": 0.92},
    {"type": "EMAIL", "text": "jane@hospital.com", "confidence": 0.99}
  ],
  "total_found": 2
}
```

#### 3. Get Available Strategies
```http
GET /api/v1/anonymization/strategies

Response:
["redact", "replace", "hash", "synthesize"]
```

#### 4. Get Supported Entity Types
```http
GET /api/v1/anonymization/entities

Response:
["PERSON", "EMAIL", "PHONE", "SSN", "ADDRESS", "DATE", ...]
```

### 📊 Performance Metrics
- PII Detection: ~100-200ms per document
- Anonymization: ~50-100ms
- Total Processing: <500ms per document
- Throughput: ~100 documents/minute

### 🗄️ Database Schema
```sql
Table: anonymization_logs
- id: UUID (PK)
- document_id: UUID (FK)
- original_hash: VARCHAR(64)
- strategy: VARCHAR(50)
- entities_found: INTEGER
- entities_detail: JSONB
- processing_time_ms: INTEGER
- created_at: TIMESTAMP
```

### 🔗 Integration Points
- **Input:** RabbitMQ queue `document_uploaded`
- **Output:** RabbitMQ queue `document_anonymized`
- **Storage:** PostgreSQL (audit logs only)

---

## 3️⃣ IndexeurSémantique Service

### 📌 Overview
**Port:** 8003  
**Purpose:** Semantic document indexing and vector search  
**Status:** ✅ Operational

### 🎯 Core Responsibilities
- Generate medical domain embeddings
- Build and maintain FAISS vector index
- Perform semantic similarity search
- Support multilingual queries
- Enable contextual document retrieval

### 🔧 Technical Features

#### Embedding Models
- **Primary:** `sentence-transformers/all-MiniLM-L6-v2`
  - 384-dimensional vectors
  - Fast inference (~50ms per document)
  - Good for general medical text
  
- **Medical-Specific:** `dmis-lab/biobert-base-cased-v1.2`
  - Clinical domain fine-tuned
  - Better for specialized terminology
  
#### Vector Database (FAISS)
- **Index Type:** IVF (Inverted File Index)
- **Distance Metric:** Cosine similarity
- **Optimization:** GPU acceleration (if available)
- **Persistence:** Index saved to disk

#### Chunking Strategy
- **Method:** Sliding window with overlap
- **Chunk Size:** 512 tokens
- **Overlap:** 50 tokens
- Preserves context across chunk boundaries

### 🌐 API Endpoints

#### 1. Index Document
```http
POST /api/v1/search/index
Content-Type: application/json

{
  "document_id": "uuid",
  "text": "Patient presented with acute chest pain...",
  "metadata": {
    "patient_id": "PAT001",
    "document_type": "clinical_note"
  }
}

Response:
{
  "document_id": "uuid",
  "chunks_indexed": 5,
  "vector_ids": ["v1", "v2", "v3", "v4", "v5"],
  "status": "indexed"
}
```

#### 2. Semantic Search
```http
POST /api/v1/search/semantic
Content-Type: application/json

{
  "query": "diabetes management with insulin",
  "top_k": 10,
  "filters": {
    "patient_id": "PAT001"
  }
}

Response:
{
  "results": [
    {
      "document_id": "uuid",
      "chunk_text": "Patient's diabetes is well-controlled with insulin...",
      "similarity_score": 0.87,
      "metadata": {...}
    }
  ],
  "total_found": 10,
  "query_time_ms": 45
}
```

#### 3. Get Index Statistics
```http
GET /api/v1/search/stats

Response:
{
  "total_documents": 1247,
  "total_vectors": 6235,
  "index_size_mb": 24.5,
  "last_updated": "2025-12-20T18:30:00"
}
```

### 📊 Performance Metrics
- Embedding Generation: ~50ms per document
- Indexing: ~100ms per document
- Search: <500ms for top-10 results
- Batch Processing: 100 documents/minute

### 🗄️ Database Schema
```sql
Table: document_vectors
- id: UUID (PK)
- document_id: UUID (FK)
- chunk_id: VARCHAR(100)
- chunk_text: TEXT
- vector_id: VARCHAR(100)
- metadata: JSONB
- created_at: TIMESTAMP
```

### 🔗 Integration Points
- **Input:** RabbitMQ queue `document_anonymized`
- **Output:** RabbitMQ queue `document_indexed`
- **Storage:** FAISS index files + PostgreSQL metadata

---

## 4️⃣ LLM QA Module

### 📌 Overview
**Port:** 8004  
**Purpose:** AI-powered question answering with RAG (Retrieval-Augmented Generation)  
**Status:** ✅ Operational

### 🎯 Core Responsibilities
- Answer medical questions using LLMs
- Retrieve relevant context from vector database
- Generate responses with source citations
- Track conversation history
- Provide confidence scores

### 🔧 Technical Features

#### Supported LLM Providers
1. **OpenAI** (GPT-4, GPT-3.5-turbo)
   - Best quality
   - Fastest responses (~2-5s)
   - Requires API key
   
2. **Anthropic** (Claude)
   - Strong reasoning
   - Large context windows
   
3. **Local Models** (via Ollama/LlamaCpp)
   - Llama 2 (7B, 13B, 70B)
   - Mistral 7B
   - BioGPT
   - No external API needed
   - GPU recommended

#### RAG Pipeline
```
1. Question Analysis → 2. Vector Search → 3. Context Ranking
                                              ↓
                                    4. Prompt Construction
                                              ↓
                                      5. LLM Generation
                                              ↓
                                    6. Citation Extraction
```

#### Prompt Engineering
- **System Prompt:** Medical expert persona
- **Context Injection:** Top-5 relevant chunks
- **Citation Requirements:** Source document references
- **Guardrails:** "I don't know" for low-confidence answers

### 🌐 API Endpoints

#### 1. Ask Question
```http
POST /api/v1/qa/ask
Content-Type: application/json

{
  "question": "What is the recommended dosage of metformin for type 2 diabetes?",
  "patient_id": "PAT001",
  "session_id": "SESSION123",
  "top_k_context": 5
}

Response:
{
  "answer": "Based on the clinical guidelines, the initial recommended dosage of metformin for type 2 diabetes is 500mg twice daily with meals, gradually increasing to a maximum of 2000-2500mg per day...",
  "sources": [
    {
      "document_id": "uuid",
      "document_name": "Clinical_Guidelines_2024.pdf",
      "relevance_score": 0.92,
      "excerpt": "Metformin 500mg BID..."
    }
  ],
  "confidence": 0.89,
  "tokens_used": 450,
  "response_time_ms": 3200
}
```

#### 2. Get Conversation History
```http
GET /api/v1/qa/sessions/{session_id}

Response:
{
  "session_id": "SESSION123",
  "messages": [
    {
      "role": "user",
      "content": "What is metformin used for?",
      "timestamp": "2025-12-20T19:00:00"
    },
    {
      "role": "assistant",
      "content": "Metformin is primarily used...",
      "timestamp": "2025-12-20T19:00:03"
    }
  ]
}
```

#### 3. Clear Session
```http
DELETE /api/v1/qa/sessions/{session_id}
```

### 📊 Performance Metrics
- Context Retrieval: ~200ms
- LLM Response (OpenAI GPT-4): ~2-5 seconds
- LLM Response (Local Llama 2 7B): ~5-15 seconds
- Total Latency: <10 seconds for complex queries

### 🗄️ Database Schema
```sql
Table: qa_sessions
- id: UUID (PK)
- session_id: VARCHAR(100)
- user_id: VARCHAR(100)
- created_at: TIMESTAMP

Table: qa_messages
- id: UUID (PK)
- session_id: UUID (FK)
- role: VARCHAR(20) -- 'user' or 'assistant'
- content: TEXT
- sources: JSONB
- tokens_used: INTEGER
- created_at: TIMESTAMP
```

### 🔗 Integration Points
- **Input:** HTTP API requests
- **Dependencies:** IndexeurSémantique (for context retrieval)
- **Storage:** PostgreSQL (conversation history)

---

## 5️⃣ SyntheseComparative Service

### 📌 Overview
**Port:** 8005  
**Purpose:** Patient summary generation and comparative analysis  
**Status:** ✅ Operational

### 🎯 Core Responsibilities
- Generate patient summaries from multiple documents
- Compare patient data across time periods
- Identify trends and changes
- Create medical timelines
- Support differential diagnosis

### 🔧 Technical Features

#### Summary Types
1. **Comprehensive Summary**
   - All documents aggregated
   - Chronological organization
   - Key findings highlighted
   
2. **Problem-Focused Summary**
   - Filter by diagnosis/condition
   - Related medications and procedures
   - Outcome tracking
   
3. **Timeline View**
   - Events sorted chronologically
   - Visual representation ready
   - Milestone markers

#### Comparative Analysis Features
- **Temporal Comparison:** Before/after treatment
- **Multi-Patient Comparison:** Similar cases
- **Lab Value Trends:** Graphable data points
- **Medication Changes:** Start/stop/dosage adjustments

### 🌐 API Endpoints

#### 1. Generate Patient Summary
```http
POST /api/v1/synthesis/summary
Content-Type: application/json

{
  "patient_id": "PAT001",
  "summary_type": "comprehensive",
  "date_from": "2024-01-01",
  "date_to": "2025-12-20"
}

Response:
{
  "patient_id": "PAT001",
  "summary": {
    "demographics": {...},
    "diagnoses": ["Type 2 Diabetes", "Hypertension"],
    "medications": ["Metformin 1000mg BID", "Lisinopril 10mg QD"],
    "recent_visits": [...],
    "key_findings": [...]
  },
  "document_count": 15,
  "generated_at": "2025-12-20T19:00:00"
}
```

#### 2. Compare Patients
```http
POST /api/v1/synthesis/compare
Content-Type: application/json

{
  "patient_ids": ["PAT001", "PAT002"],
  "comparison_fields": ["age", "diagnoses", "medications"]
}

Response:
{
  "comparison": {
    "similarities": [...],
    "differences": [...],
    "recommendations": [...]
  }
}
```

#### 3. Generate Timeline
```http
GET /api/v1/synthesis/timeline/{patient_id}

Response:
{
  "events": [
    {
      "date": "2024-06-15",
      "type": "diagnosis",
      "description": "Diagnosed with Type 2 Diabetes"
    },
    {
      "date": "2024-06-20",
      "type": "medication_start",
      "description": "Started Metformin 500mg BID"
    }
  ]
}
```

### 📊 Performance Metrics
- Summary Generation: ~1-3 seconds
- Comparative Analysis: ~2-5 seconds
- Timeline Creation: ~500ms

### 🔗 Integration Points
- **Input:** HTTP API requests
- **Dependencies:** DocIngestor (for document data)
- **Storage:** PostgreSQL (cached summaries)

---

## 6️⃣ AuditLogger Service

### 📌 Overview
**Port:** 8006  
**Purpose:** Comprehensive audit logging for HIPAA/GDPR compliance  
**Status:** ✅ Operational

### 🎯 Core Responsibilities
- Log all system access and operations
- Track data modifications
- Record user actions
- Enable compliance reporting
- Support forensic investigations

### 🔧 Technical Features

#### Logged Events
- 📄 **Document Access:** Who viewed what, when
- ✏️ **Data Modifications:** Creates, updates, deletes
- 🔍 **Search Queries:** What was searched, results
- 💬 **QA Interactions:** Questions asked, answers provided
- 🔐 **Authentication:** Logins, logouts, failed attempts
- 🛡️ **Anonymization:** What was anonymized, strategy used
- ⚠️ **Security Events:** Suspicious activity, rate limiting

#### Audit Trail Requirements
- **Immutability:** Logs cannot be modified
- **Completeness:** All actions logged
- **Attribution:** User/system identification
- **Timestamp:** UTC with millisecond precision
- **Context:** IP address, user agent, session ID

### 🌐 API Endpoints

#### 1. Create Audit Log
```http
POST /api/v1/audit/log
Content-Type: application/json

{
  "event_type": "document_access",
  "user_id": "USER123",
  "resource_id": "DOC456",
  "action": "view",
  "ip_address": "192.168.1.100",
  "details": {
    "document_type": "clinical_note",
    "patient_id": "PAT001"
  }
}

Response:
{
  "log_id": "uuid",
  "timestamp": "2025-12-20T19:00:00.123Z",
  "status": "logged"
}
```

#### 2. Query Audit Logs
```http
GET /api/v1/audit/logs?user_id=USER123&from=2025-12-01&to=2025-12-20

Response:
{
  "logs": [
    {
      "log_id": "uuid",
      "event_type": "document_access",
      "timestamp": "2025-12-20T19:00:00.123Z",
      "user_id": "USER123",
      "action": "view",
      "resource_id": "DOC456"
    }
  ],
  "total": 247,
  "page": 1
}
```

#### 3. Generate Compliance Report
```http
GET /api/v1/audit/report?type=hipaa&month=2025-12

Response:
{
  "report_type": "HIPAA Compliance",
  "period": "December 2025",
  "total_accesses": 1523,
  "unique_users": 47,
  "documents_accessed": 892,
  "anomalies": 3,
  "report_url": "/reports/hipaa_2025_12.pdf"
}
```

### 📊 Performance Metrics
- Log Write: <10ms
- Log Query: <200ms (with indexes)
- Report Generation: ~5-10 seconds
- Storage: ~1KB per log entry

### 🗄️ Database Schema
```sql
Table: audit_logs
- id: UUID (PK)
- event_type: VARCHAR(100)
- user_id: VARCHAR(100)
- resource_id: VARCHAR(100)
- action: VARCHAR(50)
- ip_address: INET
- user_agent: TEXT
- details: JSONB
- created_at: TIMESTAMP (indexed)

-- Indexes for fast querying
CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at);
CREATE INDEX idx_audit_resource ON audit_logs(resource_id, created_at);
CREATE INDEX idx_audit_event ON audit_logs(event_type, created_at);
```

### 🔗 Integration Points
- **Input:** All other services send audit events
- **Storage:** PostgreSQL (append-only table)
- **Retention:** Configurable (default: 7 years for HIPAA)

---

## 7️⃣ API Gateway

### 📌 Overview
**Port:** 8000  
**Purpose:** Single entry point for all client requests  
**Status:** ✅ Operational

### 🎯 Core Responsibilities
- Route requests to appropriate microservices
- Load balancing across service instances
- Authentication and authorization
- Rate limiting
- Request/response transformation
- Centralized error handling

### 🔧 Technical Features

#### Routing Configuration
```python
Routes:
/api/v1/documents/*     → DocIngestor (8001)
/api/v1/anonymization/* → DeID (8002)
/api/v1/search/*        → IndexeurSémantique (8003)
/api/v1/qa/*            → LLM QA Module (8004)
/api/v1/synthesis/*     → SyntheseComparative (8005)
/api/v1/audit/*         → AuditLogger (8006)
```

#### Security Features
- **JWT Authentication:** Bearer token validation
- **CORS:** Configurable origins
- **Rate Limiting:** Per-user/IP quotas
- **Request Validation:** Input sanitization
- **Response Filtering:** Sensitive data redaction

#### Resilience Patterns
- **Circuit Breaker:** Prevent cascade failures
- **Retry Logic:** Automatic retries with exponential backoff
- **Timeout Management:** Per-service timeout configs
- **Fallback Responses:** Graceful degradation

### 🌐 Unified API

All client applications interact exclusively with the API Gateway on port **8000**.

### 📊 Performance Metrics
- Routing Overhead: <5ms
- Average Response Time: 50-500ms (depends on downstream)
- Max Throughput: 1000 requests/second
- Uptime SLA: 99.9%

---

## 🔄 Data Flow Example

### Complete Document Processing Flow

```
1. User uploads PDF document
   ↓
2. API Gateway → DocIngestor (8001)
   ↓
3. DocIngestor:
   - Parses PDF
   - Extracts text
   - Stores in database
   - Publishes to RabbitMQ: "document_uploaded"
   ↓
4. DeID Service (8002) consumes event:
   - Detects PII
   - Anonymizes using "synthesize" strategy
   - Publishes to RabbitMQ: "document_anonymized"
   ↓
5. IndexeurSémantique (8003) consumes event:
   - Generates embeddings
   - Indexes in FAISS
   - Publishes to RabbitMQ: "document_indexed"
   ↓
6. User asks question via QA Module (8004):
   - Retrieves context from IndexeurSémantique
   - Generates response with LLM
   - Returns answer with citations
   ↓
7. All actions logged by AuditLogger (8006)
```

---

## 🛠️ Technology Stack Summary

### Backend Services
| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL 15 |
| Message Queue | RabbitMQ |
| Vector DB | FAISS |
| NLP | spaCy, Presidio |
| Embeddings | SentenceTransformers |
| LLM | OpenAI GPT-4, Llama 2, Mistral |
| OCR | Tesseract |
| Logging | structlog |
| Containerization | Docker |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 18 + TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| Authentication | Auth0 |
| Charts | Chart.js |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Orchestration | Docker Compose / Kubernetes |
| API Gateway | Custom FastAPI |
| Monitoring | Prometheus + Grafana |
| Logging | ELK Stack |
| Reverse Proxy | Nginx |

---

## 📊 Port Allocation

| Service | Port | Protocol |
|---------|------|----------|
| API Gateway | 8000 | HTTP |
| DocIngestor | 8001 | HTTP |
| DeID | 8002 | HTTP |
| IndexeurSémantique | 8003 | HTTP |
| LLM QA Module | 8004 | HTTP |
| SyntheseComparative | 8005 | HTTP |
| AuditLogger | 8006 | HTTP |
| RabbitMQ | 5672 | AMQP |
| RabbitMQ Management | 15672 | HTTP |
| PostgreSQL | 5432 | PostgreSQL |
| Frontend | 3000 | HTTP |
| Grafana | 3001 | HTTP |

---

## 🔒 Security \u0026 Compliance Features

### HIPAA Compliance
- ✅ Complete audit trails
- ✅ PII anonymization
- ✅ Encrypted data at rest and in transit
- ✅ Access control and authentication
- ✅ 7-year log retention

### GDPR Compliance
- ✅ Right to erasure (document deletion)
- ✅ Data portability (export APIs)
- ✅ Consent tracking
- ✅ Data minimization
- ✅ Privacy by design

---

## 🚀 Deployment

### Development
```bash
docker-compose -f docker-compose-dev.yml up -d
```

### Production
```bash
docker-compose up -d
```

### Individual Service
```bash
docker-compose up -d doc-ingestor
```

---

## 📈 Scalability Considerations

### Horizontal Scaling
- All services are stateless (except databases)
- Can run multiple instances behind load balancer
- RabbitMQ supports distributed queuing

### Performance Optimization
- Database connection pooling
- FAISS GPU acceleration
- LLM response caching
- Batch processing for large uploads

---

## 🧪 Testing

Each service includes:
- Unit tests (pytest)
- Integration tests
- API endpoint tests
- Load testing scripts

---

## 📚 API Documentation

Each service provides auto-generated Swagger documentation:
- DocIngestor: http://localhost:8001/docs
- DeID: http://localhost:8002/docs
- IndexeurSémantique: http://localhost:8003/docs
- LLM QA Module: http://localhost:8004/docs
- SyntheseComparative: http://localhost:8005/docs
- AuditLogger: http://localhost:8006/docs
- API Gateway: http://localhost:8000/docs

---

## 👥 Development Team

- **Pr. Oumayma OUEDRHIRI** - O.ouedrhiri@emsi.ma
- **Pr. Hiba TABBAA** - H.Tabbaa@emsi.ma
- **Pr. Mohamed LACHGAR** - lachgar.m@gmail.com

---

## 📄 License

Apache 2.0

---

## ⚠️ Medical Disclaimer

This system is designed to **assist healthcare professionals**. It should **not be used as the sole basis for medical decisions**. Always verify AI-generated information with clinical expertise and judgment.

---

*MedBot Intelligence © 2025 - Transforming Clinical Data into Actionable Insights*
