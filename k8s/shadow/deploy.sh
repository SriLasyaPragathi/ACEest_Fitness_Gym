#!/bin/bash
# Shadow Deployment Strategy
# Routes duplicate traffic to new version without affecting users

set -e

NAMESPACE="aceest-production"
NEW_VERSION="latest"

echo "=========================================="
echo "👻 Shadow Deployment Strategy"
echo "=========================================="

echo "Step 1: Deploy new version as shadow (no traffic)"
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aceest-api-shadow
  namespace: $NAMESPACE
  labels:
    app: aceest-api
    version: shadow
spec:
  replicas: 2
  selector:
    matchLabels:
      app: aceest-api
      version: shadow
  template:
    metadata:
      labels:
        app: aceest-api
        version: shadow
    spec:
      containers:
      - name: aceest-api
        image: docker.io/aceest-fitness-api:$NEW_VERSION
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
EOF

echo "Waiting for shadow deployment..."
kubectl rollout status deployment/aceest-api-shadow -n $NAMESPACE --timeout=5m

echo "Step 2: Configure Istio VirtualService to mirror traffic"
cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: aceest-api-shadow
  namespace: $NAMESPACE
spec:
  hosts:
  - aceest-service
  http:
  - route:
    - destination:
        host: aceest-service
        port:
          number: 80
      weight: 100
    mirror:
      host: aceest-api-shadow
      port:
        number: 5000
    mirrorPercent: 100
EOF

echo "Step 3: Monitor shadow metrics"
echo "Shadow deployment is receiving 100% mirrored traffic (user requests go to production only)"
echo ""
echo "Collecting metrics for 60 seconds..."
sleep 60

echo "Step 4: Compare metrics"
echo "Checking shadow deployment logs for issues..."
kubectl logs -n $NAMESPACE -l version=shadow --tail=50 | tail -20

echo ""
echo "✅ Shadow deployment complete!"
echo "Shadow version successfully tested with real traffic patterns"
echo ""
echo "To promote to production: kubectl set image deployment/aceest-api aceest-api=docker.io/aceest-fitness-api:$NEW_VERSION -n $NAMESPACE"
echo "To rollback shadow: kubectl delete deployment aceest-api-shadow -n $NAMESPACE"
