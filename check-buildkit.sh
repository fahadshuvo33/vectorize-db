#!/bin/bash
# Check if BuildKit is enabled and provide instructions

echo "Checking Docker BuildKit configuration..."

if [ "$DOCKER_BUILDKIT" = "1" ]; then
    echo "✅ DOCKER_BUILDKIT is enabled"
else
    echo "❌ DOCKER_BUILDKIT is not enabled"
    echo "   Run: export DOCKER_BUILDKIT=1"
fi

if [ "$COMPOSE_DOCKER_CLI_BUILD" = "1" ]; then
    echo "✅ COMPOSE_DOCKER_CLI_BUILD is enabled"
else
    echo "❌ COMPOSE_DOCKER_CLI_BUILD is not enabled"
    echo "   Run: export COMPOSE_DOCKER_CLI_BUILD=1"
fi

# Check Docker version
DOCKER_VERSION=$(docker version --format '{{.Server.Version}}' 2>/dev/null)
if [ -n "$DOCKER_VERSION" ]; then
    echo "📦 Docker version: $DOCKER_VERSION"
    MAJOR_VERSION=$(echo $DOCKER_VERSION | cut -d. -f1)
    MINOR_VERSION=$(echo $DOCKER_VERSION | cut -d. -f2)
    if [ "$MAJOR_VERSION" -ge 20 ] && [ "$MINOR_VERSION" -ge 10 ]; then
        echo "✅ Docker version supports BuildKit (20.10+)"
    else
        echo "⚠️  Docker version may not fully support BuildKit"
    fi
fi

echo ""
echo "To enable BuildKit permanently, add to ~/.bashrc or ~/.zshrc:"
echo "  export DOCKER_BUILDKIT=1"
echo "  export COMPOSE_DOCKER_CLI_BUILD=1"

