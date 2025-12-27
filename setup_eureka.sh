#!/usr/bin/env bash
# Eureka Integration - Quick Setup Script

echo "=========================================="
echo "📋 Eureka Service Discovery Setup"
echo "=========================================="
echo ""

# Check if Docker is running
echo "🔍 Checking Docker..."
docker info > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Build Eureka Server
echo "🏗️  Building Eureka Server..."
docker-compose build eureka-server
if [ $? -ne 0 ]; then
    echo "❌ Failed to build Eureka Server"
    exit 1
fi
echo "✅ Eureka Server built successfully"
echo ""

# Start Eureka Server
echo "🚀 Starting Eureka Server..."
docker-compose up -d eureka-server
echo "⏳ Waiting 40 seconds for Eureka to fully start..."
sleep 40

# Check Eureka health
echo "🏥 Checking Eureka health..."
HEALTH=$(curl -s http://localhost:8761/actuator/health | grep -o '"status":"UP"')
if [ -z "$HEALTH" ]; then
    echo "❌ Eureka Server is not healthy"
    echo "Check logs: docker-compose logs eureka-server"
    exit 1
fi
echo "✅ Eureka Server is UP and healthy"
echo ""

# Start services with Eureka
echo "🚀 Starting services with Eureka integration..."
docker-compose up -d api-gateway indexeur-semantique

echo "⏳ Waiting 30 seconds for services to register..."
sleep 30

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📍 Next Steps:"
echo "   1. Open Eureka Dashboard: http://localhost:8761"
echo "   2. Run tests: python test_eureka_integration.py"
echo "   3. Check API Gateway: http://localhost:8000"
echo ""
echo "🔍 Verify Services:"
echo "   curl http://localhost:8761/eureka/apps"
echo ""
