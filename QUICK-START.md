# DocQA-MS — Quick Start Guide

## 🚀 Getting Started with DocIngestor Service

The **DocIngestor** service is now **100% complete** and ready to test!

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Docker Desktop installed
- ✅ Docker Compose installed
- ✅ At least 8GB RAM available
- ✅ At least 10GB disk space

---

## ⚙️ Setup Instructions

### 1. Create Environment File

```powershell
# Navigate to project directory
cd "C:\Users\HP\Desktop\PROJET lchegar"

# Copy environment template
cp .env.example .env
```

### 2. Edit `.env` File (Optional)

The default values work for local development. You can customize:
- Database passwords
- RabbitMQ credentials  
- Service ports
- Feature flags

### 3. Start Infrastructure Services

```powershell
# Start PostgreSQL, RabbitMQ, and Redis only
docker-compose up -d postgres rabbitmq redis
```

**Wait ~30 seconds** for services to be healthy, then verify:

```powershell
# Check service status
docker-compose ps

# Should show:
# - postgres (healthy)
# - rabbitmq (healthy)
# - redis (healthy)
```

### 4. Start DocIngestor Service

```powershell
# Build and start DocIngestor
docker-compose up --build doc-ingestor
```

---

## 🧪 Testing the Service

### Access the API Documentation

Once the service is running, open your browser:

**Swagger UI**: http://localhost:8001/docs

You'll see all available endpoints:
- `POST /api/v1/documents/upload` - Upload documents
- `GET /api/v1/documents` - List documents
- `GET /api/v1/documents/{id}` - Get specific document
- `PATCH /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document

### Test Document Upload

#### Option 1: Using Swagger UI (Easiest)

1. Go to http://localhost:8001/docs
2. Click on `/api/v1/documents/upload`
3. Click "Try it out"
4. Choose a file (PDF, DOCX, TXT, HL7, or FHIR JSON)
5. Optionally add patient_id, document_type, etc.
6. Click "Execute"

####  Option 2: Using curl

```powershell
# Upload a PDF document
curl -X POST "http://localhost:8001/api/v1/documents/upload" `
  -F "file=@test-document.pdf" `
  -F "patient_id=PAT001" `
  -F "document_type=compte-rendu"
```

#### Option 3: Using Python

```python
import requests

url = "http://localhost:8001/api/v1/documents/upload"

with open("test-document.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "patient_id": "PAT001",
        "document_type": "compte-rendu"
    }
    response = requests.post(url, files=files, data=data)
    print(response.json())
```

### List All Documents

```powershell
# List first 20 documents
curl http://localhost:8001/api/v1/documents

# Filter by patient
curl "http://localhost:8001/api/v1/documents?patient_id=PAT001"

# Pagination
curl "http://localhost:8001/api/v1/documents?page=2&page_size=10"
```

---

## 🔍 Monitoring & Debugging

### View Logs

```powershell
# Follow DocIngestor logs
docker-compose logs -f doc-ingestor

# View last 100 lines
docker-compose logs --tail=100 doc-ingestor
```

### Access RabbitMQ Management UI

**URL**: http://localhost:15672  
**Username**: `docqa_rabbitmq`  
**Password**: `changeme` (or your .env value)

You'll see messages published when documents are processed.

### Access PostgreSQL

```powershell
# Connect to database
docker-compose exec postgres psql -U docqa_admin -d doc_ingestor

# List documents
SELECT id, filename, file_type, status, patient_id, created_at FROM documents;

# Exit
\q
```

---

## 📚 Supported Document Types

| Type | Extension | Features |
|------|-----------|----------|
| **PDF** | `.pdf` | ✅ Native text<br>✅ OCR for scanned<br>✅ Metadata extraction |
| **DOCX** | `.docx` | ✅ Text extraction<br>✅ Table extraction<br>✅ Metadata |
| **HL7** | `.hl7` | ✅ Patient info (PID)<br>✅ Observations (OBX)<br>✅ Notes (NTE) |
| **FHIR** | `.json`, `.xml` | ✅ DocumentReference<br>✅ Patient<br>✅ Observation<br>✅ Bundle |
| **Text** | `.txt` | ✅ Plain text |

---

## 🐛 Troubleshooting

### Problem: Service won't start

**Solution:** Check if ports are already in use
```powershell
# Check port 8001
netstat -ano | findstr :8001
```

### Problem: Database connection error

**Solution:** Ensure PostgreSQL is healthy
```powershell
docker-compose ps postgres
docker-compose logs postgres
```

### Problem: File upload fails

**Check:**
1. File size < 100MB (configurable in `.env`)
2. File extension is allowed (pdf, docx, txt, hl7, json, xml)
3. Sufficient disk space

### Problem: OCR not working

**Solution:** Tesseract is installed in Docker image
```powershell
# Verify Tesseract in container
docker-compose exec doc-ingestor tesseract --version
```

---

## 🔧 Development Mode

For active development with hot-reload:

```powershell
# Edit docker-compose.yml, uncomment volume mount:
# volumes:
#   - ./services/doc-ingestor/app:/app

# Restart service
docker-compose restart doc-ingestor
```

Now code changes will be reflected immediately!

---

##  ✅ Health Check

Verify service health:

```powershell
curl http://localhost:8001/health

# Expected response:
# {"status":"healthy","service":"doc-ingestor"}
```

---

## 📊 What's Working

✅ **Document Upload** - All formats (PDF, DOCX, HL7, FHIR, TXT)  
✅ **Text Extraction** - Multiple strategies with fallback  
✅ **OCR Support** - For scanned PDFs (French + English)  
✅ **Metadata Extraction** - Author, dates, patient info  
✅ **Deduplication** - SHA256 hash checking  
✅ **Database Storage** - PostgreSQL with full indexing  
✅ **RabbitMQ Integration** - Async event publishing  
✅ **REST API** - Full CRUD operations  
✅ **API Documentation** - Auto-generated Swagger UI  
✅ **Validation** - File size, type, extension  
✅ **Error Handling** - Graceful failures with logging  

---

## 🎯 Next Steps

Now that DocIngestor is complete, you can:

1. **Test with sample documents** - Upload various medical documents
2. **Monitor RabbitMQ** - See messages being published
3. **Query the database** - Explore stored documents  
4. **Start next service** - Begin building DeID service

---

## 📞 Need Help?

Check the logs first:
```powershell
docker-compose logs -f doc-ingestor
```

Common solutions:
- Restart services: `docker-compose restart`
- Rebuild images: `docker-compose up --build`
- Check all services: `docker-compose ps`

---

**🎉 Congratulations!** Your first microservice is fully operational!

Next: Let's build the **DeID (De-identification)** service to anonymize medical documents.
