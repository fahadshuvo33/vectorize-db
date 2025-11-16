#!/bin/bash
# Script to check if all DBMelt services are running

echo "🔍 Checking DBMelt Services Status..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker Compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

echo "📦 Container Status:"
echo "-------------------"
docker compose ps

echo ""
echo "🌐 Service Ports:"
echo "-----------------"
echo -e "${YELLOW}Backend:${NC}    Port 8000  (FastAPI)"
echo -e "${YELLOW}Frontend:${NC}   Port 5173  (Vite)"
echo -e "${YELLOW}PostgreSQL:${NC} Port 5432  (Database)"
echo -e "${YELLOW}Redis:${NC}      Port 6379  (Cache)"
echo ""

# Check if containers are running
BACKEND=$(docker compose ps -q backend)
FRONTEND=$(docker compose ps -q frontend)
POSTGRES=$(docker compose ps -q postgres)
REDIS=$(docker compose ps -q redis)

echo "🔌 Connection Tests:"
echo "-------------------"

# Test Backend
if [ -n "$BACKEND" ]; then
    echo -n "Backend (8000): "
    if docker exec $BACKEND curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running${NC}"
        echo "   Health: $(docker exec $BACKEND curl -s http://localhost:8000/ | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
    else
        echo -e "${RED}❌ Not responding${NC}"
    fi
else
    echo -e "Backend (8000): ${RED}❌ Container not running${NC}"
fi

# Test Frontend
if [ -n "$FRONTEND" ]; then
    echo -n "Frontend (5173): "
    if docker exec $FRONTEND curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running${NC}"
    else
        echo -e "${YELLOW}⚠️  Container running but may not be accessible${NC}"
    fi
else
    echo -e "Frontend (5173): ${RED}❌ Container not running${NC}"
fi

# Test PostgreSQL
if [ -n "$POSTGRES" ]; then
    echo -n "PostgreSQL (5432): "
    if docker exec $POSTGRES pg_isready -U dbmelt -d dbmelt_db > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running${NC}"
    else
        echo -e "${RED}❌ Not responding${NC}"
    fi
else
    echo -e "PostgreSQL (5432): ${RED}❌ Container not running${NC}"
fi

# Test Redis
if [ -n "$REDIS" ]; then
    echo -n "Redis (6379): "
    if docker exec $REDIS redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running${NC}"
    else
        echo -e "${RED}❌ Not responding${NC}"
    fi
else
    echo -e "Redis (6379): ${RED}❌ Container not running${NC}"
fi

echo ""
echo "💡 Access Services:"
echo "------------------"
echo "If port mappings are enabled:"
echo "  - Frontend:  http://localhost:5173"
echo "  - Backend:    http://localhost:8000"
echo "  - API Docs:   http://localhost:8000/docs"
echo ""
echo "If port mappings are disabled:"
echo "  - Use: docker exec -it dbmelt-backend curl http://localhost:8000/"
echo "  - Or fix networking (see NETWORKING-FIX.md)"

