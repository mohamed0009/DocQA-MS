# Jenkins CI/CD Quick Reference

## 🚀 Quick Start

```bash
# 1. Install Jenkins (Docker method)
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v ~/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# 2. Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 3. Access Jenkins at http://localhost:8080
```

## 📋 Pipeline Stages

| Stage | Description | Runs On |
|-------|-------------|---------|
| Checkout | Clone repository | All branches |
| Environment Setup | Validate Docker, Python, Node | All branches |
| Dependency Installation | Install packages (parallel) | All branches |
| Code Quality & Linting | Run flake8, build checks | All branches |
| Run Tests | Pytest for ml-predictor & indexeur | All branches |
| Build Docker Images | Build all service images | All branches |
| Security Scan | Trivy vulnerability scan | All branches |
| Integration Tests | Full stack testing | main/develop |
| Push to Registry | Push Docker images | main/develop (if enabled) |
| Deploy | Deploy to environment | main (if enabled) |

## 🔧 Common Commands

### Local Pipeline Validation
```bash
# Validate Jenkinsfile syntax (requires Jenkins CLI)
java -jar jenkins-cli.jar declarative-linter < Jenkinsfile

# Test Docker builds locally
docker-compose build --parallel

# Run tests locally
cd services/ml-predictor && python -m pytest tests/
cd services/indexeur-semantique && python -m pytest tests/
```

### Jenkins CLI Operations
```bash
# Download Jenkins CLI
wget http://localhost:8080/jnlpJars/jenkins-cli.jar

# List jobs
java -jar jenkins-cli.jar -s http://localhost:8080/ list-jobs

# Build job
java -jar jenkins-cli.jar -s http://localhost:8080/ build MedBot-Intelligence-CI

# Get build status
java -jar jenkins-cli.jar -s http://localhost:8080/ get-build MedBot-Intelligence-CI 1
```

## 🔑 Required Credentials

| Credential ID | Type | Purpose |
|---------------|------|---------|
| `docker-hub-credentials` | Username/Password | Docker Hub authentication |
| `docker-registry-url` | Secret text | Docker registry URL |
| `git-credentials` | SSH/Username | Git repository access |

## ⚙️ Key Environment Variables

```bash
# Must configure in Jenkins
PROJECT_NAME=medbot-intelligence
PUSH_TO_REGISTRY=false         # Set true to push images
DEPLOY_ENABLED=false            # Set true for auto-deploy

# Optional
NOTIFICATION_EMAIL=team@example.com
DOCKER_REGISTRY=docker.io
```

## 📊 Build Status Indicators

| Icon | Status | Meaning |
|------|--------|---------|
| ✅ | Success | All stages passed |
| ❌ | Failure | Build/test failed |
| ⚠️ | Unstable | Tests passed with warnings |
| 🔵 | Running | Build in progress |
| ⏭️ | Skipped | Stage not executed (condition not met) |

## 🐛 Quick Troubleshooting

### Build Fails at Tests
```bash
# Check if pytest is installed
pip3 install pytest pytest-cov

# Run tests locally to debug
cd services/ml-predictor
python -m pytest tests/ -v
```

### Docker Build Fails
```bash
# Check Docker is accessible
docker ps

# Verify docker-compose works
docker-compose config

# Check disk space
df -h
```

### Permission Errors
```bash
# Add Jenkins user to docker group (Linux)
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

## 📈 Monitoring

### Check Build Health
- Dashboard: `http://localhost:8080/job/MedBot-Intelligence-CI/`
- Blue Ocean: `http://localhost:8080/blue/organizations/jenkins/MedBot-Intelligence-CI/`
- Console Output: Click on build number → Console Output

### View Test Reports
- Navigate to build → Test Result
- Code Coverage: Build → Coverage Report
- HTML Reports: Build → Coverage Report (for each service)

## 🔗 Useful Links

- [Full Setup Guide](JENKINS_SETUP.md)
- [Environment Config](`.jenkins/ENV_CONFIG.md`)
- [Helper Functions](`.jenkins/helpers.groovy`)
- [Jenkins Docs](https://www.jenkins.io/doc/)

## 💡 Tips

1. **First Build**: Always expect first build to take longer (downloading dependencies)
2. **Parallel Builds**: Disabled by default to avoid resource issues
3. **Test Failures**: Check test reports for detailed error messages
4. **Docker Cache**: Enable layer caching to speed up builds
5. **Notifications**: Configure email/Slack for failure alerts only

---

**Need help?** Check [JENKINS_SETUP.md](JENKINS_SETUP.md#troubleshooting) for detailed troubleshooting.
