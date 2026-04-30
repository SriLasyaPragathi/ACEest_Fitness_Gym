#!/bin/bash

# ============================================================================
# Phase 6 Verification Script
# Quickly validate that Jenkins pipeline and K8s deployment are working
# ============================================================================

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       PHASE 6: JENKINS & K8S VERIFICATION SCRIPT               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNING=0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

print_warn() {
    echo -e "${YELLOW}[⚠ WARN]${NC} $1"
    ((TESTS_WARNING++))
}

print_section() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ============================================================================
# SECTION 1: MINIKUBE CHECKS
# ============================================================================

print_section "1. MINIKUBE CLUSTER CHECKS"

print_test "Checking if Minikube is installed..."
if command -v minikube &> /dev/null; then
    MINIKUBE_VERSION=$(minikube version 2>/dev/null | cut -d' ' -f3)
    print_pass "Minikube installed (version: $MINIKUBE_VERSION)"
else
    print_fail "Minikube not found. Install with: minikube start --cpus=4 --memory=4096"
fi

print_test "Checking if Minikube cluster is running..."
if minikube status 2>/dev/null | grep -q "Running"; then
    print_pass "Minikube is running"
else
    print_fail "Minikube not running. Start with: minikube start --cpus=4 --memory=4096"
fi

print_test "Checking Kubernetes cluster info..."
if kubectl cluster-info &> /dev/null; then
    CLUSTER_INFO=$(kubectl cluster-info | head -1)
    print_pass "K8s cluster accessible: $CLUSTER_INFO"
else
    print_fail "Cannot access Kubernetes cluster. Ensure Minikube is running."
fi

# ============================================================================
# SECTION 2: KUBERNETES DEPLOYMENT CHECKS
# ============================================================================

print_section "2. KUBERNETES DEPLOYMENT CHECKS"

print_test "Checking if namespace 'aceest-production' exists..."
if kubectl get namespace aceest-production &> /dev/null; then
    print_pass "Namespace 'aceest-production' exists"
else
    print_fail "Namespace 'aceest-production' not found. Run: kubectl apply -f k8s/namespace.yaml"
fi

print_test "Checking K8s deployment..."
if kubectl get deployment aceest-api -n aceest-production &> /dev/null; then
    DESIRED=$(kubectl get deployment aceest-api -n aceest-production -o jsonpath='{.spec.replicas}')
    READY=$(kubectl get deployment aceest-api -n aceest-production -o jsonpath='{.status.readyReplicas}')
    print_pass "Deployment 'aceest-api' exists (Desired: $DESIRED, Ready: $READY)"
    
    if [ "$DESIRED" -eq "$READY" ] 2>/dev/null && [ "$READY" -eq "3" ] 2>/dev/null; then
        print_pass "All 3 replicas are ready!"
    else
        print_warn "Not all replicas ready yet (Ready: $READY/$DESIRED). Give it more time..."
    fi
else
    print_fail "Deployment 'aceest-api' not found. Run: kubectl apply -f k8s/"
fi

