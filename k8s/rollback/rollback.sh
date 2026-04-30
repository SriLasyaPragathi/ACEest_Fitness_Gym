#!/bin/bash
# Automatic Rollback Mechanism
# Detects deployment failures and rolls back to last stable version

set -e

NAMESPACE="aceest-production"
DEPLOYMENT="aceest-api"
HEALTH_CHECK_RETRIES=5
HEALTH_CHECK_INTERVAL=10

echo "=========================================="
echo "🔄 Automatic Rollback Mechanism"
echo "=========================================="

# Get current deployment info
CURRENT_REVISION=$(kubectl rollout history deployment/$DEPLOYMENT -n $NAMESPACE | tail -2 | head -1 | awk '{print $1}')
PREVIOUS_REVISION=$((CURRENT_REVISION - 1))

echo "Current revision: $CURRENT_REVISION"
echo "Previous revision: $PREVIOUS_REVISION"

# Function to check deployment health
check_health() {
    local retries=$1
    local counter=0
    
    echo "Checking deployment health..."
    
    while [ $counter -lt $retries ]; do
        # Check if pods are ready
        READY_REPLICAS=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
        DESIRED_REPLICAS=$(kubectl get deployment $DEPLOYMENT -n $NAMESPACE -o jsonpath='{.spec.replicas}')
        
        echo "Ready replicas: $READY_REPLICAS/$DESIRED_REPLICAS"
        
        if [ "$READY_REPLICAS" = "$DESIRED_REPLICAS" ]; then
            echo "✅ All replicas are ready"
            
            # Check pod health
            FAILED_PODS=$(kubectl get pods -n $NAMESPACE -l app=$DEPLOYMENT -o jsonpath='{.items[?(@.status.phase!="Running")].metadata.name}' | wc -w)
            
            if [ $FAILED_PODS -eq 0 ]; then
                echo "✅ All pods are running"
                return 0
            else
                echo "❌ Found $FAILED_PODS failed pods"
                return 1
            fi
        fi
        
        counter=$((counter + 1))
        if [ $counter -lt $retries ]; then
            echo "Retrying in ${HEALTH_CHECK_INTERVAL}s..."
            sleep $HEALTH_CHECK_INTERVAL
        fi
    done
    
    return 1
}

# Function to check service endpoints
check_service_endpoints() {
    echo "Checking service endpoints..."
    ENDPOINTS=$(kubectl get endpoints aceest-service -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}' | wc -w)
    
    if [ $ENDPOINTS -gt 0 ]; then
        echo "✅ Service has $ENDPOINTS active endpoints"
        return 0
    else
        echo "❌ Service has no active endpoints"
        return 1
    fi
}

# Function to perform rollback
perform_rollback() {
    echo ""
    echo "⚠️  Deployment health check failed!"
    echo "Initiating automatic rollback to revision $PREVIOUS_REVISION..."
    
    kubectl rollout undo deployment/$DEPLOYMENT -n $NAMESPACE
    kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=5m
    
    echo "✅ Rollback completed"
    
    # Verify rollback
    if check_health 3; then
        echo "✅ Rollback successful - service restored"
        return 0
    else
        echo "❌ Rollback may have failed - manual intervention required"
        return 1
    fi
}

# Main health check sequence
echo ""
echo "Step 1: Verify rollout progress"
if ! kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=2m 2>/dev/null; then
    echo "⚠️  Deployment rollout did not complete in time"
fi

echo ""
echo "Step 2: Check deployment health"
if ! check_health $HEALTH_CHECK_RETRIES; then
    perform_rollback
    exit 1
fi

echo ""
echo "Step 3: Check service connectivity"
if ! check_service_endpoints; then
    perform_rollback
    exit 1
fi

echo ""
echo "Step 4: Verify pod logs for errors"
ERROR_COUNT=$(kubectl logs -n $NAMESPACE -l app=$DEPLOYMENT --tail=100 --all-containers=true 2>/dev/null | grep -c "ERROR\|CRITICAL" || echo "0")

if [ "$ERROR_COUNT" -gt 10 ]; then
    echo "⚠️  Found $ERROR_COUNT errors in recent logs"
    perform_rollback
    exit 1
fi

echo ""
echo "✅ Deployment health check passed!"
echo "No rollback needed - deployment is stable"
echo ""
echo "Current revision: $(kubectl rollout history deployment/$DEPLOYMENT -n $NAMESPACE | tail -1 | awk '{print $1}')"
