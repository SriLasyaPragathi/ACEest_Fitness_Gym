#!/bin/bash
# A/B Testing Deployment Script
# Deploys variant-a and variant-b for A/B testing

set -e

NAMESPACE="aceest-production"

echo "=========================================="
echo "A/B Testing Deployment - Full Deploy"
echo "=========================================="

# Create namespace if doesn't exist
echo "Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply base manifests
echo "Applying base manifests..."
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f storage.yaml

echo "Deploying Variant A (v1.0.0) and Variant B (v1.0.1)..."
kubectl apply -f deployments.yaml
kubectl apply -f service.yaml

# Optional: Apply ingress if NGINX ingress controller available
echo ""
read -p "Apply Ingress with header-based routing? (y/n): " APPLY_INGRESS
if [ "$APPLY_INGRESS" = "y" ] || [ "$APPLY_INGRESS" = "Y" ]; then
    echo "Applying ingress configuration..."
    kubectl apply -f ingress.yaml || echo "⚠️ Ingress configuration failed (NGINX controller may not be installed)"
fi

echo ""
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/aceest-variant-a -n $NAMESPACE --timeout=5m || true
kubectl rollout status deployment/aceest-variant-b -n $NAMESPACE --timeout=5m || true

echo ""
echo "=========================================="
echo "✅ A/B Testing deployment complete!"
echo "=========================================="
echo ""
echo "Deployment status (50/50 split):"
kubectl get deployments -l deployment-strategy=ab-testing -n $NAMESPACE
echo ""
echo "Pods status:"
kubectl get pods -l app=aceest -n $NAMESPACE
echo ""
echo "Service info:"
kubectl get svc aceest-ab-service -n $NAMESPACE
echo ""
echo "Variant-specific services:"
kubectl get svc | grep aceest-variant
echo ""
echo "Testing traffic routing:"
echo "  # Get service endpoint"
echo "  ENDPOINT=\$(kubectl get svc aceest-ab-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo ""
echo "  # Route to Variant A (default)"
echo "  curl http://\$ENDPOINT/health"
echo ""
echo "  # Route to Variant B (with header)"
echo "  curl -H 'X-AB-Test-Group: B' http://\$ENDPOINT/health"
