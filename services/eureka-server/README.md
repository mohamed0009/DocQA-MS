# Eureka Server

Netflix Eureka Server for MedBot Intelligence microservices discovery.

## Features

- Service registration and discovery
- Health monitoring
- Load balancing support
- Web dashboard at http://localhost:8761

## Configuration

The server runs in **standalone mode** and does not register with itself.

Key settings:
- Port: 8761
- Self-preservation: Disabled (development mode)
- Eviction interval: 10 seconds
- Response cache update: 5 seconds

## Endpoints

- Dashboard: http://localhost:8761
- Health: http://localhost:8761/actuator/health
- Eureka Apps: http://localhost:8761/eureka/apps

## Running Locally (Development)

```bash
mvn spring-boot:run
```

## Running with Docker

```bash
docker build -t medbot-eureka-server .
docker run -p 8761:8761 medbot-eureka-server
```

## Integration

Python microservices register using `py-eureka-client`:

```python
import py_eureka_client.eureka_client as eureka_client

eureka_client.init(
    eureka_server="http://localhost:8761/eureka",
    app_name="my-service",
    instance_port=8000,
)
```
