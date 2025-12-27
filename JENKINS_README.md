# Jenkins CI/CD Integration

## 📋 Overview

This document provides information about the Jenkins CI/CD pipeline for the MedBot-Intelligence project.

## 🚀 Files Created

The following files have been added to implement Jenkins CI/CD:

### Core Files
- **`Jenkinsfile`** - Main Jenkins pipeline definition with multi-stage build process
- **`.jenkins/helpers.groovy`** - Reusable Groovy functions for pipeline operations
- **`.jenkins/health-check.ps1`** - PowerShell health check script for Windows
- **`.jenkins/health-check.sh`** - Bash health check script for Linux/Mac

### Documentation
- **`JENKINS_SETUP.md`** - Complete setup guide with installation and configuration
- **`.jenkins/QUICK_REFERENCE.md`** - Quick reference for common commands and tasks
- **`.jenkins/ENV_CONFIG.md`** - Environment variables configuration guide

## 📖 Getting Started

### 1. Prerequisites
- Jenkins 2.400+ (LTS recommended)
- Docker 20.10+ and Docker Compose 2.0+
- Git 2.30+
- Python 3.10+
- Node.js 18+

### 2. Quick Setup

#### For Windows (PowerShell)
```powershell
# Run health check
.\.jenkins\health-check.ps1

# If all checks pass, Jenkins is ready to use
```

#### For Linux/Mac (Bash)
```bash
# Make script executable
chmod +x .jenkins/health-check.sh

# Run health check
./.jenkins/health-check.sh
```

### 3. Jenkins Installation

See [JENKINS_SETUP.md](JENKINS_SETUP.md) for detailed installation instructions.

**Quick Docker Install:**
```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v ~/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

Access at: http://localhost:8080

## 🔧 Pipeline Stages

The Jenkins pipeline includes the following stages:

1. **Checkout** - Clone the repository
2. **Environment Setup** - Validate Docker, Python, Node.js
3. **Dependency Installation** - Install packages in parallel
4. **Code Quality & Linting** - Run quality checks
5. **Run Tests** - Execute pytest for services with tests
6. **Build Docker Images** - Build all microservices
7. **Security Scan** - Run Trivy vulnerability scanning
8. **Integration Tests** - Full stack testing (main/develop only)
9. **Push to Registry** - Push images to Docker registry (optional)
10. **Deploy** - Deploy to environment (optional)

## 🧪 Testing

The pipeline runs automated tests for:
- **ml-predictor** - Machine learning service tests
- **indexeur-semantique** - Semantic indexer tests

Test reports and coverage are published after each build.

## 🐳 Docker Integration

All services are containerized and built via the pipeline:
- api-gateway
- doc-ingestor
- deid
- indexeur-semantique
- llm-qa-module
- synthese-comparative
- audit-logger
- ml-predictor
- frontend (Next.js)

## 📊 Monitoring

After setting up Jenkins, you can monitor builds at:
- **Classic UI**: http://localhost:8080/job/MedBot-Intelligence-CI/
- **Blue Ocean**: http://localhost:8080/blue/

## 🔑 Configuration

### Required Credentials (if using registry/deployment)
1. **docker-hub-credentials** - Docker Hub authentication
2. **git-credentials** - Git repository access (if private)

### Environment Variables
Set these in Jenkins global properties:
```
PROJECT_NAME=medbot-intelligence
PUSH_TO_REGISTRY=false
DEPLOY_ENABLED=false
```

See [`.jenkins/ENV_CONFIG.md`](.jenkins/ENV_CONFIG.md) for complete configuration.

## 📚 Documentation

- **Full Setup Guide**: [JENKINS_SETUP.md](JENKINS_SETUP.md)
- **Quick Reference**: [.jenkins/QUICK_REFERENCE.md](.jenkins/QUICK_REFERENCE.md)
- **Environment Config**: [.jenkins/ENV_CONFIG.md](.jenkins/ENV_CONFIG.md)
- **Helper Functions**: [.jenkins/helpers.groovy](.jenkins/helpers.groovy)

## 🆘 Troubleshooting

Common issues and solutions are documented in:
- [JENKINS_SETUP.md - Troubleshooting Section](JENKINS_SETUP.md#troubleshooting)

Quick checks:
```powershell
# Windows - Run health check
.\.jenkins\health-check.ps1

# Verify Docker
docker ps
docker-compose config

# Check Python/Node
python --version
node --version
```

## 🔄 CI/CD Workflow

### For Developers

1. **Push to feature branch**: Build and test only
2. **Push to develop**: Build, test, and integration tests
3. **Push to main**: Build, test, integration tests, and optional deploy

### Manual Build

1. Go to Jenkins: http://localhost:8080
2. Select job: **MedBot-Intelligence-CI**
3. Click **Build Now**
4. Monitor progress in Console Output or Blue Ocean

## 🎯 Best Practices

1. **Test Locally First**: Run health check before pushing
2. **Review Test Reports**: Check coverage and test results
3. **Monitor Build Times**: Optimize slow stages
4. **Enable Notifications**: Configure email/Slack for failures
5. **Keep Jenkins Updated**: Regularly update Jenkins and plugins

## 📞 Support

For detailed help:
- Check [JENKINS_SETUP.md](JENKINS_SETUP.md)
- Review pipeline logs in Jenkins Console Output
- Run health check scripts for diagnostics

---

**Note**: The pipeline is configured for safety by default. Docker registry push and auto-deployment are disabled. Enable them by setting appropriate environment variables after proper configuration.
