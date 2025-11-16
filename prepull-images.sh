#!/bin/bash
# Pre-pull base images to ensure they're cached

echo "Pre-pulling base Docker images for caching..."
echo ""

echo "📦 Pulling Python base image..."
docker pull python:3.14-slim

echo "📦 Pulling Node base image..."
docker pull node:25-alpine

echo "📦 Pulling PostgreSQL image..."
docker pull postgres:18-alpine

echo "📦 Pulling Redis image..."
docker pull redis:8-alpine

echo ""
echo "✅ Base images pre-pulled and cached!"
echo "   Subsequent builds will use these cached images."

