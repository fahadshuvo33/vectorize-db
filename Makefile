.PHONY: help dev up down clean check fix-net prepull logs

# Default target
help:
	@echo "VectorizeDB Management Commands"
	@echo "=========================="
	@echo "make dev       - Start all services (builds if needed)"
	@echo "make up        - Start services in background"
	@echo "make down      - Stop services"
	@echo "make clean     - Stop services and remove volumes (reset data)"
	@echo "make logs      - View logs"
	@echo "make check     - Check service health"
	@echo "make fix-net   - Fix Docker networking (Arch/CachyOS)"
	@echo "make prepull   - Pre-pull images for faster build"

dev:
	docker compose up --build

up:
	docker compose up -d --build

down:
	docker compose down

clean:
	docker compose down -v

logs:
	docker compose logs -f

check:
	@echo "🔍 Checking Services..."
	@docker compose ps
	@echo ""
	@echo "🔌 Connection Tests:"
	@if docker compose ps -q backend > /dev/null; then \
		echo -n "Backend: "; \
		docker exec $$(docker compose ps -q backend) curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ || echo "Failed"; \
		echo " (Expected: 200)"; \
	else \
		echo "Backend: Not running"; \
	fi
	@if docker compose ps -q frontend > /dev/null; then \
		echo -n "Frontend: "; \
		docker exec $$(docker compose ps -q frontend) curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 || echo "Failed"; \
		echo " (Expected: 200)"; \
	else \
		echo "Frontend: Not running"; \
	fi

fix-net:
	@echo "🔧 Fixing Docker Networking..."
	@sudo modprobe iptable_nat 2>/dev/null || echo "  ⚠️  iptable_nat module not available"
	@sudo modprobe ip6table_nat 2>/dev/null || echo "  ⚠️  ip6table_nat module not available"
	@sudo modprobe iptable_filter 2>/dev/null || echo "  ⚠️  iptable_filter module not available"
	@sudo systemctl restart docker
	@echo "✅ Docker restarted. Try 'make dev' now."

prepull:
	@echo "📦 Pulling base images..."
	docker pull python:3.14-slim
	docker pull node:25-alpine
	docker pull postgres:18-alpine
	docker pull redis:8-alpine
	@echo "✅ Done"
