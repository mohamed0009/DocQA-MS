# Eureka Service Discovery Integration

## ✅ Completed Integration

### Infrastructure
- **Eureka Server**: Spring Boot service running on port 8761
- **Dashboard**: http://localhost:8761
- **Health Check**: http://localhost:8761/actuator/health

### Services Integrated
1. ✅ **API Gateway** - Eureka client with service discovery
2. ✅ **Indexeur Semantique** - Registered as `INDEXEUR-SEMANTIQUE`

### Shared Library
- **Location**: `services/shared/eureka_client.py`
- **Features**: Registration, deregistration, service discovery, load balancing

## 🚀 Quick Start

### 1. Build and Start Eureka Server

```bash
cd c:\Users\HP\Desktop\MedBot-Intelligence
docker-compose up -d eureka-server
```

Wait 30-40 seconds for Eureka to start, then verify:
```bash
curl http://localhost:8761/actuator/health
```

Expected response: `{"status":"UP"}`

### 2. Access Eureka Dashboard

Open your browser to: **http://localhost:8761**

You should see the Eureka dashboard with "Instances currently registered with Eureka" section.

### 3. Start Services with Eureka

```bash
# Start all services
docker-compose up -d

# Or start individually
docker-compose up -d api-gateway indexeur-semantique
```

### 4. Verify Service Registration

Check the Eureka dashboard or use the API:
```bash
# Get all registered applications
curl http://localhost:8761/eureka/apps

# Should show API-GATEWAY and INDEXEUR-SEMANTIQUE
```

## 🧪 Testing Service Discovery

### Test 1: API Gateway Discovery

```powershell
# Search endpoint (uses service discovery to find indexeur-semantique)
curl "http://localhost:8000/api/v1/search/?q=diabetes&limit=5"
```

The API Gateway will:
1. Use Eureka to discover `INDEXEUR-SEMANTIQUE` service
2. Get the service URL dynamically
3. Forward the request
4. Return results

### Test 2: Check API Gateway Health with Service Status

```powershell
curl http://localhost:8000/api/v1/health
```

This should show the health of downstream services discovered via Eureka.

### Test 3: Direct Service Registration Check

```powershell
# Check what instances are registered
$response = Invoke-RestMethod -Uri "http://localhost:8761/eureka/apps" -Method Get
$response.applications.application | ForEach-Object { Write-Host $_.name }
```

## 🔧 Configuration

### Environment Variables (Docker)

All services support these Eureka variables:

```yaml
environment:
  - EUREKA_SERVER_URL=http://eureka-server:8761/eureka
  - ENABLE_EUREKA=true
  - INSTANCE_HOST=service-name
```

### Local Development (Without Eureka)

To disable Eureka and use fallback URLs:

```bash
export ENABLE_EUREKA=false
```

Services will automatically fall back to configured URLs in `config.py`.

## 📊 Eureka Dashboard Guide

**URL**: http://localhost:8761

**What to look for**:
- **Instances currently registered with Eureka**: Shows all registered services
- **General Info**: Eureka server status
- **Instance Info**: Hostname, IP, status, metadata for each service

**Status Colors**:
- 🟢 **UP**: Service is healthy and registered
- 🔴 **DOWN**: Service is not responding
- 🟡 **STARTING**: Service is initializing

## 🐛 Troubleshooting

### Service Not Appearing in Eureka

**Check logs**:
```bash
docker-compose logs api-gateway | Select-String -Pattern "Eureka"
docker-compose logs indexeur-semantique | Select-String -Pattern "Eureka"
```

**Look for**:
- ✓ "registered with Eureka" success message
- ❌ "Failed to register" error messages

**Common issues**:
1. Eureka Server not fully started (wait 40 seconds)
2. Network connectivity issues
3. Incorrect `EUREKA_SERVER_URL` configuration

### Service Discovery Failing

**Verify Eureka is accessible**:
```bash
curl http://localhost:8761/actuator/health
```

**Check service can reach Eureka** (from within container):
```bash
docker exec docqa-api-gateway curl http://eureka-server:8761/actuator/health
```

### Fallback to Config URLs

Services automatically fall back to configured URLs if:
- Eureka is unavailable
- Service not found in registry
- `ENABLE_EUREKA=false`

## 🔄 Service Lifecycle

### Startup
1. Service starts
2. Connects to Eureka Server
3. Registers with instance info (host, port, health URL)
4. Sends heartbeat every 30 seconds

### Running
- Heartbeat maintains registration
- Other services discover via Eureka
- Load balancing for multiple instances

### Shutdown
1. Service receives shutdown signal
2. Deregisters from Eureka
3. No longer appears in registry
4. Other services stop routing to it

## 📝 Next Steps (Manual)

To complete integration for remaining services, add to each service's:

### 1. `requirements.txt`
```txt
py-eureka-client>=0.11.0
```

### 2. `app/config.py`
```python
EUREKA_SERVER_URL: str = os.getenv("EUREKA_SERVER_URL", "http://localhost:8761/eureka")
ENABLE_EUREKA: bool = os.getenv("ENABLE_EUREKA", "true").lower() == "true"
INSTANCE_HOST: str = os.getenv("INSTANCE_HOST", "localhost")
```

### 3. `app/main.py` (in lifespan or startup event)
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../shared'))

from eureka_client import EurekaServiceRegistry

# In startup:
eureka_registry = EurekaServiceRegistry(
    service_name="SERVICE-NAME",
    service_port=8000,
    eureka_server_url=settings.EUREKA_SERVER_URL,
    instance_host=settings.INSTANCE_HOST
)
eureka_registry.register()

# In shutdown:
eureka_registry.deregister()
```

### 4. `docker-compose.yml`
```yaml
environment:
  - EUREKA_SERVER_URL=http://eureka-server:8761/eureka
  - ENABLE_EUREKA=true
  - INSTANCE_HOST=service-name
volumes:
  - ./services/shared:/app/shared:ro
depends_on:
  eureka-server:
    condition: service_healthy
```

## 🎯 Benefits

✅ **Dynamic Discovery**: No hardcoded service URLs  
✅ **Load Balancing**: Distribute across multiple instances  
✅ **Health Monitoring**: Automatic detection of unhealthy services  
✅ **Scalability**: Easy horizontal scaling  
✅ **Resilience**: Automatic failover to healthy instances  
✅ **Cloud-Ready**: Standard industry pattern for microservices  

## 📚 References

- **Netflix Eureka**: https://github.com/Netflix/eureka
- **py-eureka-client**: https://github.com/keijack/python-eureka-client
- **Spring Cloud Eureka**: https://spring.io/projects/spring-cloud-netflix
