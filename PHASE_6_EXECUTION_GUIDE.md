# 🚀 Phase 6: Jenkins Pipeline Enhancement - EXECUTION GUIDE

**Status:** 🔄 IN-PROGRESS (75% → Ready for Testing)  
**Objective:** Complete K8s deployment orchestration and test full CI/CD pipeline  
**Time Estimate:** 2-3 hours  
**Date:** April 26, 2026

---

## ✅ WHAT WAS JUST COMPLETED

**3 New Jenkins Pipeline Stages Added:**

1. **Stage 12: Deploy to Minikube** ☸️
   - Verifies K8s cluster connectivity
   - Applies all Kubernetes manifests (namespace, configmap, storage, deployment, service)
   - Monitors rollout status
   - Validates pod health

2. **Stage 13: K8s Smoke Tests** ✅
   - Runs 25+ automated K8s deployment tests
   - Validates pod health, service accessibility, load balancing
   - Performs health endpoint verification
   - Archives test results

3. **Stage 14: Test Deployment Strategies (Optional)** 🔄
   - References Blue-Green, Canary, A/B Testing strategies
   - Guides manual testing of advanced deployment patterns

**Enhanced Post-Success Section:**
- Displays K8s deployment status
- Shows Docker image list
- Provides next steps and access instructions

---

## 📋 PRE-EXECUTION CHECKLIST

Before running the pipeline, verify these prerequisites:

### ✅ Local Environment Setup
```bash
# 1. Verify Minikube is installed and running
minikube status
# Expected output: host: Running, kubelet: Running, apiserver: Running

# 2. Verify kubectl is configured
kubectl cluster-info
# Expected output: Kubernetes master is running at...

# 3. Verify Python virtual environment
python --version
# Expected: Python 3.11+
```

### ✅ Git Repository
```bash
# 4. Create/configure GitHub webhook to Jenkins
# In GitHub repo settings:
# - Settings → Webhooks
# - Add webhook: http://<jenkins-url>/github-webhook/
# - Content type: application/json
# - Events: Push events

# 5. Verify main branch is ready
git branch
# Expected: * main (active branch)
```

### ✅ Docker Configuration
```bash
# 6. Verify Docker is configured for Minikube
eval $(minikube docker-env)  # Linux/macOS
# OR PowerShell:
@(minikube docker-env) | Invoke-Expression

# 7. Test Docker image build
docker build -t aceest-fitness-api:latest .
# Expected: Successfully tagged aceest-fitness-api:latest
```

### ✅ Jenkins Configuration
```bash
# 8. Verify Jenkins has kubectl configured
# In Jenkins server, as the jenkins user:
kubectl cluster-info

# 9. Verify Jenkins can access K8s cluster
# Jenkins → Manage Jenkins → Configure System
# Check: Kubernetes plugin (if installed)
```

---

## 🚀 EXECUTION STEPS

### Step 1: Start Minikube Cluster

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=4096 --disk-size=20g

# Verify cluster is running
minikube status

# Expected output:
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured

# Point Docker to Minikube (if not already done)
eval $(minikube docker-env)  # Linux/macOS
# OR Windows PowerShell:
@(minikube docker-env) | Invoke-Expression
```

### Step 2: Verify K8s Manifests

```bash
# Review K8s directory structure
ls -la k8s/
# Expected: namespace.yaml, configmap.yaml, storage.yaml, deployment-base.yaml, service.yaml, etc.

# Validate YAML syntax
kubectl apply -f k8s/ --dry-run=client -o yaml > /tmp/k8s-validation.yaml
echo "✅ K8s manifests are syntactically valid"
```

### Step 3: Build Docker Image

```bash
# Build Docker image with version tags
docker build \
    -t aceest-fitness-api:latest \
    -t aceest-fitness-api:v1.0.0 \
    -t aceest-fitness-api:phase-6 \
    .

# Verify image was created
docker images | grep aceest