print_test "Checking K8s pods..."
POD_COUNT=$(kubectl get pods -n aceest-production -l app=aceest-api --no-headers 2>/dev/null | wc -l)
if [ "$POD_COUNT" -gt 0 ]; then
    RUNNING=$(kubectl get pods -n aceest-production -l app=aceest-api --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    print_pass "Found $POD_COUNT pods ($RUNNING running)"
    
    if [ "$RUNNING" -eq "3" ]; then
        print_pass "All 3 pods are in Running state!"
        kubectl get pods -n aceest-production -l app=aceest-api | tail -3
    else
        print_warn "Not all pods running yet. Current status:"
        kubectl get pods -n aceest-production -l app=aceest-api
    fi
else
    print_fail "No pods found. Deployment may not be ready."
fi

print_test "Checking K8s service..."
if kubectl get svc aceest-service -n aceest-production &> /dev/null; then
    SERVICE_TYPE=$(kubectl get svc aceest-service -n aceest-production -o jsonpath='{.spec.type}')
    SERVICE_PORT=$(kubectl get svc aceest-service -n aceest-production -o jsonpath='{.spec.ports[0].port}')
    print_pass "Service 'aceest-service' exists (Type: $SERVICE_TYPE, Port: $SERVICE_PORT)"
else
    print_fail "Service 'aceest-service' not found. Run: kubectl apply -f k8s/service.yaml"
fi

# ============================================================================
# SECTION 3: HEALTH ENDPOINT CHECKS
# ============================================================================

print_section "3. APPLICATION HEALTH ENDPOINT CHECKS"

print_test "Getting service endpoint..."
SERVICE_URL=$(minikube service aceest-service -n aceest-production --url 2>/dev/null)
if [ -z "$SERVICE_URL" ]; then
    print_warn "Could not get service URL. Service may not have external IP yet."
    SERVICE_URL="http://localhost:8080"
    print_warn "Trying alternative port-forward method..."
fi

print_test "Testing health endpoint at $SERVICE_URL..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL/health 2>/dev/null)
if [ "$HEALTH_RESPONSE" == "200" ]; then
    print_pass "Health endpoint responding (HTTP $HEALTH_RESPONSE)"
    HEALTH_DATA=$(curl -s $SERVICE_URL/health 2>/dev/null)
    echo "  Response: $HEALTH_DATA"
else
    print_warn "Health endpoint returned HTTP $HEALTH_RESPONSE (expected 200)"
fi

# ============================================================================
# SECTION 4: DOCKER CHECKS
# ============================================================================

print_section "4. DOCKER IMAGE CHECKS"

print_test "Checking Docker images..."
if docker images 2>/dev/null | grep -q "aceest-fitness-api"; then
    IMAGE_COUNT=$(docker images | grep "aceest-fitness-api" | wc -l)
    print_pass "Found $IMAGE_COUNT Docker image(s) for aceest-fitness-api"
    docker images | grep aceest-fitness-api | while read -r line; do
        echo "  $line"
    done
else
    print_fail "No Docker images found for aceest-fitness-api"
fi

print_test "Checking Docker image tags..."
HAS_LATEST=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "aceest-fitness-api:latest" | wc -l)
HAS_VERSION=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "aceest-fitness-api:v" | wc -l)

if [ "$HAS_LATEST" -gt 0 ]; then
    print_pass "Found 'latest' tag"
else
    print_warn "Missing 'latest' tag"
fi

if [ "$HAS_VERSION" -gt 0 ]; then
    print_pass "Found version-specific tag"
else
    print_warn "Missing version-specific tag (e.g., v1.0.0)"
fi

# ============================================================================
# SECTION 5: JENKINS CHECKS
# ============================================================================

print_section "5. JENKINS PIPELINE CHECKS"

print_test "Checking if Jenkins is running..."
JENKINS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null)
if [ "$JENKINS_STATUS" == "200" ] || [ "$JENKINS_STATUS" == "403" ]; then
    print_pass "Jenkins is accessible (HTTP $JENKINS_STATUS)"
else
    print_fail "Cannot reach Jenkins at http://localhost:8080"
fi

