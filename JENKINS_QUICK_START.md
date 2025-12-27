# Jenkins Quick Start Guide

## ✅ Jenkins is Running!

**Access URL**: http://localhost:8080

**Initial Admin Password**: `54afac207bdb4dfc867c5ea04e0ff21c`

**Container Name**: `medbot-jenkins`

---

## 🚀 First Time Setup

### Step 1: Unlock Jenkins
1. Open http://localhost:8080
2. Paste the initial admin password: `54afac207bdb4dfc867c5ea04e0ff21c`
3. Click **Continue**

### Step 2: Install Plugins
1. Select **Install suggested plugins**
2. Wait for the installation to complete (3-5 minutes)

### Step 3: Create Admin User
1. Fill in your details:
   - Username: `admin`
   - Password: (choose a password)
   - Full name: Your name
   - Email: your-email@example.com
2. Click **Save and Continue**

### Step 4: Configure Instance
1. Keep the default Jenkins URL: `http://localhost:8080/`
2. Click **Save and Finish**
3. Click **Start using Jenkins**

---

## 📦 Create MedBot-Intelligence Pipeline

### Option 1: Via UI

1. Click **New Item**
2. Enter name: `MedBot-Intelligence-CI`
3. Select **Pipeline**
4. Click **OK**
5. Under **Pipeline** section:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `C:\Users\HP\Desktop\MedBot-Intelligence`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
6. Click **Save**
7. Click **Build Now**

### Option 2: Via Script (Run in PowerShell after Jenkins setup)

```powershell
# This will be available after Jenkins is fully configured
# Save as create-pipeline.ps1 and run it
```

---

## 🔧 Jenkins Container Management

### Start Jenkins
```powershell
docker start medbot-jenkins
```

### Stop Jenkins
```powershell
docker stop medbot-jenkins
```

### View Logs
```powershell
docker logs medbot-jenkins -f
```

### Get Admin Password (if needed again)
```powershell
docker exec medbot-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Remove Jenkins (if needed)
```powershell
docker stop medbot-jenkins
docker rm medbot-jenkins
# To also remove data:
docker volume rm jenkins_home
```

---

## 📊 Monitoring Your Pipeline

After creating the pipeline:

1. **Classic View**: http://localhost:8080/job/MedBot-Intelligence-CI/
2. **Console Output**: Click build number → Console Output
3. **Test Results**: Build page → Test Result
4. **Coverage Reports**: Build page → Coverage Report

---

## 🆘 Troubleshooting

### Jenkins Won't Start
```powershell
# Check if port 8080 is in use
netstat -ano | findstr :8080

# Check container status
docker ps -a | findstr jenkins

# View container logs
docker logs medbot-jenkins
```

### Can't Access Jenkins UI
- Ensure Docker Desktop is running
- Check container is running: `docker ps`
- Try restarting: `docker restart medbot-jenkins`
- Wait 30 seconds for Jenkins to fully start

### Forgot Admin Password
```powershell
docker exec medbot-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 📚 Additional Resources

- [Full Setup Guide](JENKINS_SETUP.md)
- [Quick Reference](.jenkins/QUICK_REFERENCE.md)
- [Environment Configuration](.jenkins/ENV_CONFIG.md)
- [Walkthrough](C:\Users\HP\.gemini\antigravity\brain\effa6916-7269-479f-adc6-a250dca2faeb\walkthrough.md)

---

## ⏭️ Next Steps

1. ✅ Complete Jenkins setup wizard
2. 🔧 Install additional plugins (Docker Pipeline, Blue Ocean)
3. 📦 Create MedBot-Intelligence-CI pipeline
4. ▶️ Run your first build
5. 📊 Review test results and coverage

Enjoy your Jenkins CI/CD pipeline! 🎉
