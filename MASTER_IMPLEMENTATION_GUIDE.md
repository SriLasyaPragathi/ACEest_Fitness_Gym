# Assignment-2 Master Implementation & Execution Guide

**Quick Reference for Completing ACEest Fitness & Gym DevOps CI/CD Pipeline**

---

## 🎯 QUICK START SUMMARY

| Phase | Objective | Duration | Status |
|-------|-----------|----------|--------|
| 1 | SonarQube Setup | 2 hrs | ✅ COMPLETE |
| 2 | Docker Hub Integration | 1.5 hrs | ✅ COMPLETE |
| 3 | K8s Manifests & Minikube | 2 hrs | ✅ COMPLETE |
| 4 | Deployment Strategies | 2 hrs | ✅ COMPLETE |
| 5 | K8s Smoke Tests | 1.5 hrs | ✅ COMPLETE |
| 6 | Jenkins Pipeline Enhancement | 2 hrs | 🔄 IN-PROGRESS |
| 7 | CI/CD Report | 2 hrs | ⏳ PENDING |
| 8 | Final Validation | 1 hr | ⏳ PENDING |
| **TOTAL** | | **~14 hours** | **70% DONE** |

---

## 📁 PROJECT STRUCTURE

```
DevOps_Assignment/
├── app.py                              # Main Flask app (+ __version__)
├── requirements.txt                    # Dependencies (+ K8s client)
├── Dockerfile                          # Multi-stage container build
├── Jenkinsfile                         # CI/CD pipeline (11 stages)
├── docker-compose.yml                  # Services (+ SonarQube)
├── sonar-project.properties            # SonarQube config
│
├── tests/
│   ├── test_app.py
│   ├── test_auth.py
│   ├── test_database.py
│   ├── test_logic.py
│   └── test_k8s_deployment.py         # NEW: K8s smoke tests
│
├── k8s/                                # NEW: Kubernetes manifests
│   ├── namespace.yaml                  # Production namespace
│   ├── configmap.yaml                  # Environment config
│   ├── storage.yaml                    # PVC + StorageClass
│   ├── deployment-base.yaml            # Base 3-pod deployment
│   ├── service.yaml                    # LoadBalancer service
│   ├── rollback.sh                     # Rollback utility
│   │
│   ├── blue-green/                     # Blue-Green deployment
│   │   ├── deployments.yaml
│   │   ├── service.yaml
│   │   ├── switch.sh                   # Toggle blue↔green
│   │   └── deploy.sh
│   │
│   ├── canary/                         # Canary deployment
│   │   ├── deployments.yaml
│   │   ├── service.yaml
│   │   ├── promote.sh                  # Gradual promotion
│   │   └── deploy.sh
│   │
│   └── ab-testing/                     # A/B Testing deployment
│       ├── deployments.yaml
│       ├── service.yaml
│       ├── ingress.yaml                # Header-based routing
│       └── deploy.sh
│
├── PHASE_1_2_SETUP_GUIDE.md           # SonarQube + Docker Hub setup
├── PHASE_3_SETUP_GUIDE.md             # Minikube + K8s setup
├── IMPLEMENTATION_STATUS.md            # Phase-by-phase status
└── MASTER_IMPLEMENTATION_GUIDE.md      # This file
```

---

## 🚀 EXECUTION ROADMAP

### PHASE 1 & 2: CODE QUALITY & REGISTRY (Complete ✅)

**What was done:**
1. SonarQube Docker service configured
2. app.py versioning added (`__version__ = "1.0.0"`)
3. Jenkinsfile enhanced with SonarQube stage
4. Docker multi-tagging implemented
5. Credentials setup guide created

**To verify manually:**
```bash
# 1. Start SonarQube
cd p:\MTech_Devops\DevOps_Assignment
docker-compose up -d sonarqube
sleep 30
curl http://localhost:9000  # Should show SonarQube login page

# 2. Check version in app.py
grep "__version__" app.py    # Should show: __version__ = "1.0.0"

# 3. Check Jenkinsfile stages
grep -c "stage(" Jenkinsfile  # Should show: 11
```

---

### PHASE 3: KUBERNETES SETUP (Complete ✅)