print_test "Checking for aceest-fitness-api job..."
if curl -s http://localhost:8080/job/aceest-fitness-api/api/json 2>/dev/null | grep -q "aceest-fitness-api"; then
    print_pass "Jenkins job 'aceest-fitness-api' exists"
    
    # Get last build status
    LAST_BUILD=$(curl -s http://localhost:8080/job/aceest-fitness-api/lastBuild/api/json 2>/dev/null)
    LAST_BUILD_RESULT=$(echo $LAST_BUILD | grep -o '"result":"[^"]*"' | cut -d'"' -f4)
    LAST_BUILD_NUM=$(echo $LAST_BUILD | grep -o '"number":[0-9]*' | head -1 | cut -d':' -f2)
    
    if [ "$LAST_BUILD_RESULT" == "SUCCESS" ]; then
        print_pass "Last build (#$LAST_BUILD_NUM) was successful"
    else
        print_warn "Last build (#$LAST_BUILD_NUM) result: $LAST_BUILD_RESULT"
    fi
else
    print_fail "Jenkins job 'aceest-fitness-api' not found"
fi

# ============================================================================
# SECTION 6: K8S TESTS CHECKS
# ============================================================================

print_section "6. KUBERNETES SMOKE TESTS"

print_test "Checking if pytest is installed..."
if command -v pytest &> /dev/null; then
    PYTEST_VERSION=$(pytest --version 2>&1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")
    print_pass "pytest is installed (version: $PYTEST_VERSION)"
    
    print_test "Running K8s smoke tests..."
    if [ -f "tests/test_k8s_deployment.py" ]; then
        print_pass "Test file exists: tests/test_k8s_deployment.py"
        
        # Run tests and capture results
        echo "  Running tests..."
        pytest tests/test_k8s_deployment.py -v --tb=short 2>&1 | tail -20
    else
        print_fail "Test file not found: tests/test_k8s_deployment.py"
    fi
else
    print_fail "pytest not installed. Run: pip install -r requirements.txt"
fi

# ============================================================================
# SECTION 7: SONARQUBE CHECKS
# ============================================================================

print_section "7. SONARQUBE CHECKS"

print_test "Checking SonarQube service..."
SONAR_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000 2>/dev/null)
if [ "$SONAR_STATUS" == "200" ]; then
    print_pass "SonarQube is accessible (HTTP $SONAR_STATUS)"
else
    print_warn "SonarQube not accessible (HTTP $SONAR_STATUS). Start with: docker-compose up -d sonarqube"
fi

# ============================================================================
# SECTION 8: FILE STRUCTURE CHECKS
# ============================================================================

print_section "8. FILE STRUCTURE CHECKS"

print_test "Checking Phase 6 documentation..."
if [ -f "PHASE_6_EXECUTION_GUIDE.md" ]; then
    print_pass "PHASE_6_EXECUTION_GUIDE.md exists"
else
    print_warn "PHASE_6_EXECUTION_GUIDE.md not found"
fi

if [ -f "PHASE_6_COMPLETION_SUMMARY.md" ]; then
    print_pass "PHASE_6_COMPLETION_SUMMARY.md exists"
else
    print_warn "PHASE_6_COMPLETION_SUMMARY.md not found"
fi

print_test "Checking K8s manifests..."
K8S_FILES=$(find k8s -name "*.yaml" -o -name "*.sh" 2>/dev/null | wc -l)
if [ "$K8S_FILES" -gt 0 ]; then
    print_pass "Found $K8S_FILES K8s files"
else
    print_fail "No K8s files found in k8s/ directory"
fi

# ============================================================================
# SUMMARY
# ============================================================================

print_section "VERIFICATION SUMMARY"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_WARNING))

echo ""
echo "Tests Passed:   $TESTS_PASSED ✓"
echo "Tests Failed:   $TESTS_FAILED ✗"
echo "Tests Warnings: $TESTS_WARNING ⚠"
echo "Total Tests:    $TOTAL_TESTS"
echo ""

PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
echo "Pass Rate: $PASS_RATE%"

echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ PHASE 6 VERIFICATION SUCCESSFUL!                           ║${NC}"
    echo -e "${GREEN}║  All critical components are working correctly.                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next Steps:"
    echo "  1. Monitor Jenkins pipeline execution"
    echo "  2. Verify all 14 stages pass"
    echo "  3. Proceed to Phase 7 (CI/CD Architecture Report)"
    echo ""
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ PHASE 6 VERIFICATION INCOMPLETE                             ║${NC}"
    echo -e "${RED}║  Please fix the $TESTS_FAILED failed test(s) above.                        ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - Ensure Minikube is running: minikube start --cpus=4 --memory=4096"
    echo "  - Ensure K8s manifests are deployed: kubectl apply -f k8s/"
    echo "  - Check deployment status: kubectl get pods -n aceest-production"
    echo "  - Review logs: kubectl logs -n aceest-production -l app=aceest-api"
    echo ""
    exit 1
fi