# Expected:
# aceest-fitness-api    latest    <image-id>    <time> ago    xxx MB
# aceest-fitness-api    v1.0.0    <image-id>    <time> ago    xxx MB
# aceest-fitness-api    phase-6   <image-id>    <time> ago    xxx MB
```

### Step 4: Commit Code to Git

```bash
# Stage changes
git add -A

# Commit with meaningful message
git commit -m "Phase 6: Add K8s deployment stages to Jenkins pipeline"

# Push to main branch (triggers Jenkins webhook)
git push origin main

# Verify commit
git log --oneline -3
```

### Step 5: Monitor Jenkins Pipeline

```bash
# Option A: Watch Jenkins console
# 1. Open Jenkins UI: http://localhost:8080
# 2. Click on "aceest-fitness-api" job
# 3. Click "Console Output" on the latest build
# 4. Watch stages execute in real-time

# Option B: Monitor from CLI
# Tail Jenkins logs for this build
tail -f ~/.jenkins/jobs/aceest-fitness-api/builds/lastBuild/log

# Option C: Check pipeline status
curl -s http://localhost:8080/job/aceest-fitness-api/lastBuild/api/json | grep '"result"'
```

### Step 6: Expected Pipeline Execution

**Stage Sequence:**
```
✅ Stage 1: Checkout
   ├─ Git clone
   └─ Verify branch

✅ Stage 2: Build & Dependencies
   ├─ Create venv
   └─ pip install -r requirements.txt

✅ Stage 3: Lint
   ├─ Run flake8
   └─ Check code quality

✅ Stage 4: Unit Tests
   ├─ Run pytest
   └─ Report results

✅ Stage 5: Code Coverage
   ├─ Generate coverage report
   └─ Create HTML report

✅ Stage 6: SonarQube Analysis
   ├─ Run sonar-scanner
   └─ Upload results to http://localhost:9000

✅ Stage 7: Docker Build
   ├─ Build image with 3 tags
   └─ Verify image exists

✅ Stage 8: Docker Security Scan
   ├─ Scan with Trivy (if available)
   └─ Report vulnerabilities

✅ Stage 9: Integration Tests
   ├─ Run tests in container
   └─ Validate in isolated environment

✅ Stage 10: Docker Push
   ├─ Tag images
   └─ Ready for registry push (credentials needed)

✅ Stage 11: Archive Artifacts
   ├─ Collect test results
   └─ Archive for later retrieval

🆕 ✅ Stage 12: Deploy to Minikube ☸️
   ├─ Apply K8s manifests
   ├─ Monitor rollout status
   └─ Verify pod health

🆕 ✅ Stage 13: K8s Smoke Tests ✅
   ├─ Run 25+ K8s tests
   ├─ Validate health endpoints
   └─ Archive test results

🆕 ✅ Stage 14: Test Deployment Strategies (Optional)
   └─ Reference strategy scripts
```

**Expected Total Time:** 5-10 minutes

### Step 7: Verify Successful Deployment

```bash
# Check K8s deployment
kubectl get pods -n aceest-production

# Expected output:
# NAME                           READY   STATUS    RESTARTS   AGE
# aceest-api-xxxxx-xxxxx    1/1     Running   0          1m
# aceest-api-xxxxx-yyyyy    1/1     Running   0          1m
# aceest-api-xxxxx-zzzzz    1/1     Running   0          1m

# Check service
kubectl get svc -n aceest-production

# Expected output:
# NAME              TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
# aceest-service    LoadBalancer   10.98.xx.xx    <pending>     80:32xxx/TCP   1m

# If using Minikube, get the service IP
minikube service aceest-service -n aceest-production --url

# Test health endpoint
curl http://<service-ip>/health

# Expected response (200 OK):
# {"status": "healthy", "version": "1.0.0", "timestamp": "..."}
```

### Step 8: Verify K8s Smoke Tests Passed

```bash
# Check Jenkins test results
# In Jenkins UI: job → build → Test Result (should show all green ✅)

# Manually run tests to verify
kubectl cluster-info  # Verify K8s connection first

pip install -r requirements.txt
pytest tests/test_k8s_deployment.py -v