**What was done:**
1. K8s directory structure created (18+ manifests)
2. Base deployment manifests (namespace, configmap, storage, deployment, service)
3. 4 deployment strategies implemented (Blue-Green, Canary, Rolling, A/B)
4. Minikube setup guide created

**To execute now:**
```bash
# Follow PHASE_3_SETUP_GUIDE.md exactly:

# 1. Install Minikube
# (Choose: Chocolatey, WSL2, or direct download)

# 2. Start Minikube
minikube start --cpus=4 --memory=4096 --disk-size=20g

# 3. Point Docker to Minikube
eval $(minikube docker-env)  # Linux/macOS
# OR (PowerShell on Windows):
@(minikube docker-env) | Invoke-Expression

# 4. Build Docker image
cd p:\MTech_Devops\DevOps_Assignment
docker build -t aceest-fitness-api:latest \
             -t aceest-fitness-api:v1.0.0 \
             -t aceest-fitness-api:v1.0.1 \
             .

# 5. Deploy base K8s
cd k8s
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f storage.yaml
kubectl apply -f deployment-base.yaml
kubectl apply -f service.yaml

# 6. Verify deployment
kubectl get pods -n aceest-production  # Should show 3 pods "Running"
kubectl get svc -n aceest-production   # Should show LoadBalancer

# 7. Access application
minikube service aceest-service -n aceest-production  # Opens browser

# 8. Test health endpoint
curl http://$(minikube ip)/health      # Should return 200 with JSON
```

---

### PHASE 4: DEPLOYMENT STRATEGIES (Complete ✅)

**What was done:**
1. Blue-Green deployment manifests (v1.0.0 ↔ v1.0.1 switch)
2. Canary deployment manifests (gradual rollout)
3. Rolling update configuration (built-in K8s)
4. A/B testing manifests (50/50 traffic split)
5. Rollback scripts for each strategy

**To test strategies:**
```bash
# TEST 1: Blue-Green
cd k8s/blue-green
./deploy.sh         # Deploy both blue & green
sleep 20
kubectl get pods -n aceest-production | grep blue  # Should see 6 pods (3 blue + 3 green)
curl $(minikube ip)/health    # Should work on blue version
./switch.sh         # Switch to green
curl $(minikube ip)/health    # Still works (now on green)

# TEST 2: Canary
cd k8s/canary
./deploy.sh         # Deploy stable (2 replicas) + canary (1 replica)
sleep 20
# 67% traffic → v1.0.0 (stable)
# 33% traffic → v1.0.1 (canary)
./promote.sh        # Interactive menu to promote gradually

# TEST 3: Rolling Update
# (Automatic when updating deployment image)
kubectl set image deployment/aceest-api \
  aceest-api=aceest-fitness-api:v1.0.1 \
  -n aceest-production
kubectl rollout status deployment/aceest-api -n aceest-production

# TEST 4: A/B Testing
cd k8s/ab-testing
./deploy.sh         # Deploy variant-a (50%) + variant-b (50%)
# Traffic split:
# Variant A: v1.0.0 (old UI)
# Variant B: v1.0.1 (new UI)
```

---

### PHASE 5: K8S SMOKE TESTS (Complete ✅)

**What was done:**
1. Comprehensive test suite (25+ tests)
2. Tests for deployment health, service, load balancing, persistence
3. Tests for rollback mechanisms

**To run tests:**
```bash
# 1. Install K8s dependencies
pip install -r requirements.txt

# 2. Ensure Minikube is running and kubectl configured
kubectl cluster-info

# 3. Run all K8s tests
pytest tests/test_k8s_deployment.py -v

# 4. Run specific test class
pytest tests/test_k8s_deployment.py::TestDeploymentHealth -v

# 5. Run with service connectivity
pytest tests/test_k8s_deployment.py -v -m requires_service

# Expected output:
# - 25+ tests
# - All pass ✅
# - Validates: deployment, pods, service, load balancing, persistence
```

---

### PHASE 6: JENKINS PIPELINE (In-Progress 🔄)

**What's done (75%):**
- ✅ SonarQube analysis stage added
- ✅ Docker multi-tagging implemented
- ✅ Environment variables for versioning
- ✅ Build metadata collection

