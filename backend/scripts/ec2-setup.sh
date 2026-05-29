#!/bin/bash
# scripts/ec2-setup.sh
# Run ONCE on a fresh Ubuntu 22.04 t3.micro instance.
# Usage: bash ec2-setup.sh
set -euo pipefail

echo "=== [1/6] Updating system packages ==="
sudo apt-get update && sudo apt-get upgrade -y

echo "=== [2/6] Installing Docker ==="
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker ubuntu
# Note: newgrp only affects this shell — log out and back in (or use 'sg docker')
# for the docker group to take effect without sudo.

echo "=== [3/6] Installing Docker Compose plugin ==="
sudo apt-get install -y docker-compose-plugin

echo "=== [4/6] Installing Nginx, Certbot, and AWS CLI ==="
sudo apt-get install -y nginx certbot python3-certbot-nginx awscli

echo "=== [5/6] Configuring Docker log rotation ==="
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
sudo systemctl restart docker

echo "=== [6/6] Creating application directory ==="
mkdir -p /home/ubuntu/studyroom
sudo chown ubuntu:ubuntu /home/ubuntu/studyroom

echo ""
echo "✅ EC2 base setup complete."
echo ""
echo "Next steps:"
echo "  1. Copy backend/docker-compose.yml to /home/ubuntu/studyroom/"
echo "  2. Create /home/ubuntu/studyroom/.env from .env.example and fill all values"
echo "  3. Configure DNS: api.yourdomain.com → this EC2 Elastic IP (wait for propagation)"
echo "  4. Copy nginx/studyroom.conf → /etc/nginx/sites-available/studyroom"
echo "     Replace 'api.yourdomain.com' with your actual domain in the file"
echo "  5. sudo ln -s /etc/nginx/sites-available/studyroom /etc/nginx/sites-enabled/"
echo "  6. sudo certbot --nginx -d api.yourdomain.com"
echo "  7. sudo nginx -t && sudo systemctl reload nginx"
echo "  8. cd /home/ubuntu/studyroom && docker compose up -d"
echo "  9. curl https://api.yourdomain.com/health"
