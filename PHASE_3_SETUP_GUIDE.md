# Phase 3 Setup Guide: Kubernetes Manifests & Minikube

## Overview
This guide covers setting up Minikube locally and deploying ACEest Fitness API using Kubernetes manifests created in this phase.

---

## Prerequisites

### System Requirements
- **OS:** Windows (with WSL2), macOS, or Linux
- **Memory:** 4GB minimum (8GB recommended)
- **CPU:** 4 cores minimum
- **Disk:** 10GB free space for Minikube VM + Docker images

### Required Tools
1. **Docker/Podman:** For building and managing containers
2. **Minikube:** Local Kubernetes cluster
3. **kubectl:** Kubernetes CLI tool
4. **Git:** Version control (already have)
5. **curl/wget:** For testing endpoints

---

## Step 1: Install Minikube

### Windows (with WSL2)

**Option A: Using Chocolatey**
```powershell
# Run PowerShell as Administrator
choco install minikube
choco install kubectl
```

**Option B: Manual Download**
```powershell
# Download Minikube installer
# Visit: https://minikube.sigs.k8s.io/docs/start/

# Or download directly:
Invoke-WebRequest -Uri "https://github.com/kubernetes/minikube/releases/download/v1.31.2/minikube-installer.exe" -OutFile "minikube-installer.exe"

# Run installer and follow prompts
.\minikube-installer.exe
```

**Option C: Using WSL2 with Linux Binary**
```bash
# In WSL2 terminal
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify
minikube version
```

### macOS
```bash
# Using Homebrew
brew install minikube
brew install kubectl

# Or download directly
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo install minikube-darwin-amd64 /usr/local/bin/minikube
```

### Linux
```bash
# Download and install
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
sudo apt-get install -y kubectl  # Debian/Ubuntu
# Or download: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
```

---

## Step 2: Start Minikube Cluster

```bash
# Start Minikube with appropriate resources
minikube start \
    --cpus=4 \
    --memory=4096 \
    --disk-size=20g \
    --driver=hyperv  # Use 'virtualbox' for VirtualBox, 'kvm2' for KVM on Linux

# Wait for startup (2-3 minutes)
# Output: "Done! kubectl is now configured to use "minikube" by default"

# Verify cluster is running
minikube status
# Expected: "host: Running, kubelet: Running, apiserver: Running"

# Check kubectl connectivity
kubectl cluster-info

# Get cluster version
kubectl version
```

**Note for Windows:**
- If using Hyper-V driver, ensure Hyper-V is enabled (System Admin required)
- Alternative: Use VirtualBox driver (`--driver=virtualbox`)

---

## Step 3: Configure Docker Registry Access

```bash
# Point Docker CLI to Minikube's Docker daemon
minikube docker-env

# On Windows PowerShell:
@(minikube docker-env) | Invoke-Expression

# On bash/WSL2:
eval $(minikube docker-env)

# Verify Docker is pointing to Minikube
docker ps
# Should show Docker ID of Minikube environment
```

---

## Step 4: Build and Push Docker Image to Minikube

```bash
# Build image in Minikube's Docker
cd p:\MTech_Devops\DevOps_Assignment

# Build with tags
docker build -t aceest-fitness-api:latest \
             -t aceest-fitness-api:v1.0.0 \
             -t aceest-fitness-api:v1.0.1 \
             .

# Verify images exist in Minikube
docker images | grep aceest

# Optional: Push to Docker Hub (if image is public)
# docker login
# docker push your-username/aceest-fitness-api:latest
```

---

## Step 5: Deploy Base Configuration

```bash
# Navigate to k8s directory
cd k8s

# Apply manifests in order:

# 1. Create namespace
kubectl apply -f namespace.yaml

# 2. Create ConfigMap
kubectl apply -f configmap.yaml

# 3. Create storage (PVC + StorageClass)
kubectl apply -f storage.yaml

# 4. Deploy base application
kubectl apply -f deployment-base.yaml

# 5. Create service
kubectl apply -f service.yaml

# Verify deployments
kubectl get deployments -n aceest-production
kubectl get pods -n aceest-production
kubectl get svc -n aceest-production

# Wait for pods to be running (may take 1-2 minutes)
kubectl rollout status deployment/aceest-api -n aceest-production --timeout=5m
```

---

## Step 6: Access Application

```bash
# Get service endpoint (Minikube LoadBalancer)
minikube service aceest-service -n aceest-production

# This opens browser automatically or shows URL
# Format: http://192.168.X.X:XXXXX

# Or manually get IP:
minikube ip
# e.g., 192.168.49.2

# Test health endpoint
curl http://192.168.49.2:80/health

# Test API endpoints
curl -X GET http://192.168.49.2/api/clients
```

---

## Step 7: Verify Deployment

```bash
# Check pods are running
kubectl get pods -n aceest-production

# Check logs of a pod
kubectl logs -f <pod-name> -n aceest-production

# Describe pod for detailed info
kubectl describe pod <pod-name> -n aceest-production

# Port-forward for local access (alternative to LoadBalancer)
kubectl port-forward svc/aceest-service 8080:80 -n aceest-production
# Then access: http://localhost:8080/health
```

---

## Step 8: Deploy Deployment Strategies

