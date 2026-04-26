#!/bin/bash
# Canary Deployment Deploy Script
# Deploys canary (stable + canary variant)

set -e

NAMESPACE="aceest-production"

echo "=========================================="
echo "Canary Deployment - Full Deploy"
echo "=========================================="

# Create namespace if doesn't exist
echo "Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply base manifests
echo "Applying base manifests..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f storage.yaml

echo "Deploying Stable (v1.0.0) and Canary (v1.0.1)..."
kubectl apply -f deployments.yaml
kubectl apply -f service.yaml

echo ""
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/aceest-stable -n $NAMESPACE --timeout=5m || true
kubectl rollout status deployment/aceest-canary -n $NAMESPACE --timeout=5m || true

echo ""
echo "=========================================="
echo "✅ Canary deployment complete!"
echo "=========================================="
echo ""
echo "Deployment status (67% stable, 33% canary):"
kubectl get deployments -l deployment-strategy=canary -n $NAMESPACE
echo ""
echo "Pods status:"
kubectl get pods -l app=aceest -n $NAMESPACE
echo ""
echo "Service info:"
kubectl get svc aceest-canary-service -n $NAMESPACE
echo ""
echo "To promote canary gradually:"
echo "  ./promote.sh"
