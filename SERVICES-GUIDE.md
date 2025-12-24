# MedBot Intelligence - Services Quick Reference

## 🚀 Running Services Locally

All services are now running on your local machine without Docker!

### Service Endpoints

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| **doc-ingestor** | 8001 | http://localhost:8001 | Document upload and processing |
| **deid** | 8002 | http://localhost:8002 | De-identification service |
| **indexeur-semantique** | 8003 | http://localhost:8003 | Semantic search and indexing |
| **llm-qa-module** | 8004 | http://localhost:8004 | AI Q&A service |
| **synthese-comparative** | 8005 | http://localhost:8005 | Patient synthesis and comparison |
| **audit-logger** | 8006 | http://localhost:8006 | Audit logging service |

### Frontend
- **URL**: http://localhost:3000
- **Status**: Running (Next.js dev server)

## 📝 How to Use

### Start All Services
```powershell
.\start-all-services.ps1
```

This will open 6 separate PowerShell windows, one for each service.

### Stop Services
- Press `Ctrl+C` in each service window
- Or close the PowerShell windows

### Check Service Health
Visit the API docs for each service:
- http://localhost:8001/docs (Doc Ingestor)
- http://localhost:8002/docs (De-ID)
- http://localhost:8003/docs (Search)
- http://localhost:8004/docs (Q&A)
- http://localhost:8005/docs (Synthesis)
- http://localhost:8006/docs (Audit)

## 🔧 Troubleshooting

### Service Won't Start
1. Check if Python is installed: `python --version`
2. Install dependencies: `cd services/[service-name]` then `pip install -r requirements.txt`
3. Check if port is already in use

### Frontend Shows Network Error
1. Wait 10-15 seconds for all services to fully start
2. Refresh the browser
3. Check browser console for specific error messages

### Database Connection Issues
Some services may need PostgreSQL or other databases running. Check the `.env` file for database configuration.

## 📦 Dependencies

Each service requires:
- Python 3.8+
- uvicorn (ASGI server)
- FastAPI
- Service-specific packages (see requirements.txt in each service)

## 🎯 Next Steps

1. ✅ All services are running
2. Open http://localhost:3000 in your browser
3. The dashboard should now load without network errors
4. Try uploading a document or asking a question to test the services

## 💡 Tips

- Keep all service windows open while using the application
- Monitor the service windows for error messages
- Services auto-reload when you make code changes (--reload flag)
- Check the audit logger for system activity
