# 🔧 Minikube Startup Fix

**Issue:** Existing Minikube cluster + API server failed to start  
**Solution:** Delete old cluster and restart fresh

---

## ✅ QUICK FIX (2 steps)

### Step 1: Delete Existing Minikube Cluster

```powershell
# Stop Minikube
minikube stop

# Delete the cluster
minikube delete

# Verify it's deleted
minikube status
# Expected: minikube cluster is not running.
```

### Step 2: Start Fresh Minikube Cluster

```powershell
# Start Minikube (this will create a new cluster)
minikube start --driver=docker

# Wait for it to fully start (1-2 minutes)
# You should see: ✅ Done! kubectl is now configured to use "minikube" cluster

# Verify cluster is running
minikube status
```

**Expected Output:**
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

---

## 🔍 If Still Having Issues

### Check Docker is Running
```powershell
docker ps
# Should show running containers

docker info
# Should show Docker daemon info
```

### Try Alternative: VirtualBox Driver

```powershell
# If Docker driver has issues, try VirtualBox
minikube delete
minikube start --driver=virtualbox

# Or use Hyper-V on Windows
minikube delete
minikube start --driver=hyperv
```

### Check System Resources

```powershell
# View Docker container resources
docker stats

# Ensure sufficient disk space
Get-Volume
```

---

## 🚀 Next Steps (After Minikube Starts)

Once `minikube status` shows all "Running":

```powershell
# 1. Configure Docker for Minikube
@(minikube docker-env) | Invoke-Expression
docker ps  # Verify Docker points to Minikube

# 2. Verify kubectl
kubectl cluster-info
kubectl get nodes

# 3. Continue with Phase 6 steps
```

---

## 📋 Full Step-by-Step Recovery

```powershell
# Step 1: Stop and clean up
Write-Host "Stopping Minikube..."
minikube stop
Start-Sleep -Seconds 3

Write-Host "Deleting old cluster..."
minikube delete
Start-Sleep -Seconds 3

Write-Host "Verifying deletion..."
minikube status

# Step 2: Start fresh
Write-Host "Starting Minikube with Docker driver..."
minikube start --driver=docker

# Step 3: Configure Docker environment
Write-Host "Configuring Docker environment..."
@(minikube docker-env) | Invoke-Expression

# Step 4: Verify everything
Write-Host "Verifying Minikube..."
minikube status

Write-Host "Verifying kubectl..."
kubectl cluster-info

Write-Host "Verifying Docker..."
docker ps

Write-Host "`n✅ Minikube is ready! Proceeding with Phase 6..."
```

---

## 💡 Common Causes & Fixes

| Issue | Fix |
|-------|-----|
| "Cannot change memory/CPUs" | Delete cluster first: `minikube delete` |
| "API server never appeared" | Ensure Docker daemon is running, restart Minikube |
| "Registry connection failed" | Network issue (usually non-blocking), cluster still works |
| "Storage provisioner error" | Can ignore, not needed for basic deployment |

---

## ✅ Success Indicators

After completing the fix:

✅ `minikube status` shows all "Running"  
✅ `kubectl cluster-info` shows cluster endpoint  
✅ `kubectl get nodes` shows 1 Ready node  
✅ `docker ps` shows minikube container  

---

**Ready to proceed with Phase 6!** 🚀