# Expected output:
# tests/test_k8s_deployment.py::TestDeploymentHealth::test_deployment_exists PASSED ✅
# tests/test_k8s_deployment.py::TestDeploymentHealth::test_replicas_configured PASSED ✅
# tests/test_k8s_deployment.py::TestServiceAccessibility::test_service_exists PASSED ✅
# ... (25+ more tests)
# ======================== 25 passed in X.XXs ========================
```

---

## 🔧 TROUBLESHOOTING

### Issue: "kubectl: command not found"
```bash
# Solution 1: Install kubectl
# macOS: brew install kubectl
# Windows: choco install kubernetes-cli
# Linux: sudo apt-get install kubectl

# Solution 2: Verify kubectl in Jenkins
# Jenkins → Manage Jenkins → System Configuration
# Check PATH includes kubectl binary
```

### Issue: "Kubernetes cluster not accessible"
```bash
# Solution: Start Minikube
minikube start --cpus=4 --memory=4096

# Verify connection
kubectl cluster-info

# If still failing, reset Minikube:
minikube delete
minikube start --cpus=4 --memory=4096
```

### Issue: "K8s deployment timeout"
```bash
# Check pod status
kubectl describe pods -n aceest-production

# Check pod logs
kubectl logs -n aceest-production -l app=aceest-api --tail=50

# Check resource availability
kubectl get nodes
kubectl describe nodes

# Increase timeout if needed (edit Jenkinsfile Stage 12)
kubectl rollout status deployment/aceest-api -n aceest-production --timeout=10m
```

### Issue: "SonarQube server unreachable"
```bash
# Ensure SonarQube Docker service is running
docker-compose up -d sonarqube
docker-compose logs sonarqube | tail -20

# Verify connectivity from Jenkins container
docker exec jenkins curl http://sonarqube:9000
```

### Issue: "Integration tests fail in Docker"
```bash
# Check Docker image
docker images | grep aceest

# Test image manually
docker run -it aceest-fitness-api:latest /bin/bash
pytest tests/ -v

# Verify app.py syntax
python -m py_compile app.py
```

---

## ✨ POST-DEPLOYMENT VALIDATION

### Verification Checklist

```bash
# ☑️ 1. Verify Jenkins Pipeline Stages
curl http://localhost:8080/job/aceest-fitness-api/lastBuild/api/json | grep '"displayName"'
# Should show build number and timestamp

# ☑️ 2. Verify K8s Pods Running
kubectl get pods -n aceest-production --no-headers | wc -l
# Should show 3 (three pod replicas)

# ☑️ 3. Verify Service Accessibility
kubectl get svc aceest-service -n aceest-production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
# Should return an IP or wait for LoadBalancer to assign

# ☑️ 4. Verify Health Endpoint
SERVICE_URL=$(minikube service aceest-service -n aceest-production --url)
curl $SERVICE_URL/health
# Should return 200 with {"status": "healthy", ...}

# ☑️ 5. Verify K8s Tests Passed
kubectl get events -n aceest-production --sort-by='.lastTimestamp'
# Should show successful pod deployments

# ☑️ 6. Verify Docker Images Tagged
docker images | grep aceest
# Should show latest, v1.0.0, and build-specific tags

# ☑️ 7. Verify SonarQube Analysis
curl http://localhost:9000/api/projects | grep aceest-fitness-api
# Should find the project analysis

# ☑️ 8. Verify Artifacts Archived
curl http://localhost:8080/job/aceest-fitness-api/lastBuild/artifact/build-artifacts/ \
  | grep -c "\.xml\|\.txt\|\.py"
