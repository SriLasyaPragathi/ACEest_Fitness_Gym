#!/bin/bash
# Unified Deployment Strategy Orchestrator
# Routes deployment requests to appropriate strategy implementation

set -e

NAMESPACE="aceest-production"
STRATEGY="${1:-rolling}"  # Default to rolling update
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Deployment Strategy Orchestrator - ACEest Fitness API      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Show usage if requested
if [ "$STRATEGY" = "help" ] || [ "$STRATEGY" = "-h" ] || [ "$STRATEGY" = "--help" ]; then
    echo "Usage: ./deploy-strategy.sh [strategy] [options]"
    echo ""
    echo "Available Strategies:"
    echo "  rolling       - Standard rolling update (default)"
    echo "  blue-green    - Zero-downtime deployment with instant rollback"
    echo "  canary        - Gradual rollout with traffic shift"
    echo "  shadow        - Mirror production traffic to test new version"
    echo "  ab-test       - A/B test with traffic split"
    echo "  rollback      - Automatic rollback on failure detection"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy-strategy.sh blue-green"
    echo "  ./deploy-strategy.sh canary"
    echo "  ./deploy-strategy.sh shadow"
    echo ""
    exit 0
fi

# Validate Kubernetes connectivity
echo "Verifying Kubernetes connectivity..."
if ! kubectl cluster-info &>/dev/null; then
    echo "❌ Error: Cannot connect to Kubernetes cluster"
    exit 1
fi
echo "✅ Connected to cluster"

echo ""

# Route to appropriate strategy
case "$STRATEGY" in
    rolling)
        echo "📊 Deploying with Rolling Update strategy..."
        echo "Performing standard rolling update..."
        kubectl rollout restart deployment/aceest-api -n $NAMESPACE
        kubectl rollout status deployment/aceest-api -n $NAMESPACE --timeout=5m
        echo "✅ Rolling update complete"
        ;;
        
    blue-green)
        echo "🔵🟢 Deploying with Blue-Green strategy..."
        if [ ! -f "$SCRIPT_DIR/k8s/blue-green/deploy.sh" ]; then
            echo "❌ Blue-green deployment script not found"
            exit 1
        fi
        bash "$SCRIPT_DIR/k8s/blue-green/deploy.sh"
        ;;
        
    canary)
        echo "🐤 Deploying with Canary strategy..."
        if [ ! -f "$SCRIPT_DIR/k8s/canary/deploy.sh" ]; then
            echo "❌ Canary deployment script not found"
            exit 1
        fi
        bash "$SCRIPT_DIR/k8s/canary/deploy.sh"
        ;;
        
    shadow)
        echo "👻 Deploying with Shadow strategy..."
        if [ ! -f "$SCRIPT_DIR/k8s/shadow/deploy.sh" ]; then
            echo "❌ Shadow deployment script not found"
            exit 1
        fi
        bash "$SCRIPT_DIR/k8s/shadow/deploy.sh"
        ;;
        
    ab-test)
        echo "📊 Deploying with A/B Testing strategy..."
        if [ ! -f "$SCRIPT_DIR/k8s/a-b-testing/deploy.sh" ]; then
            echo "❌ A/B testing deployment script not found"
            exit 1
        fi
        bash "$SCRIPT_DIR/k8s/a-b-testing/deploy.sh"
        ;;
        
    rollback)
        echo "🔄 Running Automatic Rollback mechanism..."
        if [ ! -f "$SCRIPT_DIR/k8s/rollback/rollback.sh" ]; then
            echo "❌ Rollback script not found"
            exit 1
        fi
        bash "$SCRIPT_DIR/k8s/rollback/rollback.sh"
        ;;
        
    *)
        echo "❌ Unknown strategy: $STRATEGY"
        echo ""
        echo "Use './deploy-strategy.sh help' for available options"
        exit 1
        ;;
esac

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  Deployment Complete! ✅                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
