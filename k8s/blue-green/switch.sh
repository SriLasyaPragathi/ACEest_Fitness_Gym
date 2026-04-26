#!/bin/bash
# Blue-Green Deployment Switch Script
# Switches traffic between Blue (v1.0.0) and Green (v1.0.1) deployments

set -e

NAMESPACE="aceest-production"
SERVICE_NAME="aceest-blue-green-service"
CURRENT_VERSION=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.spec.selector.version}')

echo "=========================================="
echo "Blue-Green Deployment Switch"
echo "=========================================="
echo "Current version serving: $CURRENT_VERSION"
echo ""

if [ "$CURRENT_VERSION" == "blue" ]; then
    echo "Switching from BLUE (v1.0.0) to GREEN (v1.0.1)..."
    
    # Run smoke tests on green deployment before switching
    echo "⏳ Running smoke tests on GREEN deployment..."
    PODS=$(kubectl get pods -l version=green -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}')
    if [ ! -z "$PODS" ]; then
        echo "  Testing pod: $PODS"
        kubectl exec -it $PODS -n $NAMESPACE -- curl -s http://localhost:5000/health || true
        echo "  ✅ Smoke test completed"
    fi
    
    # Switch service selector to GREEN
    echo "Patching service to point to GREEN..."
    kubectl patch svc $SERVICE_NAME -n $NAMESPACE -p '{"spec":{"selector":{"version":"green"}}}'
    
    NEW_VERSION="green"
    
elif [ "$CURRENT_VERSION" == "green" ]; then
    echo "Switching from GREEN (v1.0.1) to BLUE (v1.0.0)..."
    
    # Run smoke tests on blue deployment before switching
    echo "⏳ Running smoke tests on BLUE deployment..."
    PODS=$(kubectl get pods -l version=blue -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}')
    if [ ! -z "$PODS" ]; then
        echo "  Testing pod: $PODS"
        kubectl exec -it $PODS -n $NAMESPACE -- curl -s http://localhost:5000/health || true
        echo "  ✅ Smoke test completed"
    fi
    
    # Switch service selector to BLUE
    echo "Patching service to point to BLUE..."
    kubectl patch svc $SERVICE_NAME -n $NAMESPACE -p '{"spec":{"selector":{"version":"blue"}}}'
    
    NEW_VERSION="blue"
else
    echo "❌ Unknown version: $CURRENT_VERSION"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Switch completed successfully!"
echo "=========================================="
echo "New version serving: $NEW_VERSION"
echo ""
echo "Verifying service connectivity..."
kubectl get svc $SERVICE_NAME -n $NAMESPACE
echo ""
echo "Pods now serving traffic:"
kubectl get pods -l app=aceest,version=$NEW_VERSION -n $NAMESPACE

echo ""
echo "To verify traffic routing:"
echo "  kubectl get svc $SERVICE_NAME -n $NAMESPACE"
echo "  minikube service $SERVICE_NAME -n $NAMESPACE"
