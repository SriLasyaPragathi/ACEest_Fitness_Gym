#!/bin/bash
# Universal Rollback Script
# Rollbacks to previous deployment version in K8s

set -e

NAMESPACE="aceest-production"

echo "=========================================="
echo "Universal Deployment Rollback"
echo "=========================================="
echo ""

# List available deployments
echo "Available deployments:"
kubectl get deployments -n $NAMESPACE -o custom-columns=NAME:.metadata.name,READY:.status.readyReplicas,REPLICAS:.spec.replicas

echo ""
read -p "Enter deployment name to rollback: " DEPLOYMENT_NAME

if [ -z "$DEPLOYMENT_NAME" ]; then
    echo "❌ Deployment name required"
    exit 1
fi

# Verify deployment exists
if ! kubectl get deployment $DEPLOYMENT_NAME -n $NAMESPACE &> /dev/null; then
    echo "❌ Deployment $DEPLOYMENT_NAME not found in namespace $NAMESPACE"
    exit 1
fi

echo ""
echo "Checking rollout history for $DEPLOYMENT_NAME..."
HISTORY=$(kubectl rollout history deployment/$DEPLOYMENT_NAME -n $NAMESPACE)
echo "$HISTORY"

echo ""
echo "Rolling back to previous revision..."
kubectl rollout undo deployment/$DEPLOYMENT_NAME -n $NAMESPACE

echo ""
echo "Waiting for rollback to complete..."
kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=5m

echo ""
echo "=========================================="
echo "✅ Rollback completed successfully!"
echo "=========================================="
echo ""
echo "Current revision:"
kubectl rollout history deployment/$DEPLOYMENT_NAME -n $NAMESPACE | tail -1
echo ""
echo "Pods status:"
kubectl get pods -l app=aceest -n $NAMESPACE
