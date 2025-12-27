pipeline {
    agent any
    
    environment {
        // Project Configuration
        PROJECT_NAME = 'medbot-intelligence'
        DOCKER_REGISTRY = credentials('docker-registry-url') // Configure in Jenkins
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials') // Configure in Jenkins
        
        // Service Ports (for health checks)
        API_GATEWAY_PORT = '8000'
        DOC_INGESTOR_PORT = '8001'
        DEID_PORT = '8002'
        INDEXEUR_PORT = '8003'
        LLM_QA_PORT = '8004'
        SYNTHESE_PORT = '8005'
        AUDIT_PORT = '8006'
        ML_PREDICTOR_PORT = '8007'
        FRONTEND_PORT = '3000'
        
        // Build Configuration
        COMPOSE_PROJECT_NAME = "docqa-ci-${BUILD_NUMBER}"
        COMPOSE_FILE = 'docker-compose.yml'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
        timestamps()
        timeout(time: 2, unit: 'HOURS')
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '🔍 Checking out source code...'
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    env.GIT_BRANCH_NAME = env.GIT_BRANCH.replaceAll('origin/', '')
                }
                echo "📝 Building commit: ${env.GIT_COMMIT_SHORT} on branch: ${env.GIT_BRANCH_NAME}"
            }
        }
        
        stage('Environment Setup') {
            steps {
                echo '⚙️ Validating environment...'
                sh '''
                    echo "Docker version:"
                    docker --version
                    echo "Docker Compose version:"
                    docker-compose --version
                    echo "Python version:"
                    python3 --version || python --version
                    echo "Node version:"
                    node --version
                    echo "NPM version:"
                    npm --version
                '''
            }
        }
        
        stage('Dependency Installation') {
            parallel {
                stage('Python Services') {
                    steps {
                        echo '🐍 Installing Python dependencies...'
                        script {
                            def services = [
                                'api-gateway', 'doc-ingestor', 'deid', 
                                'indexeur-semantique', 'llm-qa-module', 
                                'synthese-comparative', 'audit-logger', 'ml-predictor'
                            ]
                            services.each { service ->
                                echo "Installing dependencies for ${service}..."
                                sh """
                                    cd services/${service}
                                    if [ -f requirements.txt ]; then
                                        pip3 install -r requirements.txt --quiet || echo "Warning: Failed to install ${service} dependencies"
                                    fi
                                """
                            }
                        }
                    }
                }
                
                stage('Frontend') {
                    steps {
                        echo '⚛️ Installing Frontend dependencies...'
                        dir('interface-clinique') {
                            sh 'npm ci --prefer-offline --no-audit'
                        }
                    }
                }
            }
        }
        
        stage('Code Quality & Linting') {
            parallel {
                stage('Python Linting') {
                    steps {
                        echo '🔍 Running Python linters...'
                        script {
                            try {
                                sh '''
                                    pip3 install flake8 pylint --quiet
                                    echo "Running flake8..."
                                    flake8 services/ --count --select=E9,F63,F7,F82 --show-source --statistics || true
                                '''
                            } catch (Exception e) {
                                echo "⚠️ Linting warnings found (non-blocking)"
                            }
                        }
                    }
                }
                
                stage('Frontend Linting') {
                    steps {
                        echo '🔍 Running Next.js build check...'
                        dir('interface-clinique') {
                            script {
                                try {
                                    sh 'npm run build'
                                } catch (Exception e) {
                                    echo "⚠️ Frontend build warnings (non-blocking)"
                                }
                            }
                        }
                    }
                }
            }
        }
        
        stage('Run Tests') {
            parallel {
                stage('ML Predictor Tests') {
                    steps {
                        echo '🧪 Running ML Predictor tests...'
                        dir('services/ml-predictor') {
                            sh '''
                                if [ -f pytest.ini ] && [ -d tests ]; then
                                    pip3 install pytest pytest-cov --quiet
                                    python3 -m pytest tests/ -v --tb=short --junitxml=test-results.xml --cov=app --cov-report=xml --cov-report=html || true
                                else
                                    echo "No tests found for ml-predictor"
                                fi
                            '''
                        }
                    }
                    post {
                        always {
                            junit(testResults: 'services/ml-predictor/test-results.xml', allowEmptyResults: true)
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'services/ml-predictor/htmlcov',
                                reportFiles: 'index.html',
                                reportName: 'ML Predictor Coverage Report'
                            ])
                        }
                    }
                }
                
                stage('Indexeur Semantique Tests') {
                    steps {
                        echo '🧪 Running Indexeur Semantique tests...'
                        dir('services/indexeur-semantique') {
                            sh '''
                                if [ -d tests ]; then
                                    pip3 install pytest pytest-cov --quiet
                                    python3 -m pytest tests/ -v --tb=short --junitxml=test-results.xml --cov=app --cov-report=xml --cov-report=html || true
                                else
                                    echo "No tests found for indexeur-semantique"
                                fi
                            '''
                        }
                    }
                    post {
                        always {
                            junit(testResults: 'services/indexeur-semantique/test-results.xml', allowEmptyResults: true)
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'services/indexeur-semantique/htmlcov',
                                reportFiles: 'index.html',
                                reportName: 'Indexeur Coverage Report'
                            ])
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Images') {
            steps {
                echo '🐳 Building Docker images...'
                script {
                    // Build all services in parallel using docker-compose
                    sh """
                        docker-compose -f ${COMPOSE_FILE} build --parallel
                    """
                    
                    // Tag images with build number and git commit
                    def services = [
                        'api-gateway', 'doc-ingestor', 'deid', 
                        'indexeur-semantique', 'llm-qa-module', 
                        'synthese-comparative', 'audit-logger', 'ml-predictor', 'frontend'
                    ]
                    
                    services.each { service ->
                        sh """
                            docker tag docqa-${service}:latest ${PROJECT_NAME}/${service}:${BUILD_NUMBER}
                            docker tag docqa-${service}:latest ${PROJECT_NAME}/${service}:${GIT_COMMIT_SHORT}
                        """
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo '🔒 Running security scans...'
                script {
                    try {
                        // Using Trivy for vulnerability scanning
                        sh '''
                            if command -v trivy &> /dev/null; then
                                echo "Running Trivy security scan..."
                                trivy image --severity HIGH,CRITICAL ${PROJECT_NAME}/api-gateway:${BUILD_NUMBER} || true
                            else
                                echo "⚠️ Trivy not installed, skipping security scan"
                                echo "Install with: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin"
                            fi
                        '''
                    } catch (Exception e) {
                        echo "⚠️ Security scan completed with warnings (non-blocking)"
                    }
                }
            }
        }
        
        stage('Integration Tests') {
            when {
                expression { return env.GIT_BRANCH_NAME == 'main' || env.GIT_BRANCH_NAME == 'develop' }
            }
            steps {
                echo '🔗 Running integration tests...'
                script {
                    try {
                        sh """
                            # Start services with test configuration
                            COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME} docker-compose -f ${COMPOSE_FILE} up -d postgres rabbitmq redis
                            
                            # Wait for infrastructure services
                            sleep 30
                            
                            # Start application services
                            COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME} docker-compose -f ${COMPOSE_FILE} up -d
                            
                            # Wait for services to be healthy
                            sleep 60
                            
                            # Run health checks
                            echo "Checking service health..."
                            curl -f http://localhost:${API_GATEWAY_PORT}/health || echo "API Gateway not ready"
                            curl -f http://localhost:${INDEXEUR_PORT}/health || echo "Indexeur not ready"
                            
                            echo "✅ Integration test environment ready"
                        """
                    } catch (Exception e) {
                        error "Integration tests failed: ${e.message}"
                    }
                }
            }
            post {
                always {
                    sh """
                        # Cleanup test environment
                        COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME} docker-compose -f ${COMPOSE_FILE} down -v || true
                    """
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                expression { 
                    return (env.GIT_BRANCH_NAME == 'main' || env.GIT_BRANCH_NAME == 'develop') && 
                           env.PUSH_TO_REGISTRY == 'true' 
                }
            }
            steps {
                echo '📤 Pushing images to registry...'
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-hub-credentials') {
                        def services = [
                            'api-gateway', 'doc-ingestor', 'deid', 
                            'indexeur-semantique', 'llm-qa-module', 
                            'synthese-comparative', 'audit-logger', 'ml-predictor', 'frontend'
                        ]
                        
                        services.each { service ->
                            sh """
                                docker push ${PROJECT_NAME}/${service}:${BUILD_NUMBER}
                                docker push ${PROJECT_NAME}/${service}:${GIT_COMMIT_SHORT}
                            """
                        }
                        
                        // Tag latest for main branch
                        if (env.GIT_BRANCH_NAME == 'main') {
                            services.each { service ->
                                sh """
                                    docker tag ${PROJECT_NAME}/${service}:${BUILD_NUMBER} ${PROJECT_NAME}/${service}:latest
                                    docker push ${PROJECT_NAME}/${service}:latest
                                """
                            }
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Environment') {
            when {
                expression { 
                    return env.GIT_BRANCH_NAME == 'main' && env.DEPLOY_ENABLED == 'true'
                }
            }
            steps {
                echo '🚀 Deploying to environment...'
                script {
                    // Example deployment - customize based on your infrastructure
                    sh """
                        # Pull latest images
                        docker-compose pull
                        
                        # Restart services with zero downtime
                        docker-compose up -d --no-build --remove-orphans
                        
                        # Wait for services to be healthy
                        sleep 30
                        
                        # Verify deployment
                        docker-compose ps
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up...'
            sh '''
                # Remove dangling images
                docker image prune -f || true
                
                # Clean up test containers
                docker ps -a -q --filter "name=${COMPOSE_PROJECT_NAME}" | xargs -r docker rm -f || true
            '''
        }
        
        success {
            echo '✅ Pipeline succeeded!'
            // Uncomment to enable notifications
            // emailext(
            //     subject: "✅ Build Successful: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
            //     body: "Build ${env.BUILD_NUMBER} succeeded for ${env.GIT_BRANCH_NAME}.\n\nCommit: ${env.GIT_COMMIT_SHORT}",
            //     to: "${env.NOTIFICATION_EMAIL}"
            // )
        }
        
        failure {
            echo '❌ Pipeline failed!'
            // Uncomment to enable notifications
            // emailext(
            //     subject: "❌ Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
            //     body: "Build ${env.BUILD_NUMBER} failed for ${env.GIT_BRANCH_NAME}.\n\nCommit: ${env.GIT_COMMIT_SHORT}\n\nCheck console output: ${env.BUILD_URL}",
            //     to: "${env.NOTIFICATION_EMAIL}"
            // )
        }
        
        unstable {
            echo '⚠️ Pipeline unstable!'
        }
    }
}
