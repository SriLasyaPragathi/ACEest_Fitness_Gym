#!/bin/bash
# Canary Deployment Promotion Script
# Gradually promotes the canary deployment to stable

set -e

NAMESPACE="aceest-production"

echo "=========================================="
echo "Canary Deployment Promotion"
echo "=========================================="

# Check current replica counts
STABLE_REPLICAS=$(kubectl get deployment aceest-stable -n $NAMESPACE -o jsonpath='{.spec.replicas}')
CANARY_REPLICAS=$(kubectl get deployment aceest-canary -n $NAMESPACE -o jsonpath='{.spec.replicas}')

echo "Current state:"
echo "  Stable (v1.0.0): $STABLE_REPLICAS replicas"
echo "  Canary (v1.0.1): $CANARY_REPLICAS replicas"
echo ""

# Menu
echo "Promotion options:"
echo "1) Promote canary (increase to 2 replicas, 50/50 split)"
echo "2) Promote canary fully (scale stable to 0, canary to 3)"
echo "3) Rollback canary (scale canary to 0)"
echo ""
read -p "Select option (1-3): " OPTION

case $OPTION in
  1)
    echo ""
    echo "Scaling canary to 2 replicas (50/50 traffic split)..."
    kubectl scale deployment aceest-canary -n $NAMESPACE --replicas=2
    echo "✅ Canary scaled to 2 replicas"
    ;;
  2)
    echo ""
    echo "⚠️  Fully promoting canary (v1.0.1)..."
    echo "Scaling canary to 3 replicas..."
    kubectl scale deployment aceest-canary -n $NAMESPACE --replicas=3
    echo "Scaling stable to 0 replicas..."
    kubectl scale deployment aceest-stable -n $NAMESPACE --replicas=0
    echo "✅ Canary fully promoted! All traffic now to v1.0.1"
    ;;
  3)
    echo ""
    echo "Rolling back canary..."
    kubectl scale deployment aceest-canary -n $NAMESPACE --replicas=0
    kubectl scale deployment aceest-stable -n $NAMESPACE --replicas=3
    echo "✅ Canary rolled back. All traffic back to v1.0.0"
    ;;
  *)
    echo "Invalid option"
    exit 1
    ;;
esac

echo ""
echo "=========================================="
echo "Updated state:"
echo "=========================================="
kubectl get deployments -l deployment-strategy=canary -n $NAMESPACE
echo ""
echo "Pods:"
kubectl get pods -l app=aceest -n $NAMESPACE