### Option A: Blue-Green Deployment

```bash
cd k8s/blue-green

# Deploy both blue and green versions
./deploy.sh  # Linux/macOS
# OR
bash deploy.sh  # Windows with Git Bash
# OR
cat deploy.sh | kubectl apply -f -  # Manual apply

# Switch between versions
./switch.sh
```

### Option B: Canary Deployment

```bash
cd k8s/canary

# Deploy stable + canary
./deploy.sh

# Promote canary gradually
./promote.sh
```

### Option C: A/B Testing

```bash
cd k8s/ab-testing

# Deploy variant-a and variant-b
./deploy.sh

# Test traffic routing
curl -H 'X-AB-Test-Group: A' http://<service-ip>/health
curl -H 'X-AB-Test-Group: B' http://<service-ip>/health
```

---

## Troubleshooting

### Issue: Minikube won't start
```bash
# Check logs
minikube logs

# Delete and restart
minikube delete
minikube start --cpus=4 --memory=4096

# Check if virtualization is enabled (Windows Hyper-V)
# Settings → Apps → Programs and Features → Turn Windows features on/off
# Check: Hyper-V, Containers
```

### Issue: Pods stuck in "Pending" state
```bash
# Check PVC status
kubectl get pvc -n aceest-production

# Check events
kubectl describe pvc <pvc-name> -n aceest-production

# Manual PV creation (if needed)
sudo mkdir -p /mnt/data/aceest
```

### Issue: Service not accessible
```bash
# Verify service exists
kubectl get svc -n aceest-production

# Get LoadBalancer IP
kubectl get svc aceest-service -n aceest-production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# If external IP is <pending>, use minikube service
minikube service aceest-service -n aceest-production --url
```

### Issue: Image not found in Minikube
```bash
# Ensure Docker is pointing to Minikube
eval $(minikube docker-env)

# Rebuild image
docker build -t aceest-fitness-api:latest .

# Verify image exists
docker images | grep aceest
```

---

## Useful Commands

```bash
# Cluster Management
minikube status                        # Check cluster status
minikube start                         # Start cluster
minikube stop                          # Stop cluster (saves state)
minikube delete                        # Delete cluster (clean slate)
minikube dashboard                     # Open Kubernetes dashboard in browser
minikube addons list                   # List available addons
minikube addons enable metrics-server  # Enable metrics for HPA

# Kubectl Commands
kubectl get nodes                                    # List nodes
kubectl get pods -n aceest-production              # List pods
kubectl get svc -n aceest-production               # List services
kubectl describe pod <pod-name> -n aceest-production  # Pod details
kubectl logs <pod-name> -n aceest-production       # View pod logs
kubectl logs -f <pod-name> -n aceest-production    # Follow logs
kubectl exec -it <pod-name> -n aceest-production -- /bin/bash  # Shell into pod
kubectl port-forward svc/aceest-service 8080:80 -n aceest-production  # Port forward

# Deployment Operations
kubectl apply -f deployment.yaml                   # Deploy
kubectl delete -f deployment.yaml                  # Undeploy
kubectl scale deployment aceest-api --replicas=5 -n aceest-production  # Scale
kubectl rollout status deployment/aceest-api -n aceest-production      # Check rollout
kubectl rollout history deployment/aceest-api -n aceest-production     # View history
kubectl rollout undo deployment/aceest-api -n aceest-production        # Rollback

# Debugging
kubectl get events -n aceest-production            # View cluster events
kubectl describe node minikube                     # Node details
minikube logs                                      # Minikube VM logs
```

---

## VERIFICATION CHECKLIST

- [ ] Minikube running (`minikube status` shows "Running")
- [ ] kubectl connected to Minikube (`kubectl cluster-info`)
- [ ] Docker pointing to Minikube (`docker ps` works)
- [ ] Docker image built (`docker images | grep aceest`)
- [ ] Namespace created (`kubectl get ns | grep aceest`)
- [ ] 3 Pods running (`kubectl get pods -n aceest-production`)
- [ ] Service accessible (`minikube service aceest-service -n aceest-production`)
- [ ] Health endpoint responds (`curl http://<ip>/health`)
- [ ] All deployment strategies deployed (Blue-Green, Canary, A/B)
- [ ] Rollback script working (`./rollback.sh`)

---

## NEXT STEPS

After Phase 3 verification:
1. Proceed to **Phase 4: Advanced Deployment Strategies** for detailed testing
2. Proceed to **Phase 5: K8s Smoke Tests** for automated validation
3. Proceed to **Phase 6: Jenkins Pipeline Enhancement** for CI/CD integration

---

## QUICK START SUMMARY

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=4096

# 2. Point Docker to Minikube
eval $(minikube docker-env)

# 3. Build image
cd p:\MTech_Devops\DevOps_Assignment
docker build -t aceest-fitness-api:latest .

# 4. Deploy
cd k8s
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f storage.yaml
kubectl apply -f deployment-base.yaml
kubectl apply -f service.yaml

# 5. Access
minikube service aceest-service -n aceest-production

# 6. Test
curl http://<ip>/health
```

---

**Status:** ✅ Phase 3 setup guide complete  
**Next:** Phase 4 - Advanced Deployment Strategies Testing