**What still needs doing (25%):**
- ❌ Test Docker Hub push with actual credentials
- ❌ Add K8s deployment stage
- ❌ Add K8s smoke tests execution
- ❌ Add manual approval gates
- ❌ Test full pipeline end-to-end

**To complete Phase 6:**
```bash
# 1. Enable Docker Hub Push (in Jenkinsfile)
# Uncomment Docker Push stage with credentials:
withCredentials([usernamePassword(credentialsId: 'DOCKER_HUB_CREDENTIALS', ...)]) {
    sh '''
        echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin
        docker push ${DOCKER_IMAGE}
        docker push ${DOCKER_IMAGE_LATEST}
        docker push ${DOCKER_VERSION_TAG}
    '''
}

# 2. Add K8s deployment stage
stage('Deploy to Minikube') {
    when { branch 'main' }
    steps {
        sh '''
            kubectl apply -f k8s/
            kubectl rollout status deployment/aceest-api -n aceest-production --timeout=5m
        '''
    }
}

# 3. Add K8s smoke tests stage
stage('K8s Smoke Tests') {
    steps {
        sh '''
            pytest tests/test_k8s_deployment.py -v
        '''
    }
}

# 4. Test pipeline
# Commit code to main branch → Jenkins auto-triggers
# Watch console: All 11 stages should pass ✅
```

---

### PHASE 7: CI/CD ARCHITECTURE REPORT (Pending ⏳)

**To create report (2-3 pages):**

Create file: `CI_CD_ARCHITECTURE_REPORT.md`

**Contents:**
1. **Executive Summary** (0.5 pg)
   - Pipeline overview
   - Key tools & technologies
   - Business value

2. **Architecture Diagram** (0.5 pg)
   - Git → Jenkins → Docker Hub → Minikube flow
   - ASCII art or link to diagram tool

3. **CI/CD Pipeline Details** (0.75 pg)
   - Stage breakdown with timings
   - Trigger mechanisms
   - Artifact flow
   - Example pipeline run

4. **Deployment Strategies** (1 pg)
   - Blue-Green process + rollback procedure
   - Canary rollout steps
   - Rolling update configuration
   - A/B testing traffic distribution
   - Zero-downtime verification

5. **Code Quality & Testing** (0.5 pg)
   - SonarQube metrics
   - Test coverage (80%+)
   - Security scan results
   - Quality gates

6. **Challenges & Solutions** (0.5 pg)
   - Database persistence → Solution: PVC
   - Health checks timing → Solution: initialDelaySeconds
   - Rate limiting → Solution: credentials
   - K8s context switching → Solution: minikube cli

7. **Rollback & Recovery** (0.25 pg)
   - Automatic rollback on failure
   - Manual rollback procedures
   - Data recovery strategies

8. **Future Improvements** (0.25 pg)
   - Helm charts for templating
   - Prometheus/Grafana monitoring
   - ArgoCD for GitOps

---

### PHASE 8: FINAL VALIDATION & SUBMISSION (Pending ⏳)

**Submission Checklist:**

```bash
# 1. GitHub Repository
☐ Repository public or instructor invited
☐ All K8s manifests committed
☐ Updated Jenkinsfile committed
☐ Comprehensive tests committed
☐ All documentation files committed
☐ README has clear setup instructions
☐ Git log shows meaningful commit history

# 2. Docker Hub
☐ Public repository created
☐ 3+ image versions pushed (latest, v1.0.0, v1.0.1)
☐ Repository link accessible
☐ Image pull works: docker pull username/aceest-fitness-api:latest

# 3. Minikube Cluster
☐ Running: minikube status → "Running"
☐ 3 pods healthy: kubectl get pods -n aceest-production
☐ Service accessible: minikube service aceest-service
☐ Health endpoint responds: curl http://<ip>/health
☐ Record cluster IP for submission

# 4. Jenkins Pipeline
☐ Build triggered via webhook
☐ All 11 stages pass ✅
☐ Build logs show SonarQube analysis
☐ Images tagged with versions
☐ Console output archived
☐ Recent successful builds visible

# 5. SonarQube
☐ Dashboard accessible: http://localhost:9000
☐ Project analysis complete
☐ Quality metrics visible
☐ Report can be exported/screenshotted

# 6. Documentation
☐ PHASE_1_2_SETUP_GUIDE.md complete
☐ PHASE_3_SETUP_GUIDE.md complete
☐ CI_CD_ARCHITECTURE_REPORT.md (2-3 pages) complete
☐ IMPLEMENTATION_STATUS.md (detailed status)
☐ README.md updated with K8s deployment instructions

# 7. Artifacts Ready
☐ Dockerfile (multi-stage, production-grade)
☐ K8s manifests (18+ files in k8s/ directory)
☐ Jenkinsfile (11 stages, all working)
☐ Test suite (25+ K8s tests, all passing)
☐ Setup guides (PHASE_1_2_3 step-by-step)
```

