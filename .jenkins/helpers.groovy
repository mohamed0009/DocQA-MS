#!/usr/bin/env groovy

/**
 * Jenkins Helper Functions for MedBot Intelligence CI/CD Pipeline
 * Contains reusable functions for building, testing, and deploying services
 */

/**
 * Build a Python FastAPI service
 * @param serviceName Name of the service directory
 * @param buildArgs Additional docker build arguments (optional)
 */
def buildPythonService(String serviceName, Map buildArgs = [:]) {
    echo "🔨 Building Python service: ${serviceName}"
    
    dir("services/${serviceName}") {
        // Install dependencies
        sh """
            if [ -f requirements.txt ]; then
                pip3 install -r requirements.txt --quiet
                echo "✅ Dependencies installed for ${serviceName}"
            fi
        """
        
        // Build Docker image if Dockerfile exists
        if (fileExists('Dockerfile')) {
            def imageTag = "${env.PROJECT_NAME}/${serviceName}:${env.BUILD_NUMBER}"
            def buildArgsStr = buildArgs.collect { k, v -> "--build-arg ${k}=${v}" }.join(' ')
            
            sh """
                docker build ${buildArgsStr} -t ${imageTag} .
                echo "✅ Docker image built: ${imageTag}"
            """
        }
    }
}

/**
 * Run pytest for a Python service
 * @param serviceName Name of the service directory
 * @param coverage Whether to generate coverage reports (default: true)
 */
def runPytestForService(String serviceName, boolean coverage = true) {
    echo "🧪 Running tests for: ${serviceName}"
    
    dir("services/${serviceName}") {
        if (fileExists('tests') || fileExists('test')) {
            def coverageArgs = coverage ? '--cov=app --cov-report=xml --cov-report=html' : ''
            
            sh """
                pip3 install pytest pytest-cov --quiet
                python3 -m pytest tests/ -v --tb=short --junitxml=test-results.xml ${coverageArgs} || true
            """
            
            // Publish results
            junit(testResults: 'test-results.xml', allowEmptyResults: true)
            
            if (coverage && fileExists('htmlcov/index.html')) {
                publishHTML(target: [
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: "${serviceName} Coverage Report"
                ])
            }
        } else {
            echo "⚠️ No tests found for ${serviceName}"
        }
    }
}

/**
 * Build Docker image for a service
 * @param serviceName Service name
 * @param tag Docker tag (default: BUILD_NUMBER)
 * @param context Build context directory (default: service directory)
 */
def buildDockerImage(String serviceName, String tag = null, String context = null) {
    def imageTag = tag ?: env.BUILD_NUMBER
    def buildContext = context ?: "services/${serviceName}"
    
    echo "🐳 Building Docker image for ${serviceName}"
    
    sh """
        docker build -t ${env.PROJECT_NAME}/${serviceName}:${imageTag} ${buildContext}
        docker tag ${env.PROJECT_NAME}/${serviceName}:${imageTag} ${env.PROJECT_NAME}/${serviceName}:latest
    """
}

/**
 * Push Docker image to registry
 * @param serviceName Service name
 * @param tags List of tags to push
 */
def pushDockerImage(String serviceName, List<String> tags) {
    echo "📤 Pushing Docker image for ${serviceName}"
    
    tags.each { tag ->
        sh """
            docker push ${env.PROJECT_NAME}/${serviceName}:${tag}
        """
    }
}

/**
 * Health check for a service
 * @param url Service health check URL
 * @param retries Number of retry attempts (default: 5)
 * @param waitSeconds Seconds between retries (default: 10)
 */
def healthCheckService(String url, int retries = 5, int waitSeconds = 10) {
    echo "🏥 Health checking: ${url}"
    
    def attempt = 0
    def healthy = false
    
    while (attempt < retries && !healthy) {
        attempt++
        try {
            sh """
                curl -f -s -o /dev/null -w "%{http_code}" ${url} | grep -q "200"
            """
            healthy = true
            echo "✅ Service is healthy: ${url}"
        } catch (Exception e) {
            if (attempt < retries) {
                echo "⏳ Attempt ${attempt}/${retries} failed, retrying in ${waitSeconds}s..."
                sleep(waitSeconds)
            } else {
                error "❌ Service failed health check after ${retries} attempts: ${url}"
            }
        }
    }
}

/**
 * Run database migrations for a service
 * @param serviceName Service name
 */
def runMigrations(String serviceName) {
    echo "🗄️ Running migrations for ${serviceName}"
    
    dir("services/${serviceName}") {
        if (fileExists('alembic.ini') || fileExists('migrations')) {
            sh """
                pip3 install alembic --quiet
                alembic upgrade head
                echo "✅ Migrations completed for ${serviceName}"
            """
        } else {
            echo "⚠️ No migrations found for ${serviceName}"
        }
    }
}

/**
 * Get list of changed services based on git diff
 * @param baseBranch Branch to compare against (default: main)
 * @return List of changed service names
 */
def getChangedServices(String baseBranch = 'main') {
    def changedFiles = sh(
        returnStdout: true,
        script: "git diff --name-only origin/${baseBranch}...HEAD || echo ''"
    ).trim()
    
    def services = []
    changedFiles.split('\n').each { file ->
        if (file.startsWith('services/')) {
            def service = file.split('/')[1]
            if (!services.contains(service)) {
                services.add(service)
            }
        }
    }
    
    echo "📝 Changed services: ${services.join(', ') ?: 'none'}"
    return services
}

/**
 * Send notification (Slack, Email, etc.)
 * @param status Build status (success, failure, unstable)
 * @param message Custom message
 */
def sendNotification(String status, String message = null) {
    def statusEmoji = [
        'success': '✅',
        'failure': '❌',
        'unstable': '⚠️'
    ]
    
    def emoji = statusEmoji[status] ?: '📢'
    def msg = message ?: "Build ${env.BUILD_NUMBER} ${status}"
    
    echo "${emoji} ${msg}"
    
    // Uncomment and configure for Slack notifications
    // slackSend(
    //     color: status == 'success' ? 'good' : (status == 'failure' ? 'danger' : 'warning'),
    //     message: "${emoji} ${msg}\nBranch: ${env.GIT_BRANCH_NAME}\nCommit: ${env.GIT_COMMIT_SHORT}"
    // )
}

/**
 * Clean up Docker resources
 * @param olderThanHours Remove images older than X hours (default: 24)
 */
def cleanupDocker(int olderThanHours = 24) {
    echo "🧹 Cleaning up Docker resources..."
    
    sh """
        # Remove stopped containers
        docker container prune -f --filter "until=${olderThanHours}h" || true
        
        # Remove dangling images
        docker image prune -f || true
        
        # Remove unused volumes
        docker volume prune -f --filter "label!=keep" || true
        
        echo "✅ Docker cleanup completed"
    """
}

/**
 * Archive build artifacts
 * @param serviceName Service name
 * @param patterns File patterns to archive
 */
def archiveArtifacts(String serviceName, List<String> patterns) {
    echo "📦 Archiving artifacts for ${serviceName}"
    
    patterns.each { pattern ->
        archiveArtifacts artifacts: "services/${serviceName}/${pattern}", 
                        allowEmptyArchive: true,
                        fingerprint: true
    }
}

// Return this for use in Jenkinsfile
return this
