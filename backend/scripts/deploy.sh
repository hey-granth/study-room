#!/bin/bash
# scripts/deploy.sh
# Manual deployment script — use when deploying without triggering GitHub Actions.
# Run this ON the EC2 instance: bash /home/ubuntu/studyroom/scripts/deploy.sh
set -euo pipefail

DEPLOY_DIR="/home/ubuntu/studyroom"
ECR_REGISTRY="<account_id>.dkr.ecr.us-east-1.amazonaws.com"
REGION="us-east-1"

echo "[deploy] Authenticating with ECR..."
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "$ECR_REGISTRY"

echo "[deploy] Pulling latest image..."
cd "$DEPLOY_DIR"
docker compose pull api

echo "[deploy] Restarting API container (zero-downtime)..."
docker compose up -d --no-deps api

echo "[deploy] Cleaning up dangling images..."
docker image prune -f

echo "[deploy] Done. Current container status:"
docker compose ps