**Submission Package:**
```
Submit to instructor:
1. GitHub repository URL (public link)
2. Minikube cluster endpoint URL (running K8s cluster)
3. Docker Hub repository URL (versioned images)
4. Screenshot of Jenkins pipeline (successful build)
5. Screenshot of SonarQube dashboard (quality metrics)
6. 2-3 page CI/CD Architecture Report (PDF or MD)
7. Brief explanation of challenges & solutions
```

---

## 📚 DOCUMENTATION REFERENCE

| Document | Purpose | Location |
|----------|---------|----------|
| PHASE_1_2_SETUP_GUIDE.md | SonarQube + Docker Hub setup | Root directory |
| PHASE_3_SETUP_GUIDE.md | Minikube + K8s setup | Root directory |
| IMPLEMENTATION_STATUS.md | Detailed phase-by-phase status | Root directory |
| CI_CD_ARCHITECTURE_REPORT.md | 2-3 page technical report | Root directory (to create) |
| README.md | Quick start & overview | Root directory |
| k8s/*/README.md | Strategy-specific guides | Each K8s subdirectory |

---

## 🔑 KEY COMMANDS QUICK REFERENCE

```bash
# ===== MINIKUBE =====
minikube start --cpus=4 --memory=4096
minikube stop
minikube delete
minikube status
minikube ip
minikube dashboard
minikube service aceest-service -n aceest-production

# ===== KUBECTL =====
kubectl cluster-info
kubectl get pods -n aceest-production
kubectl get svc -n aceest-production
kubectl logs <pod-name> -n aceest-production -f
kubectl describe pod <pod-name> -n aceest-production
kubectl exec -it <pod-name> -n aceest-production -- /bin/bash
kubectl port-forward svc/aceest-service 8080:80 -n aceest-production

# ===== DEPLOYMENT STRATEGIES =====
cd k8s/blue-green && ./deploy.sh && ./switch.sh
cd k8s/canary && ./deploy.sh && ./promote.sh
cd k8s/ab-testing && ./deploy.sh
./k8s/rollback.sh

# ===== DOCKER =====
eval $(minikube docker-env)
docker build -t aceest-fitness-api:latest -t aceest-fitness-api:v1.0.0 .
docker images | grep aceest
docker ps

# ===== PYTEST =====
pytest tests/ -v                                    # All tests
pytest tests/test_k8s_deployment.py -v             # K8s tests only
pytest tests/test_k8s_deployment.py::TestDeploymentHealth -v  # Specific class

# ===== JENKINS =====
# Trigger: Push to main branch → automatic webhook trigger
# Monitor: http://localhost:8080/job/aceest-fitness-api
# Logs: Click build → Console Output

# ===== SONARQUBE =====
docker-compose up -d sonarqube
curl http://localhost:9000
# Login: admin/admin
# Dashboard: http://localhost:9000/dashboard
```

---

## ✅ SUCCESS CRITERIA

**Assignment-2 is complete when:**

✅ **CI/CD Pipeline Operational**
- All 11 Jenkins stages execute successfully
- Build takes ~5-10 minutes start to finish
- Artifacts properly archived

✅ **Code Quality Enforced**
- SonarQube analysis shows project metrics
- Quality gates pass (code coverage, bugs, vulnerabilities)
- Report generated and accessible

✅ **Container Registry Setup**
- Docker Hub repository contains versioned images
- Images tagged: latest, v1.0.0, v1.0.1, build numbers
- Pull from Docker Hub works

✅ **Kubernetes Deployment**
- Minikube cluster running locally
- 3 pods deployed and healthy
- Service accessible via LoadBalancer
- Health endpoint responds (GET /health → 200)

✅ **Deployment Strategies Verified**
- Blue-Green switching works (instant rollover)
- Canary promotion works (gradual rollout)
- Rolling updates work (zero-downtime)
- A/B testing routes to both variants

✅ **Automated Testing**
- 25+ K8s smoke tests passing
- Tests validate deployment health
- Tests verify load balancing
- Tests confirm persistence

✅ **Documentation Complete**
- Setup guides for each phase
- 2-3 page CI/CD architecture report
- Challenges & solutions documented
- All files committed to GitHub

✅ **Ready for Submission**
- GitHub repo public & accessible
- Minikube endpoint running & responsive
- Docker Hub repository accessible
- Jenkins pipeline demonstrated
- SonarQube results captured

---

## 🎓 LEARNING OUTCOMES ACHIEVED

Upon completion, you will understand:

1. **DevOps Principles** — Automation, CI/CD, infrastructure as code
2. **CI/CD Tools** — Jenkins, GitHub webhooks, artifact management
3. **Code Quality** — SonarQube analysis, quality gates, coverage metrics
4. **Container Orchestration** — Kubernetes concepts, pods, services, deployments
5. **Deployment Strategies** — Blue-Green, Canary, Rolling, A/B Testing
6. **Zero-Downtime Deployments** — Graceful updates, health checks, rollback
7. **Infrastructure as Code** — Kubernetes YAML manifests, declarative configuration
8. **Automated Testing** — Integration testing, smoke tests, health verification
9. **Production Readiness** — Security, resource limits, persistence, monitoring
10. **DevOps Collaboration** — Git workflows, code reviews, automated feedback

---

## 🆘 TROUBLESHOOTING QUICK HELP

| Problem | Solution |
|---------|----------|
| Minikube won't start | `minikube delete` then `minikube start --cpus=4 --memory=4096` |
| Pods stuck "Pending" | Check PVC status: `kubectl describe pvc aceest-pvc -n aceest-production` |
| Service not accessible | Use port-forward: `kubectl port-forward svc/aceest-service 8080:80 -n aceest-production` |
| Docker image not found | Ensure Docker points to Minikube: `eval $(minikube docker-env)` |
| Jenkins can't reach SonarQube | Use `http://sonarqube:9000` inside Docker network |
| Kubectl can't connect | Check kubeconfig: `cat ~/.kube/config` or use Minikube context |
| Tests failing | Verify Minikube running and service accessible before running K8s tests |

---

## 📞 ADDITIONAL RESOURCES

- **Kubernetes Docs:** https://kubernetes.io/docs/
- **Minikube Guide:** https://minikube.sigs.k8s.io/docs/start/
- **SonarQube Setup:** https://docs.sonarqube.org/
- **Jenkins Declarative Pipeline:** https://jenkins.io/doc/book/pipeline/
- **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/

---

## 🎯 FINAL CHECKLIST

Before submitting, verify:

- [ ] All 8 phases documented & implemented
- [ ] GitHub repository public & complete
- [ ] Docker Hub repository with versioned images
- [ ] Minikube cluster running with app accessible
- [ ] Jenkins pipeline demonstrated (successful build)
- [ ] SonarQube analysis visible
- [ ] K8s smoke tests passing (25+)
- [ ] 2-3 page CI/CD report written
- [ ] All setup guides clear & tested
- [ ] README updated for new K8s features
- [ ] Challenges & solutions documented
- [ ] Endpoint URLs recorded for submission

---

**Status:** ✅ Phases 1-5 Complete | 🔄 Phase 6 In-Progress | ⏳ Phases 7-8 Ready to Start

**Estimated Time to Complete:** ~5-6 hours (Phase 6-8)

**Total Assignment Time:** ~14-16 hours

---

**Last Updated:** April 26, 2026  
**Version:** 1.0 - Master Implementation Guide
