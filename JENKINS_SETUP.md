# Jenkins Setup Guide for MedBot Intelligence

This guide will help you set up Jenkins CI/CD for the MedBot Intelligence project.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Jenkins Installation](#jenkins-installation)
- [Plugin Installation](#plugin-installation)
- [Credentials Configuration](#credentials-configuration)
- [Pipeline Setup](#pipeline-setup)
- [Environment Configuration](#environment-configuration)
- [Running Your First Build](#running-your-first-build)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Jenkins** 2.400+ (LTS recommended)
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Git** 2.30+
- **Python** 3.10+
- **Node.js** 18+ and **npm** 9+

### Required Jenkins Plugins
Install these from **Manage Jenkins → Manage Plugins**:

#### Essential Plugins
- ✅ **Pipeline** - Core pipeline functionality
- ✅ **Docker Pipeline** - Docker integration
- ✅ **Git Plugin** - Git source control
- ✅ **GitHub Plugin** - GitHub integration
- ✅ **Email Extension** - Email notifications
- ✅ **Workspace Cleanup** - Clean workspace between builds

#### Recommended Plugins
- 📦 **Blue Ocean** - Modern pipeline UI
- 📦 **Pipeline: Stage View** - Visual stage representation
- 📦 **JUnit Plugin** - Test report publishing
- 📦 **HTML Publisher** - Coverage report publishing
- 📦 **Slack Notification** - Slack integration
- 📦 **Timestamper** - Add timestamps to console output
- 📦 **AnsiColor** - Colorize console output

---

## Jenkins Installation

### Option 1: Docker (Recommended for Testing)

```bash
# Create Jenkins home directory
mkdir -p ~/jenkins_home

# Run Jenkins in Docker
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v ~/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(which docker):/usr/bin/docker \
  jenkins/jenkins:lts
```

Access at: **http://localhost:8080**

Get initial admin password:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Option 2: Windows Installation

1. Download Jenkins from: https://www.jenkins.io/download/
2. Run the installer
3. Complete the setup wizard
4. Access at: **http://localhost:8080**

### Option 3: Linux (Ubuntu/Debian)

```bash
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins
sudo systemctl start jenkins
```

---

## Plugin Installation

### via Jenkins UI

1. Navigate to **Manage Jenkins → Manage Plugins**
2. Go to **Available** tab
3. Search and install:
   - Pipeline
   - Docker Pipeline
   - Git Plugin
   - Email Extension
   - Blue Ocean (optional)
4. Check **Restart Jenkins when installation is complete**

### via Jenkins CLI

```bash
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin \
  workflow-aggregator \
  docker-workflow \
  git \
  email-ext \
  blueocean
```

---

## Credentials Configuration

### 1. Docker Hub Credentials (if pushing images)

1. Go to: **Manage Jenkins → Manage Credentials**
2. Click **(global)** → **Add Credentials**
3. Select **Username with password**
4. Configure:
   - **ID**: `docker-hub-credentials`
   - **Username**: Your Docker Hub username
   - **Password**: Your Docker Hub password/token
   - **Description**: Docker Hub Authentication
5. Click **OK**

### 2. Git Credentials (if using private repo)

1. Add new credentials (same path as above)
2. Configure:
   - **ID**: `git-credentials`
   - **Kind**: SSH Username with private key (or Username/Password)
   - **Username**: Your Git username
   - Add your SSH private key or password
3. Click **OK**

### 3. Docker Registry URL (if using private registry)

1. Go to: **Manage Jenkins → Configure System**
2. Scroll to **Global Properties**
3. Check **Environment variables**
4. Add:
   - **Name**: `DOCKER_REGISTRY`
   - **Value**: `your-registry.azurecr.io` (or Docker Hub: `docker.io`)

---

## Pipeline Setup

### Step 1: Create New Pipeline Job

1. Click **New Item** from Jenkins dashboard
2. Enter name: **MedBot-Intelligence-CI**
3. Select **Pipeline**
4. Click **OK**

### Step 2: Configure Pipeline

#### General Settings
- ✅ **Discard old builds**: Keep builds for 10 days, max 10 builds
- ✅ **Do not allow concurrent builds**

#### Build Triggers (choose one)
- **Poll SCM**: `H/5 * * * *` (check every 5 minutes)
- **GitHub hook trigger** (if using GitHub webhooks)
- **Build periodically**: `H 2 * * *` (nightly at 2 AM)

#### Pipeline Definition
- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/your-username/MedBot-Intelligence.git`
- **Credentials**: Select git credentials (if private)
- **Branch Specifier**: `*/main` (or `*/develop`)
- **Script Path**: `Jenkinsfile`

### Step 3: Save Configuration

Click **Save** at the bottom

---

## Environment Configuration

### Global Environment Variables

1. Go to: **Manage Jenkins → Configure System**
2. Find **Global Properties**
3. Check **Environment variables**
4. Add variables from [ENV_CONFIG.md](.jenkins/ENV_CONFIG.md)

### Key Variables to Set

```
PROJECT_NAME=medbot-intelligence
PUSH_TO_REGISTRY=false
DEPLOY_ENABLED=false
NOTIFICATION_EMAIL=your-email@example.com
```

---

## Running Your First Build

### Manual Build

1. Go to your pipeline job: **MedBot-Intelligence-CI**
2. Click **Build Now**
3. Watch the build progress in:
   - **Console Output** (traditional view)
   - **Blue Ocean** (modern view)

### Expected Pipeline Stages

1. ✅ **Checkout** - Clone repository
2. ✅ **Environment Setup** - Validate tools
3. ✅ **Dependency Installation** - Install Python/Node packages
4. ✅ **Code Quality & Linting** - Run linters
5. ✅ **Run Tests** - Execute pytest for ml-predictor and indexeur-semantique
6. ✅ **Build Docker Images** - Create all service images
7. ⚠️ **Security Scan** - Scan for vulnerabilities (if Trivy installed)
8. ⏭️ **Integration Tests** - (Only on main/develop branches)
9. ⏭️ **Push to Registry** - (If PUSH_TO_REGISTRY=true)
10. ⏭️ **Deploy** - (If DEPLOY_ENABLED=true)

---

## Advanced Configuration

### Enable Slack Notifications

1. Install Slack Notification plugin
2. Get Slack webhook URL from workspace settings
3. Add to Jenkins:
   - **Manage Jenkins → Configure System**
   - Find **Slack** section
   - Add Workspace, Token, and Default Channel
4. Uncomment Slack notification code in `Jenkinsfile`

### Enable Email Notifications

1. Configure SMTP:
   - **Manage Jenkins → Configure System**
   - Find **E-mail Notification**
   - Add SMTP server settings
2. Uncomment email notification code in `Jenkinsfile`

### Enable Docker Registry Push

1. Set credentials (see Credentials Configuration)
2. Set environment variables:
   ```
   PUSH_TO_REGISTRY=true
   DOCKER_REGISTRY=docker.io
   ```
3. Re-run pipeline

---

## Troubleshooting

### Build Fails at "Checkout" Stage

**Problem**: Cannot access repository

**Solutions**:
- Verify repository URL is correct
- Check Git credentials are configured
- Ensure Jenkins has network access to Git server

### Build Fails at "Dependency Installation"

**Problem**: Python or npm packages fail to install

**Solutions**:
```bash
# Ensure Python/pip are in PATH
which python3
which pip3

# Ensure Node/npm are in PATH
which node
which npm

# Install in Jenkins agent/container
docker exec jenkins apt-get install python3-pip nodejs npm
```

### Build Fails at "Build Docker Images"

**Problem**: Docker not available in Jenkins

**Solutions**:
```bash
# For Docker-in-Docker, ensure socket is mounted
docker run -v /var/run/docker.sock:/var/run/docker.sock ...

# Or install Docker in Jenkins container
docker exec -u root jenkins apt-get update
docker exec -u root jenkins apt-get install docker.io
```

### Tests Fail

**Problem**: pytest cannot find modules

**Solutions**:
```bash
# Ensure PYTHONPATH is set correctly
export PYTHONPATH=/path/to/MedBot-Intelligence/services/ml-predictor

# Install test dependencies
pip3 install pytest pytest-cov
```

### Pipeline Timeout

**Problem**: Build exceeds 2-hour timeout

**Solutions**:
- Reduce number of services built in parallel
- Disable security scanning temporarily
- Increase timeout in Jenkinsfile:
  ```groovy
  options {
      timeout(time: 4, unit: 'HOURS')
  }
  ```

### Permission Denied Errors

**Problem**: Jenkins user lacks permissions

**Solutions**:
```bash
# Add Jenkins user to docker group (Linux)
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins

# Fix file permissions
sudo chown -R jenkins:jenkins /var/jenkins_home
```

---

## Best Practices

### 1. Use Branches for Different Pipelines
- `main` → Production deployments
- `develop` → Staging deployments
- `feature/*` → Build and test only

### 2. Monitor Build Times
- Use Blue Ocean to visualize stage durations
- Optimize slow stages (use caching, parallel builds)

### 3. Keep Build Logs
- Archive important artifacts
- Set appropriate log retention policies

### 4. Security
- Never commit credentials to Jenkinsfile
- Use Jenkins credentials manager
- Regularly update Jenkins and plugins

### 5. Notifications
- Configure notifications for failures only
- Use different channels for different branches

---

## Next Steps

1. ✅ Set up Jenkins server
2. ✅ Install required plugins
3. ✅ Configure credentials
4. ✅ Create pipeline job
5. ✅ Run first build
6. 🔄 Monitor and optimize
7. 🚀 Enable deployment to staging/production

## Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Pipeline Syntax Reference](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
- [Blue Ocean Guide](https://www.jenkins.io/projects/blueocean/)

---

## Support

For issues specific to this pipeline:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Jenkins console output
3. Check service logs in Docker containers
4. Consult the [implementation_plan.md](../brain/implementation_plan.md)
