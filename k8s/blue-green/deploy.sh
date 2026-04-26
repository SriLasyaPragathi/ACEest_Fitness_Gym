#!/bin/bash
# Blue-Green Deployment Deploy Script
# Deploys both blue and green deployments

set -e

NAMESPACE="aceest-production"

echo "=========================================="
echo "Blue-Green Deployment - Full Deploy"
echo "=========================================="

# Create namespace if doesn't exist
echo "Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply manifests
echo "Applying deployment manifests..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f storage.yaml

echo "Deploying Blue (v1.0.0) and Green (v1.0.1)..."
kubectl apply -f deployments.yaml
kubectl apply -f service.yaml

echo ""
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/aceest-blue -n $NAMESPACE --timeout=5m || true
kubectl rollout status deployment/aceest-green -n $NAMESPACE --timeout=5m || true

echo ""
echo "=========================================="
echo "✅ Blue-Green deployment complete!"
echo "=========================================="
echo ""
echo "Deployment status:"
kubectl get deployments -n $NAMESPACE
echo ""
echo "Pods status:"
kubectl get pods -n $NAMESPACE
echo ""
echo "Service info:"
kubectl get svc aceest-blue-green-service -n $NAMESPACE
echo ""
echo "To switch between versions:"
echo "  ./switch.sh"
