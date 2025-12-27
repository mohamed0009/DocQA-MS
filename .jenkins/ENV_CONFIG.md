# Jenkins CI/CD Configuration Guide

## Environment Variables Reference

Copy these variables to your Jenkins job configuration or global environment settings.

### Docker Registry
```bash
DOCKER_REGISTRY=docker.io  # or your-registry.azurecr.io
DOCKER_CREDENTIALS_ID=docker-hub-credentials  # Jenkins credential ID
PUSH_TO_REGISTRY=false  # Set to true to enable pushing
```

### Deployment
```bash
DEPLOY_ENABLED=false  # Set to true for auto-deployment
DEPLOY_ENVIRONMENT=staging  # or production
```

### Notifications
```bash
NOTIFICATION_EMAIL=team@example.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Testing
```bash
RUN_INTEGRATION_TESTS=true
TEST_TIMEOUT_MINUTES=30
COVERAGE_THRESHOLD=80
```

### Service Health Check URLs
```bash
API_GATEWAY_HEALTH_URL=http://localhost:8000/health
DOC_INGESTOR_HEALTH_URL=http://localhost:8001/health
DEID_HEALTH_URL=http://localhost:8002/health
INDEXEUR_HEALTH_URL=http://localhost:8003/health
LLM_QA_HEALTH_URL=http://localhost:8004/health
SYNTHESE_HEALTH_URL=http://localhost:8005/health
AUDIT_HEALTH_URL=http://localhost:8006/health
ML_PREDICTOR_HEALTH_URL=http://localhost:8007/health
FRONTEND_HEALTH_URL=http://localhost:3000
```

### Security Scanning
```bash
ENABLE_SECURITY_SCAN=true
SECURITY_SCAN_SEVERITY=HIGH,CRITICAL
```

## How to Use

1. **In Jenkins UI:**
   - Go to: Manage Jenkins → Configure System →Global Properties
   - Check "Environment variables"
   - Add each variable

2. **In Jenkinsfile (for job-specific):**
   ```groovy
   environment {
       PUSH_TO_REGISTRY = 'false'
       DEPLOY_ENABLED = 'false'
   }
   ```

3. **Using Credentials:**
   - Go to: Manage Jenkins → Manage Credentials
   - Add credentials with IDs mentioned above
   - Reference them in the pipeline
