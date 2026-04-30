# PHASE 1 & 2: Setup Guide - SonarQube & Docker Hub Integration

## Overview
This guide walks through setting up SonarQube for code quality analysis (Phase 1) and Docker Hub integration for versioned image push (Phase 2).

---

## PHASE 1: SonarQube Setup

### Step 1: Start SonarQube with Docker Compose

```bash
# Navigate to project directory
cd p:\MTech_Devops\DevOps_Assignment

# Start SonarQube service (runs on port 9000)
docker-compose up -d sonarqube

# Wait for SonarQube to be ready (check logs)
docker-compose logs -f sonarqube

# Once ready, you'll see:
# "SonarQube is up"
```

### Step 2: Access SonarQube Dashboard

1. Open browser: **http://localhost:9000**
2. Default credentials: **admin / admin**
3. You'll be prompted to change password on first login

### Step 3: Generate SonarQube Authentication Token

1. Login to SonarQube
2. Go to: **Settings → Security → Users → Tokens** (or click your profile icon → My Account → Security)
3. Click **"Generate Tokens"**
4. Enter token name: `Jenkins`
5. Select scope: `Execute Analysis`
6. Click **Generate**
7. **COPY TOKEN** (you won't see it again) → Store safely
8. Format: typically looks like: `sqa_1234567890abcdef...`

### Step 4: Configure Jenkins Credentials

1. Open Jenkins: **http://localhost:8080** (or your Jenkins URL)
2. Go to: **Manage Jenkins → Credentials → System → Global credentials**
3. Click: **+ Add Credentials**
4. Fill in:
   - **Kind:** Secret text
   - **Secret:** `<paste SonarQube token here>`
   - **ID:** `SONARQUBE_TOKEN`
   - **Description:** `SonarQube Authentication Token`
5. Click **Create**

### Step 5: Configure SonarQube Server in Jenkins

1. In Jenkins: **Manage Jenkins → Configure System**
2. Scroll to: **SonarQube servers**
3. Click: **Add SonarQube**
4. Fill in:
   - **Name:** `SonarQube`
   - **Server URL:** `http://sonarqube:9000` (or if using host: `http://localhost:9000`)
   - **Server authentication token:** Select `SONARQUBE_TOKEN` credential
5. Click **Save**

### Step 6: Verify SonarQube Integration

Run a Jenkins build:

```bash
# Trigger a Jenkins build via GitHub webhook or manually
# Watch the console output for:
# "Running SonarQube static code analysis..."
# "✅ SonarQube analysis completed"

# Check SonarQube dashboard for new project analysis:
# http://localhost:9000/dashboard
```

### Troubleshooting SonarQube

| Issue | Solution |
|-------|----------|
| SonarQube won't start | Check Docker logs: `docker-compose logs sonarqube` |
| Port 9000 already in use | Change in docker-compose.yml: `"9001:9000"` |
| Jenkins can't reach SonarQube | If using Docker network, use `http://sonarqube:9000`; if on host, use `http://localhost:9000` |
| SonarQube slow on startup | First run takes 2-5 minutes; be patient |
| Analysis shows "0 issues" | Verify `sonar-scanner` is installed; check logs |

---

## PHASE 2: Docker Hub Registry Setup

### Step 1: Create Docker Hub Account & Repository

1. Go to: **https://hub.docker.com**
2. Sign up or login with your account
3. Create a repository:
   - Click **Create Repository**
   - **Name:** `aceest-fitness-api`
   - **Description:** `ACEest Fitness & Gym Management System - DevOps CI/CD`
   - **Visibility:** Public (for assignment submission) or Private
   - Click **Create**
4. Note your **Docker Hub username** (e.g., `your-docker-username`)

### Step 2: Generate Docker Hub Credentials

**Option A: Using Personal Access Token (Recommended)**
1. Go to: **Account Settings → Security → New Access Token**
2. **Access Token Description:** `Jenkins`
3. Click **Generate**
4. **COPY TOKEN** → Store safely
5. Format: typically looks like: `dckr_pat_1234...`

**Option B: Using Password (Legacy)**
1. Use your Docker Hub password directly

### Step 3: Add Docker Hub Credentials to Jenkins

1. Open Jenkins: **http://localhost:8080**
2. Go to: **Manage Jenkins → Credentials → System → Global credentials**
3. Click: **+ Add Credentials**
4. Fill in:
   - **Kind:** Username with password
   - **Username:** `<your-docker-hub-username>`
   - **Password:** `<Docker Hub token or password>`
   - **ID:** `DOCKER_HUB_CREDENTIALS`
   - **Description:** `Docker Hub Authentication`
5. Click **Create**

### Step 4: Update Jenkins Parameters

In Jenkins job configuration (or Jenkinsfile parameters):

```groovy
parameters {
    string(name: 'DOCKER_REGISTRY', defaultValue: 'docker.io', description: 'Docker Registry URL')
    string(name: 'DOCKER_IMAGE_NAME', defaultValue: 'your-docker-username/aceest-fitness-api', description: 'Docker Image Name')
}
```

**Replace `your-docker-username` with your actual Docker Hub username**

### Step 5: Enable Docker Push in Jenkinsfile

In **Jenkinsfile** (Stage 10: Docker Push), uncomment these lines:

```groovy
withCredentials([usernamePassword(credentialsId: 'DOCKER_HUB_CREDENTIALS', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
    sh '''
        echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin
        docker push ${DOCKER_IMAGE}
        docker push ${DOCKER_IMAGE_LATEST}
        docker push ${DOCKER_VERSION_TAG}
        docker logout
    '''
}
```

Full stage should look like:

```groovy
stage('Docker Push') {
    when {
        branch 'main'
    }
    steps {
        echo '📤 Pushing Docker images to registry...'
        withCredentials([usernamePassword(credentialsId: 'DOCKER_HUB_CREDENTIALS', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
            sh '''
                echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin
                
                echo "Pushing images to Docker registry..."
                docker push ${DOCKER_IMAGE}
                docker push ${DOCKER_IMAGE_LATEST}
                docker push ${DOCKER_VERSION_TAG}
                
                docker logout
                
                echo "✅ Images pushed successfully:"
                echo "  - ${DOCKER_IMAGE}"
                echo "  - ${DOCKER_IMAGE_LATEST}"
                echo "  - ${DOCKER_VERSION_TAG} (v${APP_VERSION})"
            '''
        }
    }
}
```

### Step 6: Test Docker Hub Push

1. Commit and push code to `main` branch
2. Jenkins triggers automatically
3. Check console output for: `"✅ Images pushed successfully"`
4. Verify in Docker Hub dashboard:
   - Repository shows new images
   - Tags visible: `latest`, `v1.0.0`, build numbers

### Step 7: Verify Pushed Images

```bash
# Pull image from Docker Hub
docker pull your-docker-username/aceest-fitness-api:latest
docker pull your-docker-username/aceest-fitness-api:v1.0.0

# Run container from hub image
docker run -p 5000:5000 your-docker-username/aceest-fitness-api:latest

# Check endpoints
curl http://localhost:5000/health
```

### Troubleshooting Docker Hub

| Issue | Solution |
|-------|----------|
| "Authentication required" error | Verify credentials in Jenkins and Docker Hub token is valid |
| Images not appearing in Docker Hub | Check Jenkins console for errors; verify `docker push` commands |
| Rate limiting (Docker Hub) | Use credentials to avoid rate limits; consider local registry for development |
| `docker login` fails | Use Personal Access Token, not password; ensure credentials are URL-safe |

---

## VERIFICATION CHECKLIST

### Phase 1: SonarQube
- [ ] SonarQube running on http://localhost:9000
- [ ] Dashboard accessible with default credentials
- [ ] Token generated and stored securely
- [ ] Jenkins credential created (SONARQUBE_TOKEN)
- [ ] SonarQube server configured in Jenkins
- [ ] Jenkins build includes SonarQube analysis stage
- [ ] Analysis results visible in SonarQube dashboard

### Phase 2: Docker Hub
- [ ] Docker Hub repository created (`your-username/aceest-fitness-api`)
- [ ] Personal Access Token generated and stored
- [ ] Jenkins credential created (DOCKER_HUB_CREDENTIALS)
- [ ] Jenkinsfile Docker Push stage uncommented with credentials
- [ ] Jenkins build pushes images to Docker Hub
- [ ] Docker Hub shows 3+ image tags (latest, v1.0.0, build numbers)
- [ ] `docker pull` from Docker Hub works

---

## NEXT STEPS

After verification:
1. Proceed to **Phase 3: Kubernetes Manifests & Minikube** (in PHASE_3_SETUP.md)
2. Create K8s manifests for Minikube deployment
3. Implement deployment strategies (Blue-Green, Canary, etc.)

---

## COMMANDS QUICK REFERENCE

```bash
# SonarQube
docker-compose up -d sonarqube
docker-compose logs sonarqube
curl http://localhost:9000

# Docker Hub
docker login
docker tag aceest-fitness-api:latest username/aceest-fitness-api:latest
docker push username/aceest-fitness-api:latest
docker logout

# Jenkins Log
docker logs jenkins  # if Jenkins is in Docker
# Or access: http://localhost:8080/log
```

---

**Status:** ✅ Phase 1 & 2 setup guide complete  
**Next:** Phase 3 - Kubernetes Manifests & Minikube Setup
