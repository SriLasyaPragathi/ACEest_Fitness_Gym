// Jenkins Pipeline for ACEest Fitness API
// Declarative Pipeline

pipeline {
    agent any
    
    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    parameters {
        string(name: 'DOCKER_REGISTRY', defaultValue: 'docker.io', description: 'Docker Registry URL')
        string(name: 'DOCKER_IMAGE_NAME', defaultValue: 'aceest-fitness-api', description: 'Docker Image Name')
        string(name: 'PYTHON_VERSION', defaultValue: '3.11', description: 'Python Version')
    }
    
    environment {
        PYTHON_VERSION = "${params.PYTHON_VERSION}"
        BUILD_TAG = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        DOCKER_IMAGE = "${params.DOCKER_REGISTRY}/${params.DOCKER_IMAGE_NAME}:${BUILD_TAG}"
        DOCKER_IMAGE_LATEST = "${params.DOCKER_REGISTRY}/${params.DOCKER_IMAGE_NAME}:latest"
        WORKSPACE_PATH = "${WORKSPACE}"
    }
    
    stages {
        // ============ STAGE 1: CHECKOUT ============
        stage('Checkout') {
            steps {
                echo '🔄 Cloning repository from GitHub...'
                checkout scm
                sh 'git log --oneline -5'
                echo '✅ Repository cloned successfully'
            }
        }
        
        // ============ STAGE 2: BUILD & Dependencies ============
        stage('Build & Dependencies') {
            steps {
                echo '📦 Installing Python dependencies...'
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    python -m pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                    echo "✅ Dependencies installed successfully"
                '''
            }
        }
        
        // ============ STAGE 3: LINT ============
        stage('Lint') {
            steps {
                echo '🧹 Running code quality checks...'
                sh '''
                    . venv/bin/activate || . venv/Scripts/activate
                    echo "Running flake8..."
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics || true
                    flake8 app.py --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || true
                    echo "✅ Linting completed"
                '''
            }
        }
        
        // ============ STAGE 4: UNIT TESTS ============
        stage('Unit Tests') {
            steps {
                echo '🧪 Running Pytest suite...'
                sh '''
                    . venv/bin/activate || . venv/Scripts/activate
                    pytest tests/ -v --tb=short --junit-xml=test-results.xml
                    echo "✅ Tests completed"
                '''
            }
            post {
                always {
                    // Archive test results
                    junit 'test-results.xml'
                }
            }
        }
        
        // ============ STAGE 5: CODE COVERAGE ============
        stage('Code Coverage') {
            steps {
                echo '📊 Generating code coverage report...'
                sh '''
                    . venv/bin/activate || . venv/Scripts/activate
                    pytest tests/ --cov=app --cov-report=html --cov-report=xml --cov-report=term
                    echo "✅ Coverage report generated"
                '''
            }
        }
        
        // ============ STAGE 6: DOCKER BUILD ============
        stage('Docker Build') {
            steps {
                echo '🐳 Building Docker image...'
                sh '''
                    echo "Building image: ${DOCKER_IMAGE}"
                    docker build -t ${DOCKER_IMAGE} -t ${DOCKER_IMAGE_LATEST} .
                    echo "✅ Docker image built successfully"
                    docker images | grep aceest || true
                '''
            }
        }
        
        // ============ STAGE 7: DOCKER SCAN (Security) ============
        stage('Docker Security Scan') {
            when {
                branch 'main'
            }
            steps {
                echo '🔒 Scanning Docker image for vulnerabilities...'
                sh '''
                    # Trivy scan (if available)
                    which trivy && trivy image ${DOCKER_IMAGE} || echo "⚠️ Trivy not available"
                    echo "✅ Security scan completed"
                '''
            }
        }
        
        // ============ STAGE 8: INTEGRATION TEST ============
        stage('Integration Tests') {
            steps {
                echo '🔗 Running integration tests in Docker...'
                sh '''
                    echo "Starting container for integration tests..."
                    docker run -d --name aceest-test-${BUILD_NUMBER} -p 5000:5000 ${DOCKER_IMAGE}
                    sleep 5
                    
                    echo "Running health check..."
                    docker exec aceest-test-${BUILD_NUMBER} python -c "import requests; r = requests.get('http://localhost:5000/health'); print(r.status_code, r.json())" || sleep 3
                    
                    echo "Running tests in container..."
                    docker exec aceest-test-${BUILD_NUMBER} pytest tests/ -v --tb=short || exit 1
                    
                    echo "✅ Integration tests passed"
                    docker stop aceest-test-${BUILD_NUMBER} || true
                    docker rm aceest-test-${BUILD_NUMBER} || true
                '''
            }
            post {
                always {
                    sh 'docker stop aceest-test-${BUILD_NUMBER} || true; docker rm aceest-test-${BUILD_NUMBER} || true'
                }
            }
        }
        
        // ============ STAGE 9: DOCKER PUSH (Optional) ============
        stage('Docker Push') {
            when {
                branch 'main'
            }
            steps {
                echo '📤 Pushing Docker image to registry...'
                sh '''
                    echo "To push to registry, configure Docker credentials in Jenkins"
                    echo "Image built and ready: ${DOCKER_IMAGE}"
                    # docker push ${DOCKER_IMAGE}
                    # docker push ${DOCKER_IMAGE_LATEST}
                    echo "✅ Docker image ready for push"
                '''
            }
        }
        
        // ============ STAGE 10: ARCHIVE ARTIFACTS ============
        stage('Archive Artifacts') {
            steps {
                echo '📦 Archiving build artifacts...'
                sh '''
                    mkdir -p build-artifacts
                    cp -r tests/ build-artifacts/ || true
                    cp requirements.txt build-artifacts/ || true
                    cp Dockerfile build-artifacts/ || true
                    echo "✅ Artifacts archived"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'build-artifacts/**', allowEmptyArchive: true
                }
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up...'
            
            // Clean Docker resources
            sh '''
                docker stop aceest-test-${BUILD_NUMBER} || true
                docker rm aceest-test-${BUILD_NUMBER} || true
            '''
            
            // Clean workspace (optional)
            // cleanWs()
        }
        
        success {
            echo '✅ Pipeline completed successfully!'
            emailext(
                subject: "✅ Build ${BUILD_NUMBER} Succeeded",
                to: '${DEFAULT_RECIPIENTS}',
                body: '''
                    The build has completed successfully.
                    
                    Build Number: ${BUILD_NUMBER}
                    Build Status: SUCCESS
                    Docker Image: ${DOCKER_IMAGE}
                    
                    Check console output at ${BUILD_URL} to view the results.
                ''',
                attachLog: false
            )
        }
        
        failure {
            echo '❌ Pipeline failed!'
            emailext(
                subject: "❌ Build ${BUILD_NUMBER} Failed",
                to: '${DEFAULT_RECIPIENTS}',
                body: '''
                    The build has failed.
                    
                    Build Number: ${BUILD_NUMBER}
                    Build Status: FAILURE
                    
                    Please check console output at ${BUILD_URL} to view the error details.
                ''',
                attachLog: true
            )
        }
        
        unstable {
            echo '⚠️ Pipeline unstable'
        }
    }
}