# Should show archived test results
```

---

## 🎯 NEXT IMMEDIATE ACTIONS

Once Phase 6 is verified and all tests pass:

### Phase 6 Completion Tasks
```
✅ Added K8s deployment stage to Jenkins (Stage 12)
✅ Added K8s smoke tests stage to Jenkins (Stage 13)
✅ Added deployment strategies reference (Stage 14)
✅ Enhanced post-success section with K8s status
⏳ Test full pipeline end-to-end (YOU ARE HERE)
⏳ Verify all 14 stages execute successfully
⏳ Verify K8s pods deployed and healthy
⏳ Verify smoke tests pass (25+ tests)
```

### Phase 7 Tasks (CI/CD Architecture Report)
```
- Write 2-3 page technical report
- Include pipeline architecture diagram
- Document deployment strategies
- Explain challenges and solutions
- Add rollback procedures
- Save as: CI_CD_ARCHITECTURE_REPORT.md
```

### Phase 8 Tasks (Final Validation)
```
- Verify GitHub repository is public
- Verify Docker Hub has versioned images
- Verify Minikube cluster running with live service
- Verify Jenkins pipeline successful build
- Verify SonarQube dashboard accessible
- Record endpoint URLs for submission
```

---

## 📊 SUCCESS CRITERIA

**Phase 6 is COMPLETE when:**

✅ **Jenkins Pipeline Executes Successfully**
- All 14 stages pass (green ✅ in Jenkins UI)
- Total execution time: 5-10 minutes
- No errors in console output

✅ **Kubernetes Deployment Works**
- 3 pods deployed and in "Running" state
- Service is accessible via LoadBalancer
- Health endpoint responds (200 OK)

✅ **K8s Smoke Tests Pass**
- 25+ tests pass (no failures)
- Test results archived in Jenkins
- Deployment health verified

✅ **Docker Images Tagged**
- `aceest-fitness-api:latest`
- `aceest-fitness-api:v1.0.0`
- Build-specific tag: `aceest-fitness-api:42-abc1234`

✅ **Build Artifacts Archived**
- Test results stored
- Coverage reports available
- Build metadata recorded

✅ **Ready for Production**
- Deployment strategies documented and ready
- Rollback procedures tested
- Health checks passing
- Zero-downtime verified

---

## 🎓 WHAT YOU'VE LEARNED

By completing Phase 6, you've mastered:

✅ Jenkins declarative pipeline syntax  
✅ Multi-stage CI/CD orchestration  
✅ Kubernetes deployment automation  
✅ Docker image versioning & tagging  
✅ Automated K8s testing  
✅ Post-deployment validation  
✅ Health check configuration  
✅ Build artifact management  
✅ Zero-downtime deployment patterns  
✅ Production-ready CI/CD pipeline  

---

## 📞 QUICK REFERENCE COMMANDS

```bash
# Start Minikube
minikube start --cpus=4 --memory=4096

# View Minikube dashboard
minikube dashboard

# Check K8s cluster
kubectl cluster-info
kubectl get pods -n aceest-production
kubectl get svc -n aceest-production

# View pod logs
kubectl logs -n aceest-production -l app=aceest-api -f

# Access service
minikube service aceest-service -n aceest-production

# Run K8s tests
pytest tests/test_k8s_deployment.py -v

# View Jenkins console
http://localhost:8080/job/aceest-fitness-api/lastBuild/console

# View SonarQube results
http://localhost:9000/projects

# Monitor deployment
kubectl get deployment -n aceest-production -w

# Trigger Jenkins build (via webhook)
git push origin main

# Check build status
curl http://localhost:8080/job/aceest-fitness-api/lastBuild/api/json | jq '.result'
```

---

## 📝 PHASE 6 EXECUTION SUMMARY

**What Was Done:**
- ✅ Added K8s deployment stage (Stage 12)
- ✅ Added K8s smoke tests stage (Stage 13)
- ✅ Added deployment strategies reference (Stage 14)
- ✅ Enhanced post-success section

**What You Need to Do:**
1. Follow execution steps above
2. Commit code to trigger Jenkins
3. Monitor pipeline execution
4. Verify all 14 stages pass
5. Validate K8s deployment
6. Move to Phase 7

**Expected Outcome:**
- ✅ Complete end-to-end CI/CD pipeline
- ✅ Automated K8s deployment
- ✅ 25+ passing K8s tests
- ✅ Production-ready infrastructure

---

**Phase 6 Status:** 🔄 Ready for Execution  
**Last Updated:** April 26, 2026  
**Estimated Completion Time:** 2-3 hours

Let's complete this phase! 🚀

