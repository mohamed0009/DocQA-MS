#!/bin/bash
# ===========================================
# Jenkins Pipeline Health Check Script
# ===========================================
# This script validates that the Jenkins pipeline
# can successfully build and test the project locally

set -e  # Exit on any error

echo "🔍 Jenkins Pipeline Health Check"
echo "================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 is installed${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ $1 is not installed${NC}"
        ((FAILED++))
        return 1
    fi
}

check_version() {
    echo -e "${YELLOW}ℹ️  $1 version:${NC}"
    $2
    echo ""
}

# 1. Check Prerequisites
echo "1️⃣  Checking Prerequisites..."
echo "----------------------------"
check_command docker
check_command docker-compose
check_command python3
check_command pip3
check_command node
check_command npm
check_command git
echo ""

# 2. Check Docker Access
echo "2️⃣  Checking Docker Access..."
echo "----------------------------"
if docker ps &> /dev/null; then
    echo -e "${GREEN}✅ Docker daemon is running${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Cannot access Docker daemon${NC}"
    echo "   Make sure Docker is running and you have permissions"
    ((FAILED++))
fi
echo ""

# 3. Validate Jenkinsfile
echo "3️⃣  Validating Jenkinsfile..."
echo "----------------------------"
if [ -f "Jenkinsfile" ]; then
    echo -e "${GREEN}✅ Jenkinsfile exists${NC}"
    ((PASSED++))
    
    # Basic syntax check (grep for required sections)
    if grep -q "pipeline {" Jenkinsfile && \
       grep -q "stages {" Jenkinsfile && \
       grep -q "post {" Jenkinsfile; then
        echo -e "${GREEN}✅ Jenkinsfile has valid structure${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ Jenkinsfile structure seems invalid${NC}"
        ((FAILED++))
    fi
else
    echo -e "${RED}❌ Jenkinsfile not found${NC}"
    ((FAILED++))
fi
echo ""

# 4. Check Service Dependencies
echo "4️⃣  Checking Service Dependencies..."
echo "------------------------------------"

SERVICES=("api-gateway" "doc-ingestor" "deid" "indexeur-semantique" 
          "llm-qa-module" "synthese-comparative" "audit-logger" "ml-predictor")

for service in "${SERVICES[@]}"; do
    if [ -f "services/$service/requirements.txt" ]; then
        echo -e "${GREEN}✅ services/$service/requirements.txt${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ services/$service/requirements.txt missing${NC}"
        ((FAILED++))
    fi
done
echo ""

# 5. Check Frontend Dependencies
echo "5️⃣  Checking Frontend Dependencies..."
echo "-------------------------------------"
if [ -f "interface-clinique/package.json" ]; then
    echo -e "${GREEN}✅ interface-clinique/package.json exists${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ interface-clinique/package.json missing${NC}"
    ((FAILED++))
fi
echo ""

# 6. Verify Docker Compose Configuration
echo "6️⃣  Verifying Docker Compose..."
echo "-------------------------------"
if docker-compose config &> /dev/null; then
    echo -e "${GREEN}✅ docker-compose.yml is valid${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ docker-compose.yml has errors${NC}"
    ((FAILED++))
fi
echo ""

# 7. Check Test Files
echo "7️⃣  Checking Test Files..."
echo "-------------------------"
if [ -d "services/ml-predictor/tests" ]; then
    echo -e "${GREEN}✅ ml-predictor tests exist${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  ml-predictor tests not found${NC}"
fi

if [ -d "services/indexeur-semantique/tests" ]; then
    echo -e "${GREEN}✅ indexeur-semantique tests exist${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  indexeur-semantique tests not found${NC}"
fi
echo ""

# 8. Simulate Pipeline Stages (Optional - can be slow)
echo "8️⃣  Simulating Pipeline Stages..."
echo "---------------------------------"
read -p "Run full pipeline simulation? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Testing Docker build..."
    if docker-compose build --no-cache api-gateway &> /dev/null; then
        echo -e "${GREEN}✅ Docker build successful (api-gateway)${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ Docker build failed${NC}"
        ((FAILED++))
    fi
    
    echo "🧪 Running ml-predictor tests..."
    if [ -d "services/ml-predictor/tests" ]; then
        cd services/ml-predictor
        if python3 -m pytest tests/ &> /dev/null; then
            echo -e "${GREEN}✅ ml-predictor tests passed${NC}"
            ((PASSED++))
        else
            echo -e "${RED}❌ ml-predictor tests failed${NC}"
            ((FAILED++))
        fi
        cd ../..
    fi
else
    echo "⏭️  Skipping simulation"
fi
echo ""

# Summary
echo "================================="
echo "📊 Health Check Summary"
echo "================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Jenkins pipeline should work correctly.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please fix the issues above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Install missing tools (docker, python3, node, etc.)"
    echo "  - Ensure Docker daemon is running"
    echo "  - Check file paths are correct"
    echo "  - Review docker-compose.yml syntax"
    exit 1
fi
