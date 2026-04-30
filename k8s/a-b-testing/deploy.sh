#!/bin/bash
# A/B Testing Deployment Strategy
# Routes different user segments to different versions

set -e

NAMESPACE="aceest-production"
VERSION_A="v1.0.0"
VERSION_B="latest"

echo "=========================================="
echo "📊 A/B Testing Deployment Strategy"
echo "=========================================="

echo "Step 1: Ensure both versions are running"
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aceest-api-version-a
  namespace: $NAMESPACE
  labels:
    app: aceest-api
    version: version-a
spec:
  replicas: 2
  selector:
    matchLabels:
      app: aceest-api
      version: version-a
  template:
    metadata:
      labels:
        app: aceest-api
        version: version-a
    spec:
      containers:
      - name: aceest-api
        image: docker.io/aceest-fitness-api:$VERSION_A
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: EXPERIMENT_GROUP
          value: "A"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aceest-api-version-b
  namespace: $NAMESPACE
  labels:
    app: aceest-api
    version: version-b
spec:
  replicas: 2
  selector:
    matchLabels:
      app: aceest-api
      version: version-b
  template:
    metadata:
      labels:
        app: aceest-api
        version: version-b
    spec:
      containers:
      - name: aceest-api
        image: docker.io/aceest-fitness-api:$VERSION_B
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: EXPERIMENT_GROUP
          value: "B"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
EOF

echo "Waiting for both versions to be ready..."
kubectl rollout status deployment/aceest-api-version-a -n $NAMESPACE --timeout=5m
kubectl rollout status deployment/aceest-api-version-b -n $NAMESPACE --timeout=5m

echo "✅ Both versions deployed"

echo ""
echo "Step 2: Configure traffic routing (50/50 split)"
cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: aceest-api-ab-test
  namespace: $NAMESPACE
spec:
  hosts:
  - aceest-service
  http:
  - route:
    - destination:
        host: aceest-api-version-a
        port:
          number: 5000
      weight: 50
    - destination:
        host: aceest-api-version-b
        port:
          number: 5000
      weight: 50
EOF

echo "Traffic split: Version A (50%) | Version B (50%)"

echo ""
echo "Step 3: Monitor A/B test metrics"
echo "Collecting data for 120 seconds..."
sleep 120

echo ""
echo "Step 4: Analyze results"
echo "Version A requests:"
kubectl logs -n $NAMESPACE -l version=version-a --since=2m | grep -c "GET\|POST" || echo "0"

echo "Version B requests:"
kubectl logs -n $NAMESPACE -l version=version-b --since=2m | grep -c "GET\|POST" || echo "0"

echo ""
echo "✅ A/B test complete!"
echo ""
echo "Recommendation: Review metrics and choose winning version"
echo "To promote Version A: kubectl patch service aceest-service -n $NAMESPACE -p '{\"spec\":{\"selector\":{\"version\":\"version-a\"}}}'"
echo "To promote Version B: kubectl patch service aceest-service -n $NAMESPACE -p '{\"spec\":{\"selector\":{\"version\":\"version-b\"}}}'"
